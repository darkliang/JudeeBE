# Generated by Django 2.2.7 on 2019-11-21 02:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_auto_20191121_0205'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='register_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
