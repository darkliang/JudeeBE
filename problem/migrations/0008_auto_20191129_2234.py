# Generated by Django 2.2.7 on 2019-11-29 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0007_auto_20191129_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problemtag',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
