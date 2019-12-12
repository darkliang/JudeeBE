from rest_framework import permissions
from utils.constants import AdminType


class ManagerOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.type == (AdminType.SUPER_ADMIN or AdminType.ADMIN)
        except AttributeError:
            return False


class ManagerPostOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
            return request.user.type == (AdminType.SUPER_ADMIN or AdminType.ADMIN)
        except AttributeError:
            return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user or request.user.type == AdminType.SUPER_ADMIN


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
        return request.user is not None

    def has_object_permission(self, request, view, obj):
        user = request.user
        try:
            if user.type == (AdminType.ADMIN or AdminType.SUPER_ADMIN):
                return True
        except AttributeError:
            return False
        if user.username == obj.username:
            return True
        return False


class UserLoginOnly(permissions.BasePermission):  # FIXME 无法获取正确的session
    def has_permission(self, request, view):
        if request.method != "PUT" and request.method != "POST":
            return False
        return request.user is not None


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


'''
所有身份都有list权限，只有当前递交的创建者和管理员有retrieve权限
'''


class SubmissionCheck(permissions.BasePermission):

    def has_object_permission(self, request, view, submission):
        if hasattr(view, 'action') and view.action == 'retrieve':

            try:
                if request.user.type == (AdminType.ADMIN or AdminType.SUPER_ADMIN):
                    return True
            except AttributeError:
                return False

            if request.user == submission.username:
                return True
            else:
                return False
        elif hasattr(view, 'action') and view.action == 'list':
            return True
        return False
