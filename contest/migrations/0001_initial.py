# Generated by Django 2.2.7 on 2019-11-19 18:54

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import utils.model_field


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('description', utils.model_field.RichTextField()),
                ('real_time_rank', models.BooleanField()),
                ('password', models.TextField(null=True)),
                ('rule_type', models.TextField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('last_update_time', models.DateTimeField(auto_now=True)),
                ('visible', models.BooleanField(default=True)),
                ('allowed_ip_ranges', django.contrib.postgres.fields.jsonb.JSONField(default=list)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User')),
            ],
            options={
                'db_table': 'contest',
                'ordering': ('-start_time',),
            },
        ),
        migrations.CreateModel(
            name='ContestAnnouncement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('content', utils.model_field.RichTextField()),
                ('visible', models.BooleanField(default=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contest.Contest')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User')),
            ],
            options={
                'db_table': 'contest_announcement',
                'ordering': ('-create_time',),
            },
        ),
        migrations.CreateModel(
            name='OIContestRank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_number', models.IntegerField(default=0)),
                ('total_score', models.IntegerField(default=0)),
                ('submission_info', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contest.Contest')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User')),
            ],
            options={
                'db_table': 'oi_contest_rank',
                'unique_together': {('user', 'contest')},
            },
        ),
        migrations.CreateModel(
            name='ACMContestRank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_number', models.IntegerField(default=0)),
                ('accepted_number', models.IntegerField(default=0)),
                ('total_time', models.IntegerField(default=0)),
                ('submission_info', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contest.Contest')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User')),
            ],
            options={
                'db_table': 'acm_contest_rank',
                'unique_together': {('user', 'contest')},
            },
        ),
    ]