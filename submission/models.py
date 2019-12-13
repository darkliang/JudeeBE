from django.db import models
from contest.models import Contest
from problem.models import Problem
from user.models import User
from utils.constants import JudgeStatus
from django.contrib.postgres.fields import JSONField


def default_statistic_info():
    return {"time_cost": 0, "memory_cost": 0, "score": 0, "results": []}


class Submission(models.Model):
    ID = models.AutoField(primary_key=True, db_index=True)
    contest = models.ForeignKey(Contest, null=True, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.TextField()
    result = models.IntegerField(db_index=True, default=JudgeStatus.PENDING)
    # 从JudgeServer返回的判题详情 之前statistic info 整合进info
    info = JSONField(default=list)
    language = models.CharField(max_length=15)
    # shared = models.BooleanField(default=False)

    # 存储该提交所用时间和内存值，方便提交列表显示
    # {time_cost: "", memory_cost: "", err_info: "", score: 0}
    time_cost = models.IntegerField(null=True)
    memory_cost = models.IntegerField(null=True)
    score = models.IntegerField(null=True)
    # statistic_info = JSONField(default=default_statistic_info)
    ip = models.GenericIPAddressField(unpack_ipv4=False, null=True)

    class Meta:
        db_table = "submission"
        ordering = ("-create_time",)

    def __str__(self):
        return self.ID
