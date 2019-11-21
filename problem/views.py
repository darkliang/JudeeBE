from rest_framework import viewsets, mixins
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from problem.models import Problem, ProblemTag
from problem.permission import ManagerPostOnly
from problem.serializers import ProblemSerializer, ProblemTagSerializer


class ProblemView(viewsets.GenericViewSet, mixins.DestroyModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin, mixins.ListModelMixin):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    # filter_fields = ('is_public',)
    permission_classes = (ManagerPostOnly,)
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]


class ProblemTagView(viewsets.ModelViewSet):
    queryset = ProblemTag.objects.all()
    serializer_class = ProblemTagSerializer
    permission_classes = (ManagerPostOnly,)
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]
