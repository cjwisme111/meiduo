# Generated by Django 2.2.5 on 2020-04-08 08:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth', '0003_auto_20200408_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qquser',
            name='create_time',
            field=models.TimeField(auto_now_add=datetime.datetime(2020, 4, 8, 16, 44, 49, 154102), verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='qquser',
            name='update_time',
            field=models.TimeField(auto_now=datetime.datetime(2020, 4, 8, 16, 44, 49, 154102), verbose_name='更新时间'),
        ),
    ]
