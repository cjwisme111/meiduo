# -*- coding: utf-8 -*-
from celery_tasks.main import celery_app
import time

@celery_app.task(name="send_sms_code")
def send_sms_code(mobile,sms_coed):
    """
    模拟发短信
    :param mobile: 手机号
    :param sms_coed: 验证码
    :return:
    """
    # CCP().send_template_sms(mobile, [sms_coed, constants.SMS_TEMPLATE_CODE_TIME], constants.YUNTONGXUN_CODE)
    print(mobile,sms_coed)
    time.sleep(0.5)
    return 0