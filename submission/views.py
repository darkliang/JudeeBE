from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from submission.models import Submission


class SubmissionRejudgeAPI(APIView):

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

        judge_task.send(submission.id, submission.problem.id)
        return self.success()
