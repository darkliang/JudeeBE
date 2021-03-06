# Generated by Django 2.2.7 on 2019-11-20 22:59

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import utils.model_field


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
        ('contest', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProblemTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'problem_tag',
            },
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('is_public', models.BooleanField(default=False)),
                ('title', models.TextField()),
                ('description', utils.model_field.RichTextField()),
                ('input_description', utils.model_field.RichTextField()),
                ('output_description', utils.model_field.RichTextField()),
                ('samples', django.contrib.postgres.fields.jsonb.JSONField()),
                ('test_case_score', django.contrib.postgres.fields.jsonb.JSONField()),
                ('hint', utils.model_field.RichTextField(null=True)),
                ('languages', django.contrib.postgres.fields.jsonb.JSONField()),
                ('template', django.contrib.postgres.fields.jsonb.JSONField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('last_update_time', models.DateTimeField(auto_now=True)),
                ('time_limit', models.IntegerField()),
                ('memory_limit', models.IntegerField()),
                ('difficulty', models.CharField(max_length=15)),
                ('source', models.TextField(null=True)),
                ('total_score', models.IntegerField(default=0)),
                ('submission_number', models.BigIntegerField(default=0)),
                ('accepted_number', models.BigIntegerField(default=0)),
                ('statistic_info', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('contest', models.ManyToManyField(to='contest.Contest')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User')),
                ('tags', models.ManyToManyField(to='problem.ProblemTag')),
            ],
            options={
                'db_table': 'problem',
                'ordering': ('create_time',),
            },
        ),
    ]
