# -*- coding: utf-8 -*-
from django.urls import path,re_path

from . import views

app_name = 'goods'
urlpatterns = [
    re_path("^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$",views.GoodsListView.as_view(),name="list"),
    # 热销
    re_path("^hot/(?P<category_id>\d+)/$",views.HotGoodsView.as_view()),
    # 详情
    re_path("^detail/(?P<sku_id>\d+)/$",views.DetailGoodsView.as_view(),name="detail"),
    # 统计分类商品访问量
    re_path("^detail/visit/(?P<category_id>\d+)/$", views.DetailVisitView.as_view()),

]
