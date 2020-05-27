"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include,re_path


urlpatterns = [
    path('admin/', admin.site.urls),
    # 用户模块
    path("",include('apps.user.urls',namespace='users')),
    # 内容模块
    path("",include('apps.contents.urls',namespace='contents')),
    # 验证模块
    path("",include('apps.verifications.urls')),
    # 第三方登录
    path("", include('apps.oauth.urls')),
    # 区域
    path("", include('apps.areas.urls')),
    # 商品
    path("", include('apps.goods.urls',namespace="goods")),
    # 搜索引擎
    re_path(r'^search/', include('haystack.urls')),
    # 购物车管理
    path("",include("apps.carts.urls",namespace="carts")),
]
