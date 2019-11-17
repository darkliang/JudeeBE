# -*- coding: utf-8 -*-
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField


class User(models.Model):
    username = models.CharField(max_length=50, null=False, primary_key=True)
    password = models.CharField(max_length=50, null=False)
    nickname = models.CharField(max_length=50, null=False)  # 名称
    register_time = models.DateTimeField(auto_now=True)
    email = models.EmailField(max_length=50, null=False, default="")
    phone_number = PhoneNumberField(max_length=14, null=True)
    qq_number = models.CharField('QQ number', max_length=13, null=True)
    github_username = models.CharField(max_length=50, null=True)
    desc = models.CharField(max_length=50, null=True)
    type = models.IntegerField(null=False, default=1,
                               validators=[MaxValueValidator(3), MinValueValidator(1)])  # 1 普通 2 题目管理员 3 超级管理员

    # objects = models.Manager() 就是给 objects改个名 然而这里啥也没改

    def __str__(self):
        return self.username


class UserData(models.Model):
    username = models.CharField(max_length=50, null=False, primary_key=True)
    ac = models.IntegerField(null=False, default=0)
    submit = models.IntegerField(null=False, default=0)
    score = models.IntegerField(default=0)
    rating = models.IntegerField(default=1500)
    ac_prob = models.TextField(null=True, default="")  # 竖线分割
    # objects = models.Manager()

    def __str__(self):
        return self.username


class UserLoginData(models.Model):
    username = models.CharField(max_length=50, null=False)
    ip = models.GenericIPAddressField(unpack_ipv4=False, null=True)
    login_time = models.DateTimeField(auto_now=True)
    msg = models.TextField(null=True)  # 其他额外信息，如浏览器版本等

    # objects = models.Manager()

    def __str__(self):
        return self.username
