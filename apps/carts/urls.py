# -*- coding: utf-8 -*-
from django.urls import path

from . import views

app_name ="carts"
urlpatterns = [
    path("carts/",views.CartsView.as_view(),name="info"),
    # 获取购物车数量
    path("carts/simple/", views.CartsSimpleView.as_view()),
    # 购物车全选
    path("carts/selection/", views.CartsSelectionView.as_view()),
]