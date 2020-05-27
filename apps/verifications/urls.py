# -*- coding: utf-8 -*-
from django.urls import path,re_path
from . import views

urlpatterns = [
    re_path("image_codes/(?P<uuid>[\w-]+)/",views.ImageCodeView.as_view()),
    re_path("sms_codes/(?P<mobile>1[3-9]\d{9})/",views.SmsCodeView.as_view()),
]