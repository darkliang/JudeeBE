from rest_framework import serializers

from contest.models import Contest


class ContestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = '__all__'
