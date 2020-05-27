# -*- coding: utf-8 -*-
from django.contrib.auth.backends import ModelBackend
import re
from .models import User
from django.conf import settings

from utils.signature import BaseSignature
from .constants import ACCESS_TOKEN_EXPIRES

class SignatureToken(BaseSignature):

    secret_key = settings.SECRET_KEY
    expiry = ACCESS_TOKEN_EXPIRES


class UsernameMobileModelBackend(ModelBackend):
    """自定义认证方法"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        验证重写
        :param username: 用户名或者手机号
        :param password: 密码
        :return: user对象
        """
        # 判断username 是用户还是手机号
        try:
            if re.match(r'1[3-9]\d{9}',username):
                # 手机号
                # 获取对象
                user = User.objects.get(mobile=username)
            else:
                # 用户名
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        # 校验密码
        if user.check_password(password):
            return user
        return None

        # 返回对象