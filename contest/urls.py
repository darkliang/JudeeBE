from django.conf.urls import url, include
from rest_framework import routers

from contest import views

routers = routers.DefaultRouter()
routers.register('contest', views.ContestView)
routers.register('contest-announcement', views.ContestAnnouncementView)

urlpatterns = [
    url('', include(routers.urls)),
    url(r'^contest/([0-9]+)/add-problem/$', views.ContestAddProblemAPIView.as_view()),
    url(r'^contest/([0-9]+)/remove-problem/$', views.ContestDeleteProblemAPIView.as_view()),
    url(r'^contest/([0-9]+)/problems/$', views.ContestListProblemAPIView.as_view()),
    url(r'^contest/([0-9]+)/join-with-pwd/$', views.JoinContestWithPwd.as_view()),
    url(r'^contest-rank/', views.ContestRankView.as_view()),
]
