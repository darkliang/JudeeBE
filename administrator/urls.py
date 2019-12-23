from administrator import views
from django.conf.urls import url, include
from rest_framework import routers

routers = routers.DefaultRouter()

urlpatterns = [
    url('', include(routers.urls)),
    url(r'^overall/$', views.OverallAPI.as_view()),
    url(r'^admin-submission/$', views.SubmissionStatisticsAPI.as_view()),
    url(r'^admin-login-data/$', views.UserLoginStatisticsAPI.as_view()),
    url(r'^recent-submission/$', views.RecentSubmissionAPI.as_view()),
]
