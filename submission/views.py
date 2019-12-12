import ipaddress
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_204_NO_CONTENT, \
    HTTP_403_FORBIDDEN
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from JudeeBE.settings import SUBMISSION_QUEUE
from problem.models import Problem
from submission.models import Submission
from submission.serializers import SubmissionCreateSerializer, SubmissionListSerializer
from utils.constants import ContestStatus
from utils.permissions import ManagerOnly, UserLoginOnly, SubmissionCheck


class SubmissionRejudgeAPI(APIView):
    permission_classes = (ManagerOnly,)

    def get(self, request):
        id = request.GET.get("id")
        if not id:
            return Response("Parameter error, id is required", status=HTTP_400_BAD_REQUEST)
        try:
            submission = Submission.objects.select_related("problem").get(id=id, contest_id__isnull=True)
        except Submission.DoesNotExist:
            return Response("Submission does not exists", status=HTTP_404_NOT_FOUND)
        submission.statistic_info = {}
        submission.save()

        SUBMISSION_QUEUE.produce(submission.ID)
        return Response(status=HTTP_204_NO_CONTENT)


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
    serializer_class = SubmissionCreateSerializer
    permission_classes = (UserLoginOnly,)
    throttle_scope = "judge"
    throttle_classes = [ScopedRateThrottle, ]

    def create(self, request, *args, **kwargs):
        data = dict(request.data)
        data["username"] = request.user
        data["ip"] = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
        try:
            data["problem"] = Problem.objects.get(ID=data.get("problem"))
        except (ValueError, Problem.DoesNotExist):
            return Response("Wrong problem ID", status=HTTP_400_BAD_REQUEST)
        contest_id = data.pop('contest')
        if contest_id:
            try:
                data["contest"] = Problem.objects.get(ID=data.get("problem"))
            except (ValueError, Problem.DoesNotExist):
                return Response("Wrong contest ID", status=HTTP_400_BAD_REQUEST)
            error = check_contest_permission(data)
            if error:
                return Response(error, status=HTTP_403_FORBIDDEN)
        submission = Submission.objects.create(**data)
        SUBMISSION_QUEUE.produce(submission.ID)

        return Response(submission.ID, status=HTTP_200_OK)


class SubmissionGetView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Submission.objects.filter(contest_id__isnull=True).select_related("problem__created_by")
    permission_classes = (SubmissionCheck,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('username', 'result', 'language', 'problem')

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'list':
            return SubmissionListSerializer
        if hasattr(self, 'action') and self.action == 'retrieve':
            return SubmissionCreateSerializer


