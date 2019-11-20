from rest_framework import permissions

from utils.constants import AdminType


class ManagerPostOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.session.get('type', AdminType.USER) == AdminType.SUPER_ADMIN:
            return True

        return False
