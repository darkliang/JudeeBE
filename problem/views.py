import os
import shutil
import tempfile
import zipfile
from wsgiref.util import FileWrapper

from django.db import transaction
from django.http import StreamingHttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN, \
    HTTP_204_NO_CONTENT
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from JudeeBE.settings import TEST_CASE_DIR
from problem.models import Problem, ProblemTag
from utils.constants import AdminType, SysOptions, Difficulty
from utils.fps.parser import FPSHelper, FPSParser
from utils.permissions import ManagerPostOnly, ManagerOnly
from problem.serializers import ProblemSerializer, ProblemTagSerializer, ProblemListSerializer, FPSProblemSerializer


class ProblemView(viewsets.GenericViewSet, mixins.DestroyModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin, mixins.ListModelMixin):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    pagination_class = LimitOffsetPagination
    filter_fields = ('is_public', 'created_by')
    search_fields = ('title', 'ID', 'source')
    # permission_classes = (ManagerPostOnly,)
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'list':
            return ProblemListSerializer
        if hasattr(self, 'action') and self.action == 'retrieve':
            return ProblemSerializer
        return ProblemSerializer  # I dont' know what you want for create/destroy/update.

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
        if data.get("test_case_score", None):
            total_score = 0
            for score in data["test_case_score"]:
                total_score += score
            data["total_score"] = total_score
        if data.get("tags", None):
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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 删除样例
        test_case_dir = os.path.join(TEST_CASE_DIR, str(instance.ID))
        if os.path.exists(test_case_dir):
            shutil.rmtree(test_case_dir)
        self.perform_destroy(instance)
        return Response(status=HTTP_204_NO_CONTENT)


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
    permission_classes = (ManagerOnly,)

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
        if request.user != problem.created_by and request.user.type != AdminType.SUPER_ADMIN:
            return Response("You have no permission to this problem", status=HTTP_403_FORBIDDEN)

        is_passed, info = check_name_list(file.namelist(), len(problem.test_case_score))
        if not is_passed:
            return Response(info, status=HTTP_400_BAD_REQUEST)
        else:
            test_case_dir = os.path.join(TEST_CASE_DIR, str(problem.ID))
            if os.path.exists(test_case_dir):
                shutil.rmtree(test_case_dir)
            for fileM in file.namelist():
                file.extract(fileM, test_case_dir)
            file.close()
            return Response(info, status=HTTP_200_OK)


class TestCaseDownloadAPI(APIView):
    permission_classes = (ManagerOnly,)
    throttle_scope = "download"
    throttle_classes = [ScopedRateThrottle, ]

    def get(self, request, problem_id):
        start_dir = (os.path.join(TEST_CASE_DIR, str(problem_id)))
        if not os.path.isfile(os.path.join(start_dir, '1.in')):
            return Response("No test cases", status=HTTP_404_NOT_FOUND)
        temp = tempfile.TemporaryFile()

        with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED) as zf:
            for dir_path, dir_names, filenames in os.walk(start_dir):
                f_path = dir_path.replace(start_dir, '')  # 这一句很重要，不replace的话，就从根目录开始复制
                f_path = f_path and f_path + os.sep or ''  # 这句话理解我也点郁闷，实现当前文件夹以及包含的所有文件的压缩
                for filename in filenames:
                    zf.write(os.path.join(dir_path, filename), f_path + filename)

        response = StreamingHttpResponse(FileWrapper(temp),
                                         content_type="application/zip")
        response["Content-Length"] = temp.tell()
        response["Content-Disposition"] = "attachment; filename=problem_{}_test_cases.zip".format(problem_id)
        temp.seek(0)
        return response


class FPSProblemImport(APIView):
    permission_classes = (ManagerOnly,)

    # 创建problem 并返回ID
    def _create_problem(self, problem_data, creator):
        if problem_data["time_limit"]["unit"] == "ms":
            time_limit = problem_data["time_limit"]["value"]
        else:
            time_limit = problem_data["time_limit"]["value"] * 1000

        return Problem.objects.create(
            title=problem_data["title"],
            description=problem_data["description"],
            input_description=problem_data["input"],
            output_description=problem_data["output"],
            hint=problem_data["hint"],
            test_case_score=problem_data["test_case_score"],
            total_score=len(problem_data["test_case_score"]) * 10,
            time_limit=time_limit,
            memory_limit=problem_data["memory_limit"]["value"],
            samples=problem_data["samples"],
            source=problem_data.get("source", None),
            is_public=False,
            languages=SysOptions.language_names,
            created_by=creator,
            difficulty=Difficulty.MEDIUM).ID

    def post(self, request):
        raw_file = request.FILES.get('file', None)
        if not raw_file:
            Response('Please upload the file', HTTP_400_BAD_REQUEST)
        # HACK windows 不能二次打开文件
        with tempfile.NamedTemporaryFile("wb", delete=False) as tf:
            for chunk in raw_file.chunks(4096):
                tf.file.write(chunk)
        problems = FPSParser(tf.name).parse()
        os.unlink(tf.name)

        info = []
        cnt = 0
        with transaction.atomic():
            for _problem in problems:
                if _problem["spj"]:
                    # Special judge not supported yet
                    info.append([])
                    cnt += 1
                    continue
                score = [10 for _ in range(len(_problem["test_cases"]))]
                s = FPSProblemSerializer(data=_problem)
                if not s.is_valid():
                    return Response("Parse FPS file error: {}".format(s.errors), HTTP_400_BAD_REQUEST)
                problem_data = s.data
                problem_data["test_case_score"] = score
                test_case_dir = os.path.join(TEST_CASE_DIR, str(self._create_problem(problem_data, request.user)))
                os.mkdir(test_case_dir)
                info.append(FPSHelper.save_test_case(_problem['test_cases'], test_case_dir))
        return Response({"import_count": len(problems) - cnt, "info": info}, status=HTTP_200_OK)
