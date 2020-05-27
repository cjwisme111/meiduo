# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django import http
from utils.response_code import RETCODE, err_msg
import re

from utils.response_code import RETCODE, err_msg


class LoginRequiredJSONMixin(LoginRequiredMixin):

    def handle_no_permission(self):
        """用户没有登录，返回json数据"""
        return http.JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': err_msg.get(RETCODE.SESSIONERR)})


class BaseCheckParams:
    fields = None
    result_code = None
    result_msg = None

    def check_params(self, request_params):
        if self.fields is None:
            raise Exception("缺少fields参数")

        for i in range(len(self.fields)):
            if self.fields[i][1]:
                # 必填参数的验证，1.判断是否存在，2.值不能为空
                if (self.fields[i][0] not in request_params) or (not request_params[self.fields[i][0]]):
                    self.result_code = RETCODE.NECESSARYPARAMERR
                    self.result_msg = err_msg.get(RETCODE.NECESSARYPARAMERR) + self.fields[i][0]
                    return False

            if self.fields[i][0] in request_params:
                # 判断是否是固定长度
                value = request_params[self.fields[i][0]]
                value = str(value) if isinstance(value,int) else value

                if (self.fields[i][2] and len(value) != self.fields[i][3]) \
                        or ((not self.fields[i][2]) and len(value) > self.fields[i][3]):
                    self.result_code = RETCODE.VALUELENERR
                    self.result_msg = err_msg.get(RETCODE.VALUELENERR) + self.fields[i][0]
                    return False
                if self.fields[i][4]:
                    # 判断是否在范围内
                    if isinstance(self.fields[i][4], list):
                        # 判断多个值
                        if request_params[self.fields[i][0]] not in self.fields[i][4]:
                            self.result_code = RETCODE.VALUENOTINRANGEERR
                            self.result_msg = err_msg.get(RETCODE.VALUELENERR) + ",".join(self.fields[i][0])
                            return False
                    else:
                        if request_params[self.fields[i][0]] != self.fields[i][4]:
                            self.result_code = RETCODE.FIXVALUEERR
                            self.result_msg = err_msg.get(RETCODE.VALUELENERR) + self.fields[i][0]
                            return False
                elif self.fields[i][5]:
                    # 正则判断
                    if not request_params[self.fields[i][0]] and not self.fields[i][1]:
                        regexp = re.compile('')
                    else:
                        regexp = re.compile(self.fields[i][5])

                    if not regexp.match(request_params[self.fields[i][0]]):
                        self.result_code = RETCODE.VALUEERR
                        self.result_msg = err_msg.get(RETCODE.VALUEERR) + self.fields[i][0]
                        return False
        return True
