from ipaddress import ip_network
import dateutil.parser
from django.core.cache import cache
from django.db.models.query_utils import Q
from django.db.utils import IntegrityError
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT, \
    HTTP_403_FORBIDDEN
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from contest.models import Contest, ACMContestRank, OIContestRank, ContestAnnouncement
from contest.serializers import ContestSerializer, ContestAdminSerializer, ContestListSerializer, \
    OIContestRankSerializer, ACMContestRankSerializer, ContestAnnouncementSerializer
from problem.models import Problem, ContestProblem
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

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'list':
            return ContestListSerializer
        if hasattr(self, 'action') and self.action == 'retrieve':
            return ContestSerializer
        return ContestListSerializer  # I dont' know what you want for create/destroy/update.

    def get_queryset(self):
        queryset = Contest.objects.all() if self.request.auth and self.request.user.is_admin() else Contest.objects.filter(
            visible=True)
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

    def create(self, request, *args, **kwargs):
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

    def update(self, request, *args, **kwargs):
        data = request.data
        contest = self.get_object()
        try:
            data.pop('created_by')
        except KeyError:
            pass
        # try:
        #     contest = Contest.objects.get(id=data.pop("id"))
        # except Contest.DoesNotExist:
        #     return Response("Contest does not exist", status=HTTP_404_NOT_FOUND)
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
    permission_classes = (ManagerPostOnly,)
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
                contest_problem = ContestProblem(problem=problem, contest=contest)
                contest_problem.save()
                # contest.problem_set.add(problem)
            except Problem.DoesNotExist:
                problem_not_exist.append(problem_id)
            except IntegrityError as e:
                print(e)
                continue

        if len(problem_not_exist) > 0:
            return Response("Problem {} does not exist".format(problem_not_exist), status=HTTP_200_OK)
        else:
            return Response(status=HTTP_204_NO_CONTENT)


class ContestDeleteProblemAPIView(APIView):
    permission_classes = (ManagerPostOnly,)
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
    permission_classes = (UserLoginOnly,)

    def get(self, request, contest_id):
        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            return Response("Contest does not exist", status=HTTP_404_NOT_FOUND)
        queryset = contest.problem_set.all().order_by('contestproblem__id')

        return Response(
            queryset.values('ID', 'title', 'total_score', 'submission_number', 'accepted_number', 'created_by',
                            'contestproblem__id', 'contestproblem__first_ac', 'is_public'),
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
            return Response("Wrong password", status=HTTP_400_BAD_REQUEST)


class JoinContest(APIView):
    permission_classes = (UserLoginOnly,)

    def post(self, request, contest_id):
        try:
            contest = Contest.objects.get(id=contest_id)
        except Contest.DoesNotExist:
            return Response("Contest does not exist", status=HTTP_404_NOT_FOUND)
        if contest.password:
            return Response("Password required", status=HTTP_403_FORBIDDEN)
        if contest.status == ContestStatus.CONTEST_ENDED:
            return Response("Contest is ended", status=HTTP_403_FORBIDDEN)
        if contest.rule_type == RuleType.OI:
            try:
                OIContestRank.objects.create(user=request.user, contest=contest)
            except IntegrityError:
                pass
        elif contest.rule_type == RuleType.ACM:
            try:
                ACMContestRank.objects.create(user=request.user, contest=contest)
            except IntegrityError:
                pass
        return Response(status=HTTP_204_NO_CONTENT)


class ContestRankView(APIView):
    permission_classes = (UserLoginOnly,)

    def get(self, request):
        contest = request.GET.get('contest', None)
        try:
            contest = Contest.objects.get(id=contest)
        except (Contest.DoesNotExist, ValueError):
            return Response(status=HTTP_404_NOT_FOUND)
        # OI赛制 只有比赛中的查询才会查数据库 不然直接获取缓存
        problems = contest.problem_set.all().order_by('contestproblem__id').values('ID', 'contestproblem__id')
        if contest.rule_type == RuleType.OI:
            if contest.status == ContestStatus.CONTEST_UNDERWAY:
                return Response(
                    {'rule_type': contest.rule_type, 'problems': problems, 'rank_list': self.get_rank_list(contest)},
                    status=HTTP_200_OK)
            cache_key = 'contest-rank:{}'.format(contest.id)
            # cache.delete(cache_key)
            rank_list = cache.get(cache_key)
            if not rank_list:
                rank_list = {'rule_type': contest.rule_type, 'problems': problems,
                             'rank_list': self.get_rank_list(contest)}
                # 设置缓存1天过期
                cache.set(cache_key, rank_list, 60 * 60 * 24)
            return Response(rank_list,
                            status=HTTP_200_OK)
        elif contest.rule_type == RuleType.ACM:
            if contest.status == ContestStatus.CONTEST_UNDERWAY:
                return Response(
                    {'rule_type': contest.rule_type, 'problems': problems, 'rank_list': self.get_rank_list(contest)},
                    status=HTTP_200_OK)
            else:
                cache_key = 'contest-rank:{}'.format(contest.id)
                rank_list = cache.get(cache_key)
                if not rank_list:
                    rank_list = {'rule_type': contest.rule_type, 'problems': problems,
                                 'rank_list': self.get_rank_list(contest)}
                    # 封榜状态 1小时后cache过期,否则1天过期
                    if contest.status == ContestStatus.CONTEST_LOCK_RANK:
                        cache.set(cache_key, rank_list, 60 * 60)
                    else:
                        cache.set(cache_key, rank_list, 60 * 60 * 24 * 1)
                return Response(rank_list,
                                status=HTTP_200_OK)

    def get_rank_list(self, contest):
        if contest.rule_type == RuleType.OI:
            queryset = OIContestRank.objects.filter(contest=contest).order_by('-total_score', 'user__username')
            return OIContestRankSerializer(queryset, many=True).data
        elif contest.rule_type == RuleType.ACM:
            queryset = ACMContestRank.objects.filter(contest=contest).order_by('-accepted_number', 'total_time')
            return ACMContestRankSerializer(queryset, many=True).data


class ContestAnnouncementView(viewsets.ModelViewSet):
    queryset = ContestAnnouncement.objects.all()
    permission_classes = (ManagerPostOnly,)
    serializer_class = ContestAnnouncementSerializer
    throttle_classes = [ScopedRateThrottle, ]
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('contest',)

    def get_queryset(self):
        queryset = ContestAnnouncement.objects.all() if (self.request.auth and self.request.user.is_admin()) else \
            ContestAnnouncement.objects.filter(visible=True)
        return queryset

    def create(self, request, *args, **kwargs):
        data = dict(request.data)
        data["created_by"] = request.user
        try:
            data["contest"] = Contest.objects.get(id=data["contest"])
        except (Contest.DoesNotExist, KeyError):
            return Response("Wrong contest ID", HTTP_400_BAD_REQUEST)
        contest_announcement = ContestAnnouncement.objects.create(**data)
        return Response(contest_announcement.id, status=HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        contest_announcement = self.get_object()
        data = dict(request.data)
        data["created_by"] = request.user
        try:
            data["contest"] = Contest.objects.get(id=data["contest"])
        except (Contest.DoesNotExist, KeyError):
            return Response("Wrong contest ID", HTTP_400_BAD_REQUEST)
        for k, v in data.items():
            setattr(contest_announcement, k, v)
        contest_announcement.save()
        return Response(status=HTTP_204_NO_CONTENT)
