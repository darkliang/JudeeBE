from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from JudeeBE.settings import SUBMISSION_QUEUE
from problem.models import Problem
from submission.models import Submission
from submission.serializers import SubmissionSerializer
from utils.permissions import ManagerOnly, UserLoginOnly


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

        # judge_task.send(submission.id, submission.problem.id)
        return Response("OK", status=HTTP_200_OK)


class SubmissionCreateView(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    # permission_classes = (UserLoginOnly,)
    throttle_scope = "judge"
    throttle_classes = [ScopedRateThrottle, ]

    def create(self, request, *args, **kwargs):
        data = dict(request.data)
        data["username"] = request.user
        try:
            data["problem"] = Problem.objects.get(ID=data.get("problem"))
        except (ValueError, Problem.DoesNotExist):
            return Response("Wrong problem ID", status=HTTP_400_BAD_REQUEST)
        data["ip"] = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')

        submission = Submission.objects.create(**data)
        SUBMISSION_QUEUE.add(submission)

        return Response(submission.ID, status=HTTP_200_OK)
