# Generated by Django 2.2.7 on 2019-11-20 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0004_auto_20191120_2330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='last_update_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]