import os
import zipfile

from django.db.models.query_utils import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from JudeeBE.settings import TEST_CASE_DIR
from problem.models import Problem, ProblemTag
from utils.permissions import ManagerPostOnly
from problem.serializers import ProblemSerializer, ProblemTagSerializer


class ProblemView(viewsets.GenericViewSet, mixins.DestroyModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin, mixins.ListModelMixin):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    filter_backends = (DjangoFilterBackend,)
    pagination_class = LimitOffsetPagination
    filter_fields = ('is_public', 'created_by')
    permission_classes = (ManagerPostOnly,)
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Problem.objects.all()
        tag_ids = self.request.query_params.get("tags", "").strip('/')
        if tag_ids:
            for tag_id in tag_ids.split(','):
                if tag_id:
                    try:
                        queryset = queryset.filter(tags=int(tag_id))
                    except ValueError:
                        pass

        keyword = self.request.query_params.get("keyword", "").strip('/')
        if keyword:
            queryset = queryset.filter(Q(title__icontains=keyword) | Q(ID__icontains=keyword))
        diffs = self.request.query_params.get("diff", "").strip('/')
        if diffs:
            queryset = queryset.filter(difficulty__in=diffs.split(','))
        return queryset

    # noinspection PyMethodOverriding
    def create(self, request):
        data = dict(request.data)
        tags = data.pop("tags")
        data["created_by"] = request.user
        # print(tags)
        total_score = 0
        for score in data["test_case_score"]:
            total_score += score
        data["total_score"] = total_score
        problem = Problem.objects.create(**data)
        for item in tags:
            try:
                tag = ProblemTag.objects.get(name=item)
            except ProblemTag.DoesNotExist:
                tag = ProblemTag.objects.create(name=item)
            # print(tag)
            problem.tags.add(tag)
        # 返回题目ID
        return Response(problem.ID, status=HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        data = dict(request.data)
        problem = self.get_object()
        total_score = 0
        for score in data["test_case_score"]:
            total_score += score
        data["total_score"] = total_score
        problem.tags.clear()
        tags = data.pop("tags")
        data.pop("created_by")
        for item in tags:
            try:
                tag = ProblemTag.objects.get(name=item)
            except ProblemTag.DoesNotExist:
                tag = ProblemTag.objects.create(name=item)
            problem.tags.add(tag)
        for k, v in data.items():
            setattr(problem, k, v)
        problem.save()
        return Response(problem.ID, status=HTTP_200_OK)


class ProblemTagView(viewsets.ModelViewSet):
    queryset = ProblemTag.objects.all()
    serializer_class = ProblemTagSerializer
    permission_classes = (ManagerPostOnly,)
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]


def check_name_list(name_list, case_num):
    prefix = 0
    while True:
        prefix += 1
        in_name = "{}.in".format(prefix)
        out_name = "{}.out".format(prefix)
        if in_name in name_list and out_name in name_list:
            continue
        else:
            if len(name_list) == (prefix - 1) * 2:
                return (True, "Upload success") if case_num == prefix - 1 else (False, "Wrong case number")
            else:
                return False, "Wrong filename format"


class TestCaseUploadAPI(APIView):
    permission_classes = (ManagerPostOnly,)

    def post(self, request):
        data = request.data
        raw_file = request.FILES.get("file", None)

        try:
            file = zipfile.ZipFile(raw_file, "r")
        except zipfile.BadZipFile:
            return Response("Bad zip file", status=HTTP_400_BAD_REQUEST)

        try:
            problem = Problem.objects.get(ID=data.get("problem_ID"))
        except (Problem.DoesNotExist, ValueError):
            return Response("No such problem", status=HTTP_404_NOT_FOUND)

        is_passed, info = check_name_list(file.namelist(), len(problem.test_case_score))
        if not is_passed:
            return Response(info, status=HTTP_400_BAD_REQUEST)
        else:
            for fileM in file.namelist():
                file.extract(fileM, os.path.join(TEST_CASE_DIR, str(problem.ID)))
            file.close()
            return Response(info, status=HTTP_200_OK)
