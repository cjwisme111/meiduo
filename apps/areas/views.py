from django.shortcuts import render
from django import http
from django.core.cache import cache
from django.views import View
import logging

from .models import Areas
from utils.response_code import RETCODE, err_msg
from .contants import  AREA_CACHE_EXPIRY

# Create your views here.

logger = logging.getLogger("django")


class AreasView(View):
    """省市区三级联动"""

    def get(self, request):
        area_id = request.GET.get("area_id")
        if not area_id:
            # 没有设置缓存，第一次取值
            province_list = cache.get("province_list")
            if not province_list:
                # 查询省级
                try:
                    # 查数据库
                    province_model_lists = Areas.objects.filter(parent__isnull=True)
                except Exception as e:
                    logger.error(e)
                    return http.HttpResponseServerError("省市区没有找到")
                province_list = []
                for province_model in province_model_lists:
                    province_dict = {
                        "id": province_model.id,
                        "name": province_model.name
                    }
                    province_list.append(province_dict)
                # 存到缓存中
                cache.set("province_list", province_list, AREA_CACHE_EXPIRY)
            return http.JsonResponse(
                {"code": RETCODE.OK, "errmsg": err_msg[RETCODE.OK], 'province_list': province_list})
        else:
            # 市区
            sub_data = cache.get("sub_%s" % area_id)
            if not sub_data:
                try:
                    # 查数据库
                    parent_model = Areas.objects.get(id=area_id)
                    sub_model_list = parent_model.subs.all()
                except Exception as e:
                    logger.error(e)
                    return http.HttpResponseServerError("省市区没有找到")
                subs = []
                for sub_model in sub_model_list:
                    sub_dict = {
                        "id": sub_model.id,
                        "name": sub_model.name
                    }
                    subs.append(sub_dict)

                # 构造子级JSON数据
                sub_data = {
                    'id': parent_model.id,
                    'name': parent_model.name,
                    'subs': subs
                }

                # 缓存城市或者区县
                cache.set('sub_' + area_id, sub_data, AREA_CACHE_EXPIRY)
            # 响应城市或区县JSON数据
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})