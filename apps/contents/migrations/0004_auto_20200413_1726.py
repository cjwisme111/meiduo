# Generated by Django 2.2.5 on 2020-04-13 09:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contents', '0003_auto_20200413_1654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='create_time',
            field=models.TimeField(auto_now_add=datetime.datetime(2020, 4, 13, 17, 26, 14, 161414), verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='content',
            name='update_time',
            field=models.TimeField(auto_now=datetime.datetime(2020, 4, 13, 17, 26, 14, 161414), verbose_name='更新时间'),
        ),
        migrations.AlterField(
            model_name='contentcategory',
            name='create_time',
            field=models.TimeField(auto_now_add=datetime.datetime(2020, 4, 13, 17, 26, 14, 161414), verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='contentcategory',
            name='update_time',
            field=models.TimeField(auto_now=datetime.datetime(2020, 4, 13, 17, 26, 14, 161414), verbose_name='更新时间'),
        ),
    ]
