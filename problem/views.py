from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from problem.models import Problem, ProblemTag
from problem.permission import ManagerPostOnly
from problem.serializers import ProblemSerializer, ProblemTagSerializer


class ProblemView(viewsets.GenericViewSet, mixins.DestroyModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin, mixins.ListModelMixin):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('is_public',)
    search_fields = ('title', 'description')
    permission_classes = (ManagerPostOnly,)
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Problem.objects.all()
        tag_ids = self.request.query_params.get('tags', None)
        if tag_ids:
            for tag_id in tag_ids.split(','):
                if tag_id:
                    queryset = queryset.filter(tags=int(tag_id))
        return queryset

    def post(self, request):
        data = request.data

        # todo check filename and score info
        tags = data.pop("tags")
        problem = Problem.objects.create(**data)
        for item in tags:
            try:
                tag = ProblemTag.objects.get(name=item)
            except ProblemTag.DoesNotExist:
                tag = ProblemTag.objects.create(name=item)
            problem.tags.add(tag)
        return Response('ok', status=HTTP_200_OK)

    # def get(self, request):
    #     # 问题详情页
    #     problem_id = request.GET.get("problem_id")
    #     if problem_id:
    #         try:
    #             problem = Problem.objects.select_related("created_by") \
    #                 .get(ID=problem_id, contest_id__isnull=True, is_public=True)
    #             problem_data = ProblemSerializer(problem).data
    #             # self._add_problem_status(request, problem_data)
    #             return Response(problem_data, HTTP_200_OK)
    #         except Problem.DoesNotExist:
    #             return Response("Problem not found", HTTP_404_NOT_FOUND)
    #
    #
    #     limit = request.GET.get("limit")
    #     if not limit:
    #         return self.error("Limit is needed")
    #
    #     problems = Problem.objects.select_related("created_by").filter(contest_id__isnull=True, visible=True)
    #     # 按照标签筛选
    #     tag_text = request.GET.get("tag")
    #     if tag_text:
    #         problems = problems.filter(tags__name=tag_text)
    #
    #     # 搜索的情况
    #     keyword = request.GET.get("keyword", "").strip()
    #     if keyword:
    #         problems = problems.filter(Q(title__icontains=keyword) | Q(_id__icontains=keyword))
    #
    #     # 难度筛选
    #     difficulty = request.GET.get("difficulty")
    #     if difficulty:
    #         problems = problems.filter(difficulty=difficulty)
    #     # 根据profile 为做过的题目添加标记
    #     data = self.paginate_data(request, problems, ProblemSerializer)
    #     self._add_problem_status(request, data)
    #     return self.success(data)


class ProblemTagView(viewsets.ModelViewSet):
    queryset = ProblemTag.objects.all()
    serializer_class = ProblemTagSerializer
    permission_classes = (ManagerPostOnly,)
    throttle_scope = "post"
    throttle_classes = [ScopedRateThrottle, ]

# class UploadFile(APIView):
#     def post(self, request, format=None):
