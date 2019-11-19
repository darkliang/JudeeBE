from django.conf.urls import url, include
from . import views
from rest_framework import routers

routers = routers.DefaultRouter()
routers.register('problem', views.ProblemView)

urlpatterns = [
    url('', include(routers.urls)),
    url(r'^upload_file', views.UploadFileAPIView.as_view()),
]
