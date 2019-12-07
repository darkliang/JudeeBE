from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.throttling import ScopedRateThrottle

from contest.models import Contest
from contest.serializers import ContestSerializer
from utils.permissions import ManagerOnly


class ContestView(viewsets.ModelViewSet):
    queryset = Contest.objects.all()
    serializer_class = ContestSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (ManagerOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_fields = ("begintime", "level", "type", "title",)
    search_fields = ('title',)
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]