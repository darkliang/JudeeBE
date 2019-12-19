from rest_framework import serializers
from contest.models import Contest, OIContestRank, ACMContestRank, ContestAnnouncement
from user.serializers import UserProfileSerializer


class ContestSerializer(serializers.ModelSerializer):
    is_pwd = serializers.BooleanField()

    class Meta:
        model = Contest
        fields = '__all__'


class ContestListSerializer(serializers.ModelSerializer):
    is_pwd = serializers.BooleanField()

    class Meta:
        model = Contest
        exclude = ['description', 'allowed_ip_ranges', 'password', 'visible']


class ContestAdminSerializer(serializers.ModelSerializer):
    created_by = UserProfileSerializer()
    status = serializers.CharField()
    contest_type = serializers.CharField()

    class Meta:
        model = Contest
        fields = "__all__"


class OIContestRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = OIContestRank
        exclude = ['contest', ]


class ACMContestRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = ACMContestRank
        exclude = ['contest', ]


class ContestAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContestAnnouncement
        fields = "__all__"
