# -*- coding: utf-8 -*-
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadData

from utils.exceptions import SignatureException
import logging

logger = logging.getLogger("django")

class BaseSignature:

    secret_key = None
    expiry = None

    @classmethod
    def generate_token(cls, data):
        """
        生成密文
        :param openid: 明文
        data:加密的数据
        :return: 密文
        """
        cls.check_fields()
        s = Serializer(cls.secret_key, cls.expiry)
        token = s.dumps(data)
        return token.decode()

    @classmethod
    def check_token(cls, token):
        """
        解密
        :param token: 密文:token
        :return: 明文data
        """
        s = Serializer(cls.secret_key, cls.expiry)
        try:
            data = s.loads(token)
        except BadData:
            return None
        else:
            return data

    @classmethod
    def check_fields(cls):
        if not all([cls.secret_key,cls.expiry]):
            raise SignatureException("缺少必填参数:secret_key,expiry")
