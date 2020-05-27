from django.shortcuts import render
from django.views import View
from django import http
from django_redis import get_redis_connection
import random
import logging

from celery_tasks.sms import tasks
from .libs.captcha.captcha import captcha
from utils.response_code import RETCODE


logger = logging.getLogger("django")

class ImageCodeView(View):

    def get(self, request, uuid):
        text, image = captcha.generate_captcha()
        redis = get_redis_connection(alias='image_code')
        key = "img_" + uuid
        redis.setex(key, 300, text)
        return http.HttpResponse(image, content_type='image/jpg')


class SmsCodeView(View):

    def get(self, request, mobile):
        """
        获取短信验证码
        :param mobile: 手机号
        :return: JSON
        """
        # 获取参数
        uuid = request.GET.get('uuid')
        image_code_client = request.GET.get('image_code')
        # 校验参数
        if not all([uuid, image_code_client]):
            return http.HttpResponseForbidden("必填参数")
        # 从缓存获取图片验证码
        redis_server = get_redis_connection(alias='image_code')
        image_code_server = redis_server.get("img_%s" % uuid)
        image_code_server = image_code_server.decode()

        if not image_code_server:
            return http.JsonResponse({"errmsg": "图形验证码已过期", "code": RETCODE.IMAGECODEERR})

        if image_code_server.lower() != image_code_client.lower():
            return http.JsonResponse({"errmsg": "图形验证码输入有误", "code": RETCODE.IMAGECODEERR})

        # 生成短信验证码
        sms_code = '%06d' % random.randint(1, 999999)
        redis = get_redis_connection(alias='image_code')
        key = "sms_" + mobile
        redis.setex(key, 300, sms_code)
        logger.info(sms_code)
        # 发送短信
        tasks.send_sms_code.delay(mobile, sms_code)
        # 返回参数
        return http.JsonResponse({"errmsg": "ok", "code": RETCODE.OK})
