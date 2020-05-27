from django.shortcuts import render, redirect
from django import http
from django.urls import reverse
import re, json, logging
from django.db import DatabaseError
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import View
from django.conf import settings
from django_redis import get_redis_connection

from .models import User, Address
from ..goods.models import SKU
from celery_tasks.email import tasks
from utils.response_code import RETCODE, err_msg
from utils.views import LoginRequiredJSONMixin, BaseCheckParams
from .util import SignatureToken
from .check_request_params import ADDRESS_CREATE_FIELDS, ADDRESS_FIELDS
from . import constants

# Create your views here.

logger = logging.getLogger("django")


class HistoryView(LoginRequiredJSONMixin, View):
    """用户历史浏览记录"""

    def post(self, request):
        """保存用户浏览记录"""
        # 获取参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get("sku_id")
        # 校验参数
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden("商品sku_id错误")
        # 保存数据
        redis_conn = get_redis_connection("history")
        # 1.先去重
        key = "history_%s" % request.user.id
        pl = redis_conn.pipeline()
        pl.lrem(key, 0, sku_id)
        # 2.添加
        pl.lpush(key, sku_id)
        # 3.截取
        pl.ltrim(key, 0, constants.USER_HISTORY_COUNT - 1)
        pl.execute()
        # 响应json
        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK"})

    def get(self, request):
        """获取用户浏览记录"""
        # 从redis中去除sku_id
        redis_conn = get_redis_connection("history")
        skus_id = redis_conn.lrange("history_%s" % request.user.id, 0, -1)
        # 查sku

        skus = []
        # 构造数据
        for sku_id in skus_id:
            try:
                sku = SKU.objects.get(id = sku_id)
            except Exception as e:
                logger.error(e)
                break
            skus.append({
                "id":sku.id,
                "name":sku.name,
                "price":sku.price,
                "default_image" : sku.default_image.url
            })
        # 响应json
        return http.JsonResponse({"code":RETCODE.OK,"errmsg":"OK","skus":skus})


class UpdateTitleAddressView(LoginRequiredJSONMixin, View):

    def put(self, request, address_id):
        # 更新title
        json_dict = json.loads(request.body.decode())
        title = json_dict.get("title")
        if not title:
            return http.HttpResponseForbidden("必填参数")
        try:
            Address.objects.filter(id=address_id).update(title=title)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"code": RETCODE.DBERR, "errmsg": "更新标题失败"})
        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "更新标题成功"})


class DefaultAddressView(LoginRequiredJSONMixin, View):

    def put(self, request, address_id):
        try:
            address = Address.objects.get(id=address_id)
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})


class UpdateDestroyView(LoginRequiredJSONMixin, View, BaseCheckParams):
    fields = ADDRESS_CREATE_FIELDS

    def put(self, request, address_id):
        # 更新数据
        json_dict = json.loads(request.body.decode())
        if not self.check_params(json_dict):  # 格式检查
            return http.HttpResponseForbidden(self.result_msg)

        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,  # 标题默认就是收货人
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '地址更新失败'})

            # 响应新的地址信息给前端渲染
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改地址成功', 'address': address_dict})

    def delete(self, request, address_id):
        # 删除地址
        try:
            address = Address.objects.get(id=address_id)
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址失败'})
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})


class AddressCreateView(LoginRequiredJSONMixin, View, BaseCheckParams):
    """新增收货地址"""
    fields = ADDRESS_CREATE_FIELDS  # 地址请求的参数

    def post(self, request):
        count = request.user.addresses.count()
        if count > constants.USER_ADDRESS_LIMIT_COUNT:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超出用户地址上限'})

        json_dict = json.loads(request.body.decode())
        if not self.check_params(json_dict):
            # return http.JsonResponse({"code":self.result_code,"errmsg":self.result_msg})
            return http.HttpResponseForbidden(self.result_msg)
        # 保存数据
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,  # 标题默认就是收货人
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})
        try:
            # 判断如果没有默认值设置默认值
            if not request.user.default_address_id:
                request.user.default_address_id = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})

        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应新增地址结果：需要将新增的地址返回给前端渲染
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


class AddressView(LoginRequiredMixin, View):
    fields = ADDRESS_FIELDS

    def get(self, request):
        """获取注册地址页面"""
        login_user = request.user
        try:
            addresses = Address.objects.filter(user=login_user, is_deleted=False)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('地址获取失败')

        # 将用户地址模型列表转字典列表:因为JsonResponse和Vue.js不认识模型类型，只有Django和Jinja2模板引擎认识
        address_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_list.append(address_dict)

        # 构造上下文
        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_list
        }
        return render(request, 'user_center_site.html', context)


