# -*- coding: utf-8 -*-
from django.urls import path

from . import views
urlpatterns = [
    path('qq/login/',views.QQLoginView.as_view()),
    path('oauth_callback/',views.QQLoginCallBackView.as_view()),
]