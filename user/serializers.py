# -*- coding: utf-8 -*-
from rest_framework import serializers
from utils.redis_util import RedisRank
from .models import User, UserData, UserLoginData


class UserLoginDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLoginData
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserNoPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']


class UserPwdSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=6)


class UserProfileSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(max_length=50, allow_blank=True, allow_null=True)  # 名称
    phone_number = serializers.CharField(max_length=15, allow_blank=True, allow_null=True)
    qq_number = serializers.CharField(max_length=13, allow_blank=True, allow_null=True)
    github_username = serializers.CharField(max_length=50, allow_blank=True, allow_null=True)
    desc = serializers.CharField(max_length=50, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        exclude = ['type', 'password', 'email', 'username', 'last_login']


class UserDataSerializer(serializers.ModelSerializer):
    ranking = serializers.SerializerMethodField()

    def get_ranking(self, obj):
        # print(obj.contest, obj.problem)
        return RedisRank.get_ranking(obj.username.username)

    class Meta:
        model = UserData
        fields = '__all__'


class RankUserDataSerializer(serializers.ModelSerializer):
    ac_prob_num = serializers.SerializerMethodField()
    ranking = serializers.SerializerMethodField()

    def get_ranking(self, obj):
        # print(obj.contest, obj.problem)
        return RedisRank.get_ranking(obj.username.username)

    def get_ac_prob_num(self, obj):
        # print(obj.contest, obj.problem)
        return obj.ac_prob.count('|')

    class Meta:
        model = UserData
        exclude = ['ac_prob']
