# Generated by Django 2.2.7 on 2019-12-08 16:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contest',
            name='real_time_rank',
        ),
    ]
