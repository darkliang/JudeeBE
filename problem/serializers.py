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
        exclude = ['contest']


class ProblemListSerializer(serializers.ModelSerializer):
    tags = ProblemTagSerializer(many=True)

    class Meta:
        model = Problem
        exclude = ['contest', 'description', 'input_description', 'output_description', 'samples', 'test_case_score',
                   'hint', 'languages', 'template', 'time_limit', 'memory_limit', 'source', 'statistic_info']
