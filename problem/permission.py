# coding=utf-8
from rest_framework import permissions


class ManagerOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        type = request.session.get('type', 1)
        if type == 2 or type == 3:
            return True
        else:
            return False


class AuthOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        type = request.session.get('type', 1)
        if type == 2 or type == 3:
            return True
        else:
            return False

    def has_object_permission(self, request, view, problem):
        type = request.session.get('type', 1)
        if type == 2 or type == 3:
            return True
        return problem.auth == 1 or problem.auth == 3
