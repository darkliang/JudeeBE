from django.conf.urls import url, include
from rest_framework import routers

from problem import views

routers = routers.DefaultRouter()
routers.register('problem', views.ProblemView)
routers.register('problem_tag', views.ProblemTagView)
urlpatterns = [
    url('', include(routers.urls)),
    url(r'^upload_file', views.TestCaseAPI.as_view()),
]
