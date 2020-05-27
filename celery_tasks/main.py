# -*- coding: utf-8 -*-
from celery import Celery

# 为celery使用django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.dev'

# 1.创建生产者
celery_app = Celery("meiduo")


# 2. 中间件broker
celery_app.config_from_object("celery_tasks.config")

# 3 注册任务
celery_app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])

# 4 启动消费者
# celery -A celery_tasks.main worker -l info -P eventlet -c 1000