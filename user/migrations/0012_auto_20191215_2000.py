# Generated by Django 2.2.7 on 2019-12-15 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_auto_20191202_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(default='', max_length=50, null=True),
        ),
    ]
