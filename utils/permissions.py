from rest_framework import permissions

from contest.models import ACMContestRank, OIContestRank
from utils.constants import AdminType, RuleType


class SuperAdminRequired(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.type == AdminType.SUPER_ADMIN
        except AttributeError:
            return False


class ManagerOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.type == (AdminType.SUPER_ADMIN or AdminType.ADMIN)
        except AttributeError:
            return False


# 只有对象的创建者或者超管才有权限修改对象 未登录也可以查看
class ManagerPostOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.auth and (obj.created_by == request.user or request.user.type == AdminType.SUPER_ADMIN)


'''
只有加入过竞赛的成员才能retrieve有密码的竞赛
'''


class ContestPwdRequired(permissions.BasePermission):
    def has_object_permission(self, request, view, contest):
        if request.auth and (request.user.type == AdminType.SUPER_ADMIN or request.user == contest.created_by):
            return True
        if hasattr(view, 'action') and view.action == 'retrieve':
            if not contest.password:
                return True
            if contest.rule_type == RuleType.ACM:
                return ACMContestRank.objects.filter(user=request.user, contest=contest).exists()
            elif contest.rule_type == RuleType.OI:
                return OIContestRank.objects.filter(user=request.user, contest=contest).exists()
        return True


class UserSafePostOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
            return request.user.type == AdminType.SUPER_ADMIN
        except AttributeError:
            return False


class UserAuthOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user is not None

    def has_object_permission(self, request, view, obj):
        user = request.user
        # print(user.username == obj.username)
        try:
            if user.type == (AdminType.ADMIN or AdminType.SUPER_ADMIN):
                return True
        except AttributeError:
            return False
        # print(user.username == obj.username)
        if user.username == obj.username or user == obj.username:
            return True
        return False


class UserLoginOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.auth


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
            if submission.shared:
                return True
            if request.user == submission.username:
                return True
            else:
                return False
        elif hasattr(view, 'action') and view.action == 'list':
            return True
        return False
