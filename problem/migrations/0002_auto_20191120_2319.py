# Generated by Django 2.2.7 on 2019-11-20 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='contest',
            field=models.ManyToManyField(null=True, to='contest.Contest'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='tags',
            field=models.ManyToManyField(null=True, to='problem.ProblemTag'),
        ),
    ]
