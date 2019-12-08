from rest_framework import serializers

from contest.models import Contest
from user.serializers import UserProfileSerializer


class ContestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = '__all__'


class ContestAdminSerializer(serializers.ModelSerializer):
    created_by = UserProfileSerializer()
    status = serializers.CharField()
    contest_type = serializers.CharField()

    class Meta:
        model = Contest
        fields = "__all__"
