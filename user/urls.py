# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from . import views
from rest_framework import routers


routers = routers.DefaultRouter()
routers.register('userdata', views.UserDataView)
routers.register('user', views.UserView)
routers.register('change_profile', views.UserChangeView)
routers.register('change-all', views.UserChangeAllView)
routers.register('userlogindata', views.UserLoginDataView)
# routers.register('change_pwd', views.UserChangePwdAPIView)

urlpatterns = [
    url('', include(routers.urls)),
    url(r'^register', views.UserRegisterAPIView.as_view()),
    url(r'^login', views.UserLoginAPIView.as_view()),
    url(r'^admin-login', views.AdminLoginAPI.as_view()),
    url(r'^update-ranking', views.UserUpdateRankingAPIView.as_view()),
    url(r'^get-ranking', views.UserRankingAPIView.as_view()),
    url(r'^setlogindata', views.UserLoginDataAPIView.as_view()),
    url(r'^change_pwd', views.UserChangePwdAPIView.as_view()),
    url(r'^bulk-registration', views.UserBulkRegistration.as_view()),
    url(r'^statistics', views.UserStatisticsAPIVIEW.as_view())
]
