import ipaddress
import os
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_204_NO_CONTENT, \
    HTTP_403_FORBIDDEN
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from JudeeBE.settings import TEST_CASE_DIR
from contest.models import Contest
from problem.models import Problem
from submission.models import Submission
from submission.serializers import SubmissionSerializer, SubmissionListSerializer
from utils.constants import ContestStatus
from utils.redis_util import RedisQueue
from utils.permissions import ManagerOnly, UserLoginOnly, SubmissionCheck


class ManagerSubmissionView(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    permission_classes = (ManagerOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('username', 'result', 'language', 'problem', 'contest')

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'list':
            return SubmissionListSerializer
        if hasattr(self, 'action') and self.action == 'retrieve':
            return SubmissionSerializer

    # 用于rejudge
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        RedisQueue.put('queue:submission', serializer.data.ID)

        return Response(status=HTTP_204_NO_CONTENT)


#
# class SubmissionRejudgeAPI(APIView):
#     permission_classes = (ManagerOnly,)
#
#     def get(self, request):
#         submission_id = request.GET.get("submission")
#         if not id:
#             return Response("Parameter error, id is required", status=HTTP_400_BAD_REQUEST)
#         try:
#             submission = Submission.objects.get(id=submission_id)
#         except Submission.DoesNotExist:
#             return Response("Submission does not exists", status=HTTP_404_NOT_FOUND)
#         submission.info = []
#         submission.compile_error_info = None
#         submission.time_cost = None
#         submission.memory_cost = None
#         submission.score = None
#         submission.save()
#
#         # SUBMISSION_QUEUE.produce(submission.ID)
#         RedisQueue.put('queue:submission', submission.ID)
#         return Response(status=HTTP_204_NO_CONTENT)


def check_contest_permission(submission_data):
    contest = submission_data["contest"]
    user = submission_data["username"]
    ip = submission_data["ip"]
    if contest.status == ContestStatus.CONTEST_ENDED:
        return "The contest have ended"
    if not user.is_contest_admin(contest):
        user_ip = ipaddress.ip_address(ip)
        if contest.allowed_ip_ranges:
            if not any(user_ip in ipaddress.ip_network(cidr, strict=False) for cidr in contest.allowed_ip_ranges):
                return "Your IP is not allowed in this contest"


class SubmissionCreateView(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = (UserLoginOnly,)
    throttle_scope = "judge"
    throttle_classes = [ScopedRateThrottle, ]

    def create(self, request, *args, **kwargs):
        data = dict(request.data)
        test_case_dir = os.path.join(TEST_CASE_DIR, str(data["problem"]))
        if not os.path.isfile(os.path.join(test_case_dir, '1.in')):
            return Response("No test cases", status=HTTP_400_BAD_REQUEST)
        data["username"] = request.user
        data["ip"] = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
        try:
            data["problem"] = Problem.objects.get(ID=data.get("problem"))
        except (ValueError, Problem.DoesNotExist):
            return Response("Wrong problem ID", status=HTTP_400_BAD_REQUEST)

        contest_id = data.get('contest', None)
        if contest_id:
            try:
                data["contest"] = Contest.objects.get(id=contest_id)
            except (ValueError, Problem.DoesNotExist):
                return Response("Wrong contest ID", status=HTTP_400_BAD_REQUEST)
            error = check_contest_permission(data)
            if error:
                return Response(error, status=HTTP_403_FORBIDDEN)
        submission = Submission.objects.create(**data)
        RedisQueue.put('queue:submission', submission.ID)

        return Response(submission.ID, status=HTTP_200_OK)


class SubmissionGetView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Submission.objects.filter(contest_id__isnull=True)
    permission_classes = (SubmissionCheck,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('username', 'result', 'language', 'problem', 'contest')

    def get_queryset(self):
        queryset = Submission.objects.filter(contest_id__isnull=True)

        myself = self.request.query_params.get("myself", "").strip('/')
        if myself == "true":
            queryset = queryset.filter(username=self.request.user)
        return queryset

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'list':
            return SubmissionListSerializer
        if hasattr(self, 'action') and self.action == 'retrieve':
            return SubmissionSerializer


class ContestSubmissionGetView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Submission.objects.all()
    permission_classes = (SubmissionCheck,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('username', 'result', 'language', 'problem', 'contest')

    def get_queryset(self):
        queryset = Submission.objects.filter(contest_id__isnull=False)

        myself = self.request.query_params.get("myself", "").strip('/')
        if myself == "true":
            queryset = queryset.filter(username=self.request.user)
        return queryset

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'list':
            return SubmissionListSerializer
        if hasattr(self, 'action') and self.action == 'retrieve':
            return SubmissionSerializer
