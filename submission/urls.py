from django.conf.urls import url, include
from rest_framework import routers
from submission import views


routers = routers.DefaultRouter()
routers.register("submit", views.SubmissionCreateView)
routers.register("submission", views.SubmissionGetView)
routers.register("contest-submission", views.ContestSubmissionGetView),
routers.register("manager-submission", views.ManagerSubmissionView)
urlpatterns = [
    url('', include(routers.urls)),
    url(r'^rejudge/$', views.SubmissionRejudgeAPI.as_view())
]