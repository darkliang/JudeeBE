# Generated by Django 2.2.7 on 2019-11-21 23:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0005_auto_20191120_2359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='last_update_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]