# -*- coding: utf-8 -*-
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.throttling import ScopedRateThrottle
from .models import User, UserData, UserLoginData
from .serializers import UserSerializer, UserDataSerializer, UserNoPassSerializer, UserNoTypeSerializer, \
    UserLoginDataSerializer
from .permission import UserSafePostOnly, UserPUTOnly, AuthPUTOnly, ManagerOnly
from django.db.models import Q


class UserDataView(viewsets.ModelViewSet):
    # queryset = UserData.objects.extra(select={'_has': 'if(rating=1500,0,rating)'}).order_by('-_has')
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


class UserChangeView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDataSerializer
    permission_classes = (UserPUTOnly,)
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]


class UserChangeAllView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AuthPUTOnly,)
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]


class UserLoginDataView(viewsets.ModelViewSet):
    queryset = UserLoginData.objects.all().order_by('-id')
    serializer_class = UserLoginDataSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
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
        if data.get("ip"):
            if data["ip"].find("unknown") >= 0 and request.META.get('HTTP_X_FORWARDED_FOR'):
                data["ip"] = request.META.get("HTTP_X_FORWARDED_FOR")

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

        user_data = UserData.objects.get(username__exact=user.username)
        if user.password == password:
            serializer = UserSerializer(user)
            new_data = serializer.data
            request.session['user_id'] = user.username
            request.session['type'] = user.type
            request.session['rating'] = user_data.rating
            return Response(new_data, status=HTTP_200_OK)
        return Response('pwdError', HTTP_200_OK)


class UserUpdateRatingAPIView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]

    def get(self, request, format=None):
        if request.session.get('user_id', None) is not None:
            username = request.session.get('user_id', None)
            userdata = UserData.objects.get(username__exact=username)
            request.session['rating'] = userdata.rating
            return Response('updated', HTTP_200_OK)
        else:
            return Response('ok', HTTP_200_OK)


class UserLogoutAPIView(APIView):
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]

    def get(self, request):
        if request.session.get('user_id', None) is not None:
            del request.session['user_id']
        if request.session.get('type', None) is not None:
            del request.session['type']
        if request.session.get('rating', None) is not None:
            del request.session['rating']
        return Response('ok', HTTP_200_OK)


class UserRegisterAPIView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    throttle_scope = "register"
    throttle_classes = [ScopedRateThrottle]  # 控制api使用流量

    def post(self, request):
        data = request.data.copy()
        data['type'] = 1
        username = data.get('username')
        email = data.get('email')
        if User.objects.filter(username__exact=username):
            return Response("userError", HTTP_200_OK)
        if User.objects.filter(email__exact=email):
            return Response("emailError", HTTP_200_OK)

        user_serializer = UserSerializer(data=data)
        user_data_serializer = UserDataSerializer(data=data)
        # user_data_serializer.save()
        if user_serializer.is_valid(raise_exception=True) and user_data_serializer.is_valid():
            user_serializer.save()
            user_data_serializer.save()
            return Response(user_serializer.data, status=HTTP_200_OK)
        return Response(user_serializer.errors, status=HTTP_400_BAD_REQUEST)


