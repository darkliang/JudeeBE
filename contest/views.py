from ipaddress import ip_network
import dateutil.parser
from django.db.models.query_utils import Q
from django.db.utils import IntegrityError
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, mixins
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from contest.models import Contest, ACMContestRank, OIContestRank
from contest.serializers import ContestSerializer, ContestAdminSerializer
from problem.models import Problem
from utils.constants import ContestStatus, RuleType
from utils.permissions import ManagerPostOnly, UserLoginOnly, ContestPwdRequired


class ContestView(viewsets.ModelViewSet):
    queryset = Contest.objects.all()
    serializer_class = ContestSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (ManagerPostOnly, ContestPwdRequired)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_fields = ("rule_type", "created_by")
    search_fields = ('title', 'id')
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]

    def get_queryset(self):
        queryset = Contest.objects.all()
        status = self.request.query_params.get("status", "").strip('/')
        if status:
            cur = now()
            condition = Q()
            for one_status in status.split(','):
                if one_status == ContestStatus.CONTEST_NOT_START:
                    condition |= Q(start_time__gt=cur)
                elif one_status == ContestStatus.CONTEST_ENDED:
                    condition |= Q(end_time__lt=cur)
                else:
                    condition |= Q(start_time__lte=cur, end_time__gte=cur)
            queryset = queryset.filter(condition)
        return queryset

    def create(self, request):
        data = request.data
        data["created_by"] = request.user
        data["start_time"] = dateutil.parser.parse(data["start_time"])
        data["end_time"] = dateutil.parser.parse(data["end_time"])
        if data["end_time"] <= data["start_time"]:
            return Response("Start time must occur earlier than end time", status=HTTP_400_BAD_REQUEST)
        if data.get("password") and data["password"] == "":
            data["password"] = None
        for ip_range in data["allowed_ip_ranges"]:
            try:
                ip_network(ip_range, strict=False)
            except ValueError:
                return Response("{} is not a valid cidr network".format(ip_range), status=HTTP_400_BAD_REQUEST)
        contest = Contest.objects.create(**data)
        return Response(ContestAdminSerializer(contest).data, status=HTTP_200_OK)

    def update(self, request):
        data = request.data
        try:
            contest = Contest.objects.get(id=data.pop("id"))
        except Contest.DoesNotExist:
            return Response("Contest does not exist", status=HTTP_404_NOT_FOUND)
        data["start_time"] = dateutil.parser.parse(data["start_time"])
        data["end_time"] = dateutil.parser.parse(data["end_time"])
        if data["end_time"] <= data["start_time"]:
            return Response("Start time must occur earlier than end time", status=HTTP_400_BAD_REQUEST)
        if not data["password"]:
            data["password"] = None
        for ip_range in data["allowed_ip_ranges"]:
            try:
                ip_network(ip_range, strict=False)
            except ValueError:
                return Response("{} is not a valid cidr network".format(ip_range), status=HTTP_400_BAD_REQUEST)

        for k, v in data.items():
            setattr(contest, k, v)
        contest.save()
        return Response(ContestAdminSerializer(contest).data, status=HTTP_200_OK)


class ContestAddProblemAPIView(APIView):
    # permission_classes = (ManagerPostOnly,)
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]

    def post(self, request, contest_id):
        data = request.data.copy()
        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            return Response("Contest does not exist", status=HTTP_404_NOT_FOUND)
        problem_not_exist = []
        for problem_id in data.pop("problems"):
            try:
                problem = Problem.objects.get(ID=problem_id)

                contest.problem_set.add(problem)
            except Problem.DoesNotExist:
                problem_not_exist.append(problem_id)
        if len(problem_not_exist) > 0:
            return Response("Problem {} does not exist".format(problem_not_exist), status=HTTP_200_OK)
        else:
            return Response(status=HTTP_204_NO_CONTENT)


class ContestDeleteProblemAPIView(APIView):
    # permission_classes = (ManagerPostOnly,)
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]

    def post(self, request, contest_id):
        data = request.data.copy()
        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            return Response("Contest does not exist", status=HTTP_404_NOT_FOUND)
        # problem_not_exist = []
        contest.problem_set.remove(*data.pop("problems"))

        return Response(status=HTTP_200_OK)


class ContestListProblemAPIView(APIView):
    # permission_classes = (UserLoginOnly,)

    def get(self, request, contest_id):
        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            return Response("Contest does not exist", status=HTTP_404_NOT_FOUND)
        queryset = contest.problem_set.all()
        return Response(
            queryset.values('ID', 'title', 'total_score', 'submission_number', 'accepted_number', 'created_by'),
            status=HTTP_200_OK)


'''
加入有密码的竞赛
'''


class JoinContestWithPwd(APIView):
    permission_classes = (UserLoginOnly,)

    def post(self, request, contest_id):
        data = request.data.copy()
        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            return Response("Contest does not exist", status=HTTP_404_NOT_FOUND)
        password = data.get('password', "")
        if password == contest.password:
            if contest.rule_type == RuleType.ACM:
                try:
                    ACMContestRank.objects.create(user=request.user, contest=contest)
                    return Response(ContestSerializer(contest).data, status=HTTP_200_OK)
                except IntegrityError:
                    return Response(status=HTTP_204_NO_CONTENT)
            elif contest.rule_type == RuleType.OI:
                try:
                    OIContestRank.objects.create(user=request.user, contest=contest)
                    return Response(ContestSerializer(contest).data, status=HTTP_200_OK)
                except IntegrityError:
                    return Response(status=HTTP_204_NO_CONTENT)
        else:
            return Response("Wrong password", status=HTTP_200_OK)
