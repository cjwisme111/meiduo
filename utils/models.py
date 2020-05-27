# -*- coding: utf-8 -*-
from django.db import models
from datetime import datetime

class BaseModel(models.Model):

    create_time = models.TimeField(auto_now_add=datetime.now(),verbose_name='创建时间') # auto_now_add 首次创建设置的value
    update_time = models.TimeField(auto_now=datetime.now(),verbose_name='更新时间') # auto_now 每次创建设置的value

    class Meta:
        abstract = True # 说明是抽象模型类, 用于继承使用，数据库迁移时不会创建BaseModel的表