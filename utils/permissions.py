from rest_framework import permissions
from utils.constants import AdminType


class ManagerOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.type == AdminType.SUPER_ADMIN or AdminType.ADMIN
        except AttributeError:
            return False


class UserSafePostOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
            return request.user.type == AdminType.SUPER_ADMIN
        except AttributeError:
            return False

        # if request.method == "POST":
        #     try:
        #         username = request.data.get("username")
        #         return True if username == request.session.get("user_id", None) else False
        #     except KeyError:
        #         return False


class UserAuthOnly(permissions.BasePermission):  # FIXME 无法获取正确的session
    def has_permission(self, request, view):
        user = request.user
        if not user:
            return False

            # 登录的用户必须是自定义管理员分组成员
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        try:
            if user.type == AdminType.ADMIN or AdminType.SUPER_ADMIN:
                return True
        except AttributeError:
            return False
        if user.username == obj.username:
            return True
        return False


class UserPUTOnly(permissions.BasePermission):  # FIXME 无法获取正确的session
    def has_permission(self, request, view):
        if request.method != "PUT":
            return False
        return request.session.get('user_id') is not None

    def has_object_permission(self, request, view, obj):
        if request.session.get('type', 1) == 3:
            return True
        user_id = request.session.get('user_id', default=None)
        print(user_id)
        if user_id == obj.username:
            return True
        else:
            return False


class AuthPUTOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method != "PATCH" and request.method != "PUT":
            return False
        if request.session.get('type', 1) == 3:
            return True
        else:
            return False

    def has_object_permission(self, request, view, blog):
        if request.method != "PATCH" and request.method != "PUT":
            return False
        if request.session.get('type', 1) == 3:
            return True
        else:
            return False


class ManagerPostOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
            return request.user.type == AdminType.SUPER_ADMIN or AdminType.ADMIN
        except AttributeError:
            return False
