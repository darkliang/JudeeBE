# -*- coding: utf-8 -*-
import os
import re
import xlsxwriter
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.utils.datetime_safe import datetime
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, \
    HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from JudeeBE.settings import GENERATED_USER_DIR
from utils.constants import AdminType
from utils.redis_util import RedisRank
from utils.shortcuts import rand_str
from .models import User, UserData, UserLoginData
from .serializers import UserSerializer, UserDataSerializer, UserNoPassSerializer, UserProfileSerializer, \
    UserLoginDataSerializer
from utils.permissions import UserSafePostOnly, ManagerOnly, UserAuthOnly, SuperAdminRequired, UserLoginOnly
from django.db.models import Q


class UserDataView(viewsets.ModelViewSet):
    queryset = UserData.objects.all()
    serializer_class = UserDataSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('username',)
    permission_classes = (UserSafePostOnly,)
    pagination_class = LimitOffsetPagination
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]


class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserNoPassSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_fields = ('username',)
    search_fields = ('username', 'nickname')
    permission_classes = (UserSafePostOnly,)
    pagination_class = LimitOffsetPagination
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]


class UserChangeView(viewsets.GenericViewSet, mixins.UpdateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (UserAuthOnly,)
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]


# 管理员的功能
class UserChangeAllView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (ManagerOnly,)
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]


class UserChangePwdAPIView(APIView):
    queryset = User.objects.all()
    # serializer_class = UserPwdSerializer
    permission_classes = (UserAuthOnly,)
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]

    def put(self, request, format=None):
        data = request.data
        password = data.get('password', None)
        new_password = data.get('new_password', None)
        user = request.user
        if user.is_authenticated:
            if user.check_password(password):
                user.password = make_password(new_password)
                user.save()
                return Response('OK', status=HTTP_200_OK)
            return Response('pwdError', HTTP_200_OK)
        else:
            return Response('not authenticated', HTTP_401_UNAUTHORIZED)


class UserLoginDataView(viewsets.ModelViewSet):
    queryset = UserLoginData.objects.all().order_by('-id')
    serializer_class = UserLoginDataSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    # filter_fields做相等查询
    # search_fields做模糊查询
    filter_fields = ('username', 'ip',)
    search_fields = ('username', 'ip')
    permission_classes = (ManagerOnly,)
    pagination_class = LimitOffsetPagination
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]


class UserLoginDataAPIView(APIView):
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]

    def post(self, request, format=None):
        data = request.data.copy()

        data["ip"] = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
        serializer = UserLoginDataSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response('ok', status=HTTP_200_OK)


#   登录API
class UserLoginAPIView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    throttle_scope = "login"
    throttle_classes = [ScopedRateThrottle, ]

    def post(self, request, format=None):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        try:
            user = User.objects.get(Q(username__exact=username) | Q(email__exact=username))
        except User.DoesNotExist:
            return Response('userError', HTTP_200_OK)

        if user.check_password(password):
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            user.last_login = str(datetime.today())
            user.save()
            if user.type == AdminType.USER:
                user_data = UserData.objects.get(username__exact=user.username)
                new_data = {'token': token, 'username': user_data.username_id, 'ac_prob': user_data.ac_prob,
                            'nickname': user.nickname, 'type': user.type}
            else:
                new_data = {'token': token, 'username': user.username, 'type': user.type,
                            'nickname': user.nickname}
            return Response(new_data, status=HTTP_200_OK)
        return Response('pwdError', HTTP_200_OK)


class UserRegisterAPIView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    throttle_scope = "register"
    throttle_classes = [ScopedRateThrottle]  # 控制api使用流量

    def post(self, request):
        data = request.data.copy()
        data['type'] = AdminType.USER
        username = data.get('username')
        email = data.get('email')
        if User.objects.filter(username__exact=username):
            return Response("userError", HTTP_200_OK)
        if User.objects.filter(email__exact=email):
            return Response("emailError", HTTP_200_OK)
        data['password'] = make_password(data['password'])
        user_serializer = UserSerializer(data=data)
        # print(user_serializer.data)

        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.save()
            payload = jwt_payload_handler(user)
            res_dict = user_serializer.data
            res_dict["token"] = jwt_encode_handler(
                payload)  # jwt_encode_handler(payload) 生成 token；并赋值给 res_dict["token"]
            user_data_serializer = UserDataSerializer(data=data)
            user_data_serializer.is_valid()
            user_data_serializer.save()
            return Response(res_dict, status=HTTP_200_OK)
        return Response(user_serializer.errors, status=HTTP_400_BAD_REQUEST)