class EmailVerificationView(View):

    def get(self, request):
        """email回调验证接口"""
        token = request.GET.get("token")
        if not token:
            return http.HttpResponseForbidden("缺少必填参数token")
        data = SignatureToken.check_token(token)
        if not data:
            return http.HttpResponseBadRequest("token已过期")

        try:
            request.user.email_active = True
            request.user.save()
        except User.DoesNotExist:
            return http.HttpResponseServerError("邮箱激活失败")

        return redirect(reverse("users:userCenterInfo"))


class EmailView(LoginRequiredJSONMixin, View):
    """判断用户是否登录"""

    def put(self, request):
        """更新email"""
        # 获取参数email
        json_str = request.body.decode()  # bytes 类型
        json_dict = json.loads(json_str)
        email = json_dict.get('email')
        # 校验参数
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')
        # 保存到数据库中
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            return http.JsonResponse({"code": RETCODE.DBERR, 'errmsg': err_msg[RETCODE.DBERR]})

        # 发送邮件
        data = {
            'userid': request.user.id,
            'email': request.user.email
        }
        try:
            token = SignatureToken.generate_token(data)
        except Exception as e:
            logger.error(e)

        verify_url = settings.EMAIL_VERIFY_URL + '?token=%s' % token
        tasks.send_verify_email.delay(email, verify_url)
        return http.JsonResponse({"code": RETCODE.OK, 'errmsg': "ok"})


class UserCenterInfoView(LoginRequiredMixin, View):

    # login_url =  判断用户重定向的位置
    # redirect_field_name = 'next' 默认，查询参数，用于登录以后重新回到原来的位置
    def get(self, request):
        """获取页面"""
        contents = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }
        return render(request, 'user_center_info.html', contents)


class LogoutView(View):

    def get(self, request):
        '''退出登录'''
        # 删除状态保持
        logout(request)
        # 删除cookie中username
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')
        return response


class LoginView(View):

    def get(self, request):
        """
        获取页面
        """
        return render(request, 'login.html')

    def post(self, request):
        # 获取参数
        username = request.POST.get("username")
        password = request.POST.get("password")
        remembered = request.POST.get("remembered")
        next = request.GET.get("next")
        # 校验参数
        if not all([username, password]):
            return http.HttpResponseForbidden("必填参数")

        if not re.match(r'\w{6,18}', username):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')

        if not re.match(r'^[a-zA-Z0-9_]{4,12}$', password):
            return http.HttpResponseForbidden('密码最少4位，最长12位')

        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {"account_errmsg": '用户名或密码错误'})

        # 状态保持
        login(request, user)
        if remembered != "on":
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)

        # 判断next存在
        if not next:
            response = redirect(reverse('contents:index'))
        else:
            response = redirect(next)
        # 生成cookie,用于用户登录之后从cookie 中取中username，显示用户名
        response.set_cookie("username", user.username)
        return response


class UsernameView(View):

    def get(self, request, username):
        """
        :param username: 用户名
        :return: Json5
        """
        count = User.objects.filter(username=username).count()
        resp_content = {'code': RETCODE.OK, 'errmsg': 'OK', 'count': count}
        return http.JsonResponse(resp_content)


class MobileView(View):

    def get(self, request, mobile):
        """
        :param mobile: 手机号
        :return: Json
        """
        count = User.objects.filter(mobile=mobile).count()
        resp_content = {'code': RETCODE.OK, 'errmsg': 'OK', 'count': count}
        return http.JsonResponse(resp_content)


class RegisterView(View):

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # 获取数据
        # b'{"username":"cjw123","password":"1234","confirmPassword":"1234","mobile":"15827343059","verifyCode":"","mobCode":"","protocol":true}'
        # print(request.body)
        userInfo = json.loads(request.body.decode())
        username = userInfo["username"]
        password = userInfo["password"]
        confirmPassword = userInfo["confirmPassword"]
        mobile = userInfo["mobile"]
        protocol = userInfo["protocol"]

        if not all([username, password, confirmPassword, mobile]):
            return http.JsonResponse({"errmsg": "参数必填", "code": 4004})

        if not re.match(r'\w{6,18}', username):
            return http.JsonResponse({"errmsg": "用户名必填", "code": 4004})

        if not re.match(r'^[a-zA-Z0-9_]{4,12}$', password):
            return http.JsonResponse({"errmsg": "密码必填", "code": 4004})

        if confirmPassword != password:
            return http.JsonResponse({"errmsg": "两次密码不一致", "code": 4004})

        if not re.match(r'^1[34578]\d{9}$', mobile):
            return http.JsonResponse({"errmsg": "手机号有误", "code": 4004})

        if protocol != '1':
            return http.JsonResponse({"errmsg": "请勾选协议", "code": 4004})

        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return http.JsonResponse({"errmsg": "用户注册失败", "code": 4004})

        # 状态保持
        login(request, user)

        # 重定向首页
        response = redirect(reverse('contents:index'))
        response.set_cookie("username", user.username)
        return response

