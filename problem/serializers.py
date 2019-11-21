from rest_framework import serializers
from problem.models import Problem, ProblemTag


class ProblemTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemTag
        fields = '__all__'


class ProblemSerializer(serializers.ModelSerializer):
    tags = ProblemTagSerializer(many=True)

    class Meta:
        model = Problem
        fields = '__all__'
