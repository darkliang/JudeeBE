# Generated by Django 2.2.7 on 2019-12-11 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0002_remove_contest_real_time_rank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contest',
            name='title',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
