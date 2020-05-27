from django.shortcuts import render, redirect
from django.views import View
from django import http
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
import logging, re
from django.contrib.auth import login
from django_redis import get_redis_connection

from .models import QQUser
from apps.user.models import User
from utils.response_code import RETCODE
from .utils import SignAccessToken
# Create your views here.

logger = logging.getLogger('django')


class QQLoginCallBackView(View):

    def get(self, request):
        # 获取code
        code = request.GET.get('code')
        next = request.GET.get("state")
        if not code:
            return http.HttpResponseForbidden('获取code失败')

        # 创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        try:
            # 使用code获取access_token
            access_token = oauth.get_access_token(code)

            # 使用access_token获取openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('OAuth2.0认证失败')

        # 使用openid判断该QQ用户是否绑定过美多商城的用户
        try:
            qq_user = QQUser.objects.get(openid=openid)
        except QQUser.DoesNotExist:
            # 用户不存在,展示用户注册信息
            data = {
                "openid":openid
            }
            try:
                token = SignAccessToken.generate_token(data)
            except Exception as e:
                logger.error(e)
            content = {
                'access_token_openid': token
            }
            return render(request, 'oauth_callback.html', content)
        else:
            login(request, qq_user.user)
            response = redirect(next)
            response.set_cookie('username', qq_user.user.username)
            return response

    def post(self, request):
        """实现qq用户绑定"""
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        sms_code = request.POST.get("sms_code")
        access_token_openid = request.POST.get("access_token_openid")

        if not all([mobile, password, sms_code]):
            return http.HttpResponseForbidden("必填参数")

        if not re.match(r'1[3-9]\d{9}', mobile):
            return http.HttpResponseForbidden("手机号格式有误")

        if not re.match(r'[a-zA-Z0-9_-]{4,12}',password):
            return http.HttpResponseForbidden("请输入8-20位的密码")

        redis_conn = get_redis_connection('image_code')
        sms_code_server = redis_conn.get("sms_%s" % mobile)
        # 验证短信验证码
        if not sms_code:
            return render(request,'oauth_callback.html',{"sms_code_errmsg":"短信验证码已过期"})
        if sms_code_server.decode() != sms_code:
            return render(request,'oauth_callback.html',{"sms_code_errmsg":"短信验证码输入有误"})

        data = SignAccessToken.check_token(access_token_openid)
        if not data:
            return render(request,'oauth_callback.html',{"openid_errmsg":"openid 已过期"})
        # 验证手机号是否存在
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 用户不存在，注册用户
            try:
                user = User.objects.create_user(username=mobile,password=password,mobile=mobile)
            except Exception as e:
                return render(request,'oauth_callback.html',{"qq_login_errmsg":"qq登录失败"})
        else:
            # 用户已存在
            if not user.check_password(password):
                return render(request,'oauth_callback.html',{"account_errmsg":"账号或者密码错误"})

        # 注册qquser
        try:
            qq_user = QQUser.objects.create(user=user,openid=data.get("openid"))
        except Exception as e:
            return render(request,'oauth_callback.html',{"qq_login_errmsg":"qq登录失败"})

        # 状态保持
        login(request,qq_user.user)
        next = request.GET.get("state")
        response = redirect(next)
        response.set_cookie('username',user.username)
        return response


class QQLoginView(View):

    def get(self, request):
        """提供QQ登录扫码页面"""

        # 接收next
        next = request.GET.get('next')

        # 创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)

        # 生成QQ登录扫码链接地址
        login_url = oauth.get_qq_url()

        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})
