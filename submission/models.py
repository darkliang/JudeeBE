from django.db import models
from contest.models import Contest
from problem.models import Problem
from user.models import User
from utils.constants import JudgeStatus
from django.contrib.postgres.fields import JSONField


class Submission(models.Model):
    ID = models.AutoField(primary_key=True, db_index=True)
    contest = models.ForeignKey(Contest, null=True, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.TextField()
    result = models.IntegerField(db_index=True, default=JudgeStatus.PENDING)
    # 从JudgeServer返回的判题详情
    info = JSONField(default=dict)
    language = models.CharField(max_length=15)
    # shared = models.BooleanField(default=False)

    # 存储该提交所用时间和内存值，方便提交列表显示
    # {time_cost: "", memory_cost: "", err_info: "", score: 0}
    statistic_info = JSONField(default=dict)
    ip = models.GenericIPAddressField(unpack_ipv4=False, null=True)

    class Meta:
        db_table = "submission"
        ordering = ("-create_time",)

    def __str__(self):
        return self.ID
