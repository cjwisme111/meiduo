from django.shortcuts import render
from django.views import View
from django import http
from django_redis import get_redis_connection
import json

from ..goods.models import SKU
from utils.response_code import RETCODE
from .utils import SerializationBase64


class CartsSimpleView(View):
    """获取购物车商品数量统计"""

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection("carts")
            redis_carts = redis_conn.hgetall("carts_%s" % user.id)
            skus = SKU.objects.filter(id__in=redis_carts.keys())

        else:
            pass


class CartsSelectionView(View):
    """购物车全选"""

    def put(self, request):
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get("selected")

        if not isinstance(selected, bool):
            return http.HttpResponseForbidden("selected 错误")

        user = request.user
        if user.is_authenticated:
            # 修改redis
            redis_conn = get_redis_connection("carts")
            redis_sku_id_list = redis_conn.hkeys("carts_%s" % user.id)
            if selected:
                redis_conn.sadd("selected_%s" % user.id, *redis_sku_id_list)
            else:
                redis_conn.srem("selected_%s" % user.id, *redis_sku_id_list)
            return http.JsonResponse({"code":RETCODE.OK,"errmsg":"OK"})
        else:
            # 修改cookie
            cookie_carts = request.COOKIES.get("carts")
            response = http.JsonResponse({"code": "OK", "errmsg": "OK"})
            if cookie_carts:
                carts_dict = SerializationBase64.deserialization(cookie_carts)
                for v in carts_dict.values():
                    v["selected"] = selected
                cookie_carts = SerializationBase64.serialized(carts_dict)
                response.set_cookie("carts",cookie_carts)
            return response


class CartsView(View):
    """购物车管理"""

    def post(self, request):
        """存储购物车数据"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get("sku_id")
        count = json_dict.get("count")
        selected = json_dict.get("selected", True)

        # 校验参数
        if not all([sku_id, count]):
            return http.HttpResponseForbidden("缺少必填参数")

        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden("sku_id错误")

        try:
            count = int(count)
        except Exception as e:
            return http.HttpResponseForbidden("count 错误")

        if not isinstance(selected, bool):
            return http.HttpResponseForbidden("selected 错误")

        # if not isinstance(count,int):
        #     return http.HttpResponseForbidden("count 错误")

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 保存数据到redis
            redis_conn = get_redis_connection("carts")
            pl = redis_conn.pipeline()
            key = "carts_%s" % user.id
            # 保存个数
            pl.hincrby(key, sku_id, count)
            # 勾选
            if selected:
                pl.sadd("selected_%s" % user.id, sku_id)
            pl.execute()
            return http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK"})
        else:
            # 保存cookie
            carts_str = request.COOKIES.get("carts")
            # 判断
            if carts_str:
                carts = SerializationBase64.deserialization(carts_str)
            else:
                carts = {}
            carts[sku_id] = {
                "count": count,
                "selected": selected
            }
            carts_str = SerializationBase64.serialized(carts)
            response = http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK"})
            response.set_cookie("carts", carts_str)
            return response

    def get(self, request):
        """展示购物车"""
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 取redis中数据
            redis_conn = get_redis_connection("carts")
            # pl = redis_conn.pipeline()
            redis_carts = redis_conn.hgetall("carts_%s" % user.id)
            redis_selected = redis_conn.smembers("selected_%s" % user.id)
            cart_dict = {}
            for sku_id, count in redis_carts.items():
                cart_dict[int(sku_id)] = {
                    "count": int(count),
                    "selected": str(sku_id in redis_selected)
                }
            pass
        else:
            # 取cookie中数据
            carts_str = request.COOKIES.get("carts")
            if carts_str:
                cart_dict = SerializationBase64.deserialization(carts_str)
            else:
                cart_dict = {}
        carts = []
        if cart_dict:
            skus = SKU.objects.filter(id__in=cart_dict.keys())
            for sku in skus:
                carts.append({
                    'id': sku.id,
                    'count': cart_dict.get(sku.id).get('count'),
                    'selected': str(cart_dict.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
                    'name': sku.name,
                    'default_image_url': sku.default_image.url,
                    'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析
                    'amount': str(sku.price * cart_dict.get(sku.id).get('count'))
                })
        context = {
            "cart_skus": carts
        }
        return render(request, "cart.html", context)

    def put(self, request):
        """更新购物车商品个数"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get("sku_id")
        count = json_dict.get("count")
        selected = json_dict.get("selected", True)

        # 校验参数
        if not all([sku_id, count]):
            return http.HttpResponseForbidden("缺少必填参数")

        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden("sku_id错误")

        try:
            count = int(count)
        except Exception as e:
            return http.HttpResponseForbidden("count 错误")

        if not isinstance(selected, bool):
            return http.HttpResponseForbidden("selected 错误")

        user = request.user
        # 检查用户是否登录
        if user.is_authenticated:
            redis_conn = get_redis_connection("carts")
            pl = redis_conn.pipeline()
            pl.hset("carts_%s" % user.id, sku_id, count)
            if selected:
                pl.sadd("selected_%s" % user.id, sku_id)
            else:
                pl.srem("selected_%s" % user.id, sku_id)
            pl.execute()
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'price': sku.price,
                'amount': sku.price * count,
                'default_image_url': sku.default_image.url
            }
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})

        else:
            str_carts = request.COOKIES.get("carts")
            if not str_carts:
                return http.HttpResponseForbidden("修改购物车失败")
            carts_dict = SerializationBase64.deserialization(str_carts)
            if sku_id not in carts_dict:
                return http.HttpResponseForbidden("sku_id 错误")
            carts_dict[sku_id]["count"] = count
            carts_dict[sku_id]["selected"] = selected

            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'price': sku.price,
                'amount': sku.price * count,
                'default_image_url': sku.default_image.url
            }
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
            response.set_cookie("carts", SerializationBase64.serialized(carts_dict))
            return response

    def delete(self, request):
        """删除sku"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get("sku_id")
        user = request.user
        if user.is_authenticated:
            # 保存数据到redis
            redis_conn = get_redis_connection("carts")
            pl = redis_conn.pipeline()
            if pl.hexists("carts_%s" % user.id, sku_id):
                pl.hdel("carts_%s" % user.id, sku_id)
            pl.srem("selected_%s" % user.id, sku_id)
            return http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK"})
        else:
            # 保存cookie
            carts_str = request.COOKIES.get("carts")
            response = http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK"})
            if carts_str:
                carts = SerializationBase64.deserialization(carts_str)
                if sku_id in carts:  # 判断sku_id是否存在
                    del carts[sku_id]
                carts_str = SerializationBase64.serialized(carts)
                response.set_cookie("carts", carts_str)
            return response
