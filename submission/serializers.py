from rest_framework import serializers
from submission.models import Submission


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'


class SubmissionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        exclude = ("info", "code", "ip",)


class SubmissionSharingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('shared',)
