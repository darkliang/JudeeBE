from rest_framework import permissions

from utils.constants import AdminType


class ManagerPostOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        try:
            return request.user.type == AdminType.SUPER_ADMIN or AdminType.ADMIN
        except AttributeError:
            return False
