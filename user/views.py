# -*- coding: utf-8 -*-
from django.contrib.auth.hashers import make_password
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from utils.constants import AdminType
from .models import User, UserData, UserLoginData
from .serializers import UserSerializer, UserDataSerializer, UserNoPassSerializer, UserProfileSerializer, \
    UserLoginDataSerializer, UserPwdSerializer
from .permission import UserSafePostOnly, ManagerOnly, UserAuthOnly
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
    # permission_classes = (UserAuthOnly,)
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

    # FIXME anyone can change the password
    def put(self, request, format=None):
        data = request.data
        password = data.get('password', None)
        new_password = data.get('new_password', None)
        user = request.user

        if user.check_password(password):
            user.password = make_password(new_password)
            user.save()
            return Response('OK', status=HTTP_200_OK)
        return Response('pwdError', HTTP_200_OK)


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

        # user_data = UserData.objects.get(username__exact=user.username)
        if user.check_password(password):
            serializer = UserSerializer(user)
            new_data = serializer.data
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            new_data['token'] = token
            return Response(new_data, status=HTTP_200_OK)
        return Response('pwdError', HTTP_200_OK)


class UserUpdateRankingAPIView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]

    def get(self, request, format=None):
        if request.session.get('user_id', None) is not None:
            username = request.session.get('user_id', None)
            userdata = UserData.objects.get(username__exact=username)
            # request.session['ranking'] = userdata.ranking
            return Response('updated', HTTP_200_OK)
        else:
            return Response('ok', HTTP_200_OK)


# class UserLogoutAPIView(APIView):
#     throttle_scope = "post"
#     throttle_classes = [ScopedRateThrottle, ]
#
#     def get(self, request):
#         if request.session.get('user_id', None):
#             del request.session['user_id']
#         if request.session.get('type', None):
#             del request.session['type']
#         if request.session.get('ranking', None):
#             del request.session['ranking']
#         return Response('ok', HTTP_200_OK)


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
