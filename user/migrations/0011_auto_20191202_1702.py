# Generated by Django 2.2.7 on 2019-12-02 17:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_auto_20191121_1140'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('-type',)},
        ),
    ]