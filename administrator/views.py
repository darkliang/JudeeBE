from django.core.cache import cache
from django.db.models.aggregates import Count
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from datetime import timedelta
from contest.models import Contest
from problem.models import Problem
from submission.models import Submission
from user.models import User, UserLoginData
from utils.permissions import SuperAdminRequired
from utils.shortcuts import submission_aggregate
from django.utils.timezone import now


class OverallAPI(APIView):
    permission_classes = (SuperAdminRequired,)

    def get(self, request):
        resp = dict()
        cur = now()
        resp['user_number'] = User.objects.all().count()
        # days =

        resp['problem_number'] = Problem.objects.all().count()
        resp['submission_number'] = Submission.objects.all().count()
        resp['contest_number'] = {
            'not_start': Contest.objects.filter(start_time__gt=cur).count(),
            'ended': Contest.objects.filter(end_time__lt=cur).count(),
            'underway': Contest.objects.filter(start_time__lte=cur, end_time__gte=cur).count(),
        }
        return Response(resp, status=HTTP_200_OK)


class SubmissionStatisticsAPI(APIView):
    permission_classes = (SuperAdminRequired,)

    def get(self, request):
        offset = int(request.GET.get('offset', 7))
        cache_key = 'admin-statistics:submission:{}'.format(offset)
        # cache.delete(cache_key)
        date_list = cache.get(cache_key)
        if not date_list:
            cur = now()
            days = cur - timedelta(days=offset)
            submissions = Submission.objects.filter(create_time__gte=days).values('create_time', 'result')
            date_list = submission_aggregate(submissions, cur, offset)
            cache.set(cache_key, date_list, 60 * 60 * 8)

        return Response(date_list, status=HTTP_200_OK)


class RecentSubmissionAPI(APIView):
    permission_classes = (SuperAdminRequired,)

    def get(self, request):
        offset = int(request.GET.get('offset', 24))
        hours = now() - timedelta(hours=offset)
        submissions = Submission.objects.filter(create_time__gte=hours).order_by('result').values('result').annotate(
            count=Count('result'))

        return Response(submissions, status=HTTP_200_OK)


class UserLoginStatisticsAPI(APIView):
    permission_classes = (SuperAdminRequired,)

    def get(self, request):
        offset = int(request.GET.get('offset', 7))
        cache_key = 'admin-statistics:login_data:{}'.format(offset)
        cache.delete(cache_key)
        login_data = cache.get(cache_key)
        if not login_data:
            cur = now()
            days = cur - timedelta(days=offset)
            all_data = UserLoginData.objects.filter(login_time__gte=days).values('username').annotate(
                count=Count('username')).order_by('-count')
            login_data = {'week_activists': all_data.count(), 'most_active': all_data[:50]}

            cache.set(cache_key, login_data, 60 * 60)

        return Response(login_data, status=HTTP_200_OK)
