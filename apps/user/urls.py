# -*- coding: utf-8 -*-
from django.urls import path,re_path
from . import views


app_name = 'users'
urlpatterns = [
    # 登录
    path('login/', views.LoginView.as_view(),name='login'),

    path('register/',views.RegisterView.as_view(),name='register'),
    re_path('username/(?P<username>[a-zA-Z0-9]{6,18})/count/',views.UsernameView.as_view()),
    re_path('mobile/(?P<mobile>1[34578]\d{9})/count/',views.MobileView.as_view()),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('user_center_info/', views.UserCenterInfoView.as_view(), name='userCenterInfo'),

    # 保存email
    path('emails/', views.EmailView.as_view()),
    # email 验证
    path('emails/verification/', views.EmailVerificationView.as_view()),
    # 用户收货地址
    path('addresses/', views.AddressView.as_view(), name='address'),
    # 新增收货地址
    path('addresses/create/', views.AddressCreateView.as_view()),
    # 编辑地址
    re_path(r"^addresses/(?P<address_id>\d+)/$",views.UpdateDestroyView.as_view()),
    # 设置默认值
    re_path(r"^addresses/(?P<address_id>\d+)/default/$",views.DefaultAddressView.as_view()),
    # 修改地址标题
    re_path(r"^addresses/(?P<address_id>\d+)/title/$",views.UpdateTitleAddressView.as_view()),
    # 用户浏览历史记录
    path("browse_histories/",views.HistoryView.as_view())
]
