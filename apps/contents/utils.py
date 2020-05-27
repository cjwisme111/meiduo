# -*- coding: utf-8 -*-
from collections import OrderedDict

from ..goods.models import GoodsChannel


def get_categories():
    """构造三级联动的商品分类"""
    channels = GoodsChannel.objects.order_by("group_id", "sequence")  # 排序
    categories = OrderedDict()
    for channel in channels:
        if channel.group_id not in categories:
            # 初始化 数据结构
            categories[channel.group_id] = {
                "channels": [],  # 一级频道
                "sub_cats": []  # 二级频道
            }
        cat1 = channel.category
        categories[channel.group_id]["channels"].append({
            "id": cat1.id,
            "name": cat1.name,
            "url": channel.url
        })
        # 商品频道组与商品分类是一对一关系
        cat2_list = channel.category.subs.all()  # 获取商品分类一级，一对多，获取多个商品分类
        for cat2 in cat2_list:  # 遍历二级分类，获取三级
            cat3 = cat2.subs.all()  # 三级频道
            cat2.sub_cats = cat3
            categories[channel.group_id]["sub_cats"].append(cat2)

    return categories