# -*- coding: utf-8 -*-
import base64,pickle

class SerializationBase64:

    @staticmethod
    def serialized(data):
        """
        编码
        :param data: 原始数据
        :return: str
        """
        bytes_object = pickle.dumps(data)
        bytes_str = base64.b64encode(bytes_object)
        str_object = bytes_str.decode()
        return str_object

    @staticmethod
    def deserialization(str_object):
        """
        解码
        :param str_object: 编码之后的数据
        :return: 原始数据对象
        """
        bytes_str = str_object.encode()
        bytes_object = base64.b64decode(bytes_str)
        data = pickle.loads(bytes_object)
        return data
