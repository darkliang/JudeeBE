from rest_framework import serializers

from submission.models import Submission


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'


class SubmissionListSerializer(serializers.ModelSerializer):
    problem = serializers.SlugRelatedField(read_only=True, slug_field="ID")

    class Meta:
        model = Submission
        exclude = ("info", "contest", "code", "ip",)
