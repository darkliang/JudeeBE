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
