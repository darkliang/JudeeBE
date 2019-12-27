from rest_framework import serializers
from contest.models import Contest, OIContestRank, ACMContestRank, ContestAnnouncement
from user.serializers import UserSerializer
from utils.constants import RuleType


class ContestSerializer(serializers.ModelSerializer):
    is_pwd = serializers.BooleanField()
    is_in = serializers.SerializerMethodField()

    def get_is_in(self, obj):
        if obj.rule_type == RuleType.ACM:
            try:
                ACMContestRank.objects.get(user=self.context['request'].user, contest=obj)
            except (ACMContestRank.DoesNotExist, KeyError):
                return False
            return True
        elif obj.rule_type == RuleType.OI:
            try:
                OIContestRank.objects.get(user=self.context['request'].user, contest=obj)
            except (OIContestRank.DoesNotExist, KeyError):
                return False
            return True
        return False

    class Meta:
        model = Contest
        fields = '__all__'


class ContestListSerializer(ContestSerializer):
    class Meta:
        model = Contest
        exclude = ['description', 'allowed_ip_ranges', 'password', 'visible']


class ContestAdminSerializer(serializers.ModelSerializer):
    created_by = UserSerializer()
    status = serializers.CharField()
    contest_type = serializers.CharField()

    class Meta:
        model = Contest
        fields = "__all__"


class OIContestRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = OIContestRank
        exclude = ['contest', 'id']


class ACMContestRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = ACMContestRank
        exclude = ['contest', 'id']


class ContestAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContestAnnouncement
        fields = "__all__"
