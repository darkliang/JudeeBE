from rest_framework import serializers

from problem.models import ContestProblem
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


class ContestSubmissionSerializer(SubmissionSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return ContestProblem.objects.get(contest=obj.contest, problem=obj.problem).name


class ContestSubmissionListSerializer(SubmissionListSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        print(obj.contest, obj.problem)
        return ContestProblem.objects.get(contest=obj.contest, problem=obj.problem).name
