# Generated by Django 2.2.5 on 2020-04-18 11:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth', '0007_auto_20200413_1726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qquser',
            name='create_time',
            field=models.TimeField(auto_now_add=datetime.datetime(2020, 4, 18, 19, 43, 59, 766907), verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='qquser',
            name='update_time',
            field=models.TimeField(auto_now=datetime.datetime(2020, 4, 18, 19, 43, 59, 766907), verbose_name='更新时间'),
        ),
    ]
