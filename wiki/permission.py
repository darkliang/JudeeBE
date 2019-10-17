# coding=utf-8
from rest_framework import permissions
from board.models import SettingBoard

class WikiUserOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        setting = SettingBoard.objects.get(id=1)
        if setting.openwiki is False:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True

        data = request.data
        username = data.get('username')
        userid = request.session.get('user_id', None)
        if userid == username or request.session.get('type', 1) != 1:
            return True
        else:
            return False

    def has_object_permission(self, request, view, wiki):
        setting = SettingBoard.objects.get(id=1)
        if setting.openwiki is False:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        username = wiki.username
        userid = request.session.get('user_id', None)
        print(username, userid)
        if userid == username or request.session.get('type', 1) != 1:
            return True
        else:
            return False


class UserOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        setting = SettingBoard.objects.get(id=1)
        if setting.openwiki is False:
            return False
        if request.method in permissions.SAFE_METHODS or request.method == "DELETE":
            return True

        data = request.data
        username = data.get('username')
        userid = request.session.get('user_id', None)
        if userid == username or request.session.get('type', 1) != 1:
            return True
        else:
            return False

    def has_object_permission(self, request, view, blog):
        setting = SettingBoard.objects.get(id=1)
        if setting.openwiki is False:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        username = blog.username
        userid = request.session.get('user_id', None)
        if userid == username or request.session.get('type', 1) != 1:
            return True
        else:
            return False


class ManagerOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        setting = SettingBoard.objects.get(id=1)
        if setting.openwiki is False:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.session.get('type', 1) == 3:
            return True
        else:
            return False

    def has_object_permission(self, request, view, blog):
        setting = SettingBoard.objects.get(id=1)
        if setting.openwiki is False:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.session.get('type', 1) == 3:
            return True
        else:
            return False