class UserBulkRegistration(APIView):
    permission_classes = SuperAdminRequired

    # serializer_classes = GenerateUserSerializer
    def get(self, request):
        """
        download users excel
        """
        file_id = request.GET.get("file_id")
        if not file_id:
            return Response("Invalid Parameter, file_id is required", HTTP_400_BAD_REQUEST)
        if not re.match(r"^[a-zA-Z0-9]+$", file_id):
            return Response("Illegal file_id", HTTP_400_BAD_REQUEST)

        file_path = os.path.join(GENERATED_USER_DIR, "{}.xlsx".format(file_id))

        if not os.path.isfile(file_path):
            return Response("File does not exist", HTTP_404_NOT_FOUND)
        with open(file_path, "rb") as f:
            raw_data = f.read()
        os.remove(file_path)
        response = HttpResponse(raw_data)
        response["Content-Disposition"] = "attachment; filename=users.xlsx"
        response["Content-Type"] = "application/xlsx"
        return response

    def post(self, request):
        """
                Generate User
                """
        data = request.data
        number_max_length = max(len(str(data["num_from"])), len(str(data["num_to"])))
        if number_max_length + len(data["prefix"]) + len(data["suffix"]) > 32:
            return Response("Username should not more than 32 characters", HTTP_400_BAD_REQUEST)
        if data["num_from"] > data["num_to"]:
            return Response("Start number must be lower than end number", HTTP_400_BAD_REQUEST)

        file_id = rand_str(8)
        filename = os.path.join(GENERATED_USER_DIR, "{}.xlsx".format(file_id))
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        worksheet.set_column("A:B", 20)
        worksheet.write("A1", "Username")
        worksheet.write("B1", "Password")

        user_list = []
        password_list = []
        for number in range(data["num_from"], data["num_from"] + 1):
            raw_password = rand_str(data.get("password_length", 8))
            user = User(username=f"{data.get('prefix', '')}{number}{data.get('suffix', '')}",
                        password=make_password(raw_password))
            user_list.append(user)
            password_list.append(raw_password)

        try:
            with transaction.atomic():
                ret = User.objects.bulk_create(user_list)
                UserData.objects.bulk_create([UserData(username=user) for user in ret])
                for idx, item in enumerate(user_list):
                    worksheet.write_string(idx + 1, 0, item.username)
                    worksheet.write_string(idx + 1, 1, password_list[idx])
                workbook.close()
            return Response({"file_id": file_id}, HTTP_200_OK)
        except IntegrityError as e:
            # Extract detail from exception message
            #    duplicate key value violates unique constraint "user_username_key"
            #    DETAIL:  Key (username)=(root11) already exists.
            return Response({"file_id": file_id}, HTTP_500_INTERNAL_SERVER_ERROR)


class UserRankingAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            limit = int(request.GET.get('limit', -1))
            offset = int(request.GET.get('offset', 0))
        except ValueError:
            return Response("Argument error", HTTP_400_BAD_REQUEST)
        get_res = RedisRank.get_top_n_users(limit, offset)
        res = []
        for user_data in get_res.values():
            userdata = UserDataSerializer(user_data)
            res.append(userdata.data)
        return Response({'count': len(res), 'results': res}, HTTP_200_OK)


class UserUpdateRankingAPIView(APIView):
    throttle_classes = [ScopedRateThrottle, ]

    def get(self, request, format=None):
        username = request.GET.get('username', None)
        if username:
            res = RedisRank.get_ranking(username)

        else:
            user_data = UserData.objects.get(username=request.user.username)
            res = RedisRank.record_score({user_data.username.username: user_data.score})
        # RedisRank.record_score(request.user.username)
        return Response(res, HTTP_200_OK)
