from django.conf.urls import url, include
from rest_framework import routers

from contest import views

routers = routers.DefaultRouter()
routers.register('contest', views.ContestView)
urlpatterns = [
    url('', include(routers.urls)),
    url(r'^contest/([0-9]+)/add-problem/$', views.ContestAddProblemAPIView.as_view()),
]