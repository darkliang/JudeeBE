from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from contest.models import Contest
from utils.model_field import RichTextField
from django.contrib.postgres.fields import JSONField
from user.models import User


# Create your models here.


class ProblemTag(models.Model):
    name = models.CharField(max_length=50,unique=True)

    class Meta:
        db_table = "problem_tag"
        ordering = ("id",)


class Problem(models.Model):
    # display ID
    # problem_id = models.TextField(db_index=True,primary_key=True)
    ID = models.AutoField(primary_key=True)
    contest = models.ManyToManyField(Contest, blank=True)
    # for contest problem
    is_public = models.BooleanField(default=False)
    title = models.TextField()
    # HTML
    description = RichTextField()
    input_description = RichTextField()
    output_description = RichTextField()
    # [{"input": "test", "output": "123"}, {"input": "test123", "output": "456"}]
    samples = JSONField()
    # test_case_id = models.TextField()
    # [{"input_name": "1.in", "output_name": "1.out", "score": 0}]
    test_case_score = JSONField()
    hint = RichTextField(null=True)
    # ["java", "cpp"]
    languages = JSONField()
    # {"language": "java","template": null}, {"language": "cpp","template": null}
    template = JSONField(null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    # we can not use auto_now here
    last_update_time = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    # ms
    time_limit = models.IntegerField()
    # MB
    memory_limit = models.IntegerField()
    # special judge related
    # spj = models.BooleanField(default=False)
    # spj_language = models.TextField(null=True)
    # spj_code = models.TextField(null=True)
    # spj_version = models.TextField(null=True)
    # spj_compile_ok = models.BooleanField(default=False)
    # rule_type = models.CharField(max_length=10)
    # visible = models.BooleanField(default=True)
    difficulty = models.IntegerField(null=False, default=1, validators=[MaxValueValidator(5), MinValueValidator(1)])
    tags = models.ManyToManyField(ProblemTag, blank=True)
    source = models.TextField(null=True)
    # for OI mode
    total_score = models.IntegerField(default=0)
    submission_number = models.BigIntegerField(default=0)
    accepted_number = models.BigIntegerField(default=0)
    # {JudgeStatus.ACCEPTED: 3, JudgeStaus.WRONG_ANSWER: 11}, the number means count
    statistic_info = JSONField(default=dict)

    # share_submission = models.BooleanField(default=False)

    class Meta:
        db_table = "problem"
        # unique_together = (("_id", "contest"),)
        ordering = ("create_time",)

    def add_submission_number(self):
        self.submission_number = models.F("submission_number") + 1
        self.save(update_fields=["submission_number"])

    def add_ac_number(self):
        self.accepted_number = models.F("accepted_number") + 1
        self.save(update_fields=["accepted_number"])

