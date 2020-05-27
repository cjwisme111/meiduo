# -*- coding: utf-8 -*-
from django.utils.deprecation import MiddlewareMixin
class corsMiddleware(MiddlewareMixin):

    def process_reponse(self, request, reponse):
        if request.method == "OPTIONS":  # 如果操作的是删除指令这里在这里判断下面 return 返回
            reponse["Access-Control-Allow-methods"] = "DELETE"

        reponse["Access-Control-Allow-Origin"] = "*"
        reponse["Access-Control-Allow-Headers"] = "Content-Type"
        return reponse