# Generated by Django 2.2.5 on 2020-04-13 08:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth', '0005_auto_20200409_2123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qquser',
            name='create_time',
            field=models.TimeField(auto_now_add=datetime.datetime(2020, 4, 13, 16, 54, 47, 360391), verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='qquser',
            name='update_time',
            field=models.TimeField(auto_now=datetime.datetime(2020, 4, 13, 16, 54, 47, 360391), verbose_name='更新时间'),
        ),
    ]