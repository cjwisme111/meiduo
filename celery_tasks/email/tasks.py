# -*- coding: utf-8 -*-
from django.core.mail import send_mail
from django.conf import settings
import os

from celery_tasks.main import celery_app

# bind：保证task对象会作为第一个参数自动传入
# name：异步任务别名
# retry_backoff：异常自动重试的时间间隔 第n次(retry_backoff×2^(n-1))s
# max_retries：异常自动重试次数的上限
@celery_app.task(bind=True, name="send_verify_email", retry_backoff=3)
def send_verify_email(self, to_email, verify_url):
    """发送邮件"""

    # send_mail("标题",'文本消息',"来自",[],'富文本信息')
    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
    try:
        send_mail(subject, '', settings.EMAIL_HOST_USER, [to_email], html_message=html_message)
    except Exception as exc:
        raise self.retry(exc=exc, max_retries=3)
