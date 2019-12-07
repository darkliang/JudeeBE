from django.conf.urls import url, include
from rest_framework import routers
from submission import views


routers = routers.DefaultRouter()
routers.register("submit", views.SubmissionCreateView)
urlpatterns = [
    url('', include(routers.urls)),
    url(r'^rejudge', views.SubmissionRejudgeAPI.as_view()),
]