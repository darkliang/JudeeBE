# -*- coding: utf-8 -*-
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin, UserManager
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework.views import APIView

from utils.constants import AdminType


class User(AbstractBaseUser):
    username = models.CharField(max_length=50, null=False, primary_key=True)
    USERNAME_FIELD = 'username'
    password = models.CharField(max_length=100, null=False)
    nickname = models.CharField(max_length=50, null=True)  # 名称
    register_time = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(max_length=50, null=True, default="")
    phone_number = models.CharField('Phone number', max_length=15, null=True)
    qq_number = models.CharField('QQ number', max_length=13, null=True)
    github_username = models.CharField(max_length=50, null=True)
    desc = models.CharField(max_length=50, null=True)
    type = models.IntegerField(null=False, default=1,
                               validators=[MaxValueValidator(3), MinValueValidator(1)])  # 1 普通 2 题目管理员 3 超级管理员

    # objects = models.Manager() 就是给 objects改个名 然而这里啥也没改
    def is_contest_admin(self, contest):
        return contest.created_by == self or self.type == AdminType.SUPER_ADMIN

    def is_admin(self):
        return self.type == (AdminType.SUPER_ADMIN or AdminType.ADMIN)

    objects = UserManager()

    class Meta:
        ordering = ("-type",)

    def __str__(self):
        return self.username


class UserData(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    ac = models.IntegerField(null=False, default=0)
    submit = models.IntegerField(null=False, default=0)
    score = models.IntegerField(default=0)
    ranking = models.IntegerField(default=1500)
    ac_prob = models.TextField(null=True, default="")  # 竖线分割

    # objects = models.Manager()

    def __str__(self):
        return self.username


class UserLoginData(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField(unpack_ipv4=False, null=True)
    login_time = models.DateTimeField(auto_now=True)
    msg = models.TextField(null=True)  # 其他额外信息，如浏览器版本等

    # objects = models.Manager()

    def __str__(self):
        return self.username
