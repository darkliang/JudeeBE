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


class FPSProblemSerializer(serializers.Serializer):
    class CreateSampleSerializer(serializers.Serializer):
        input = serializers.CharField(trim_whitespace=False)
        output = serializers.CharField(trim_whitespace=False)

    class UnitSerializer(serializers.Serializer):
        unit = serializers.ChoiceField(choices=["MB", "s", "ms"])
        value = serializers.IntegerField(min_value=1, max_value=60000)

    title = serializers.CharField(max_length=128)
    description = serializers.CharField()
    input = serializers.CharField()
    output = serializers.CharField()
    hint = serializers.CharField(allow_blank=True, allow_null=True)
    time_limit = UnitSerializer()
    memory_limit = UnitSerializer()
    samples = serializers.ListField(child=CreateSampleSerializer())
    source = serializers.CharField(max_length=200, allow_blank=True, allow_null=True)
