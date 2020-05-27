# -*- coding: utf-8 -*-

def get_breadcrumb(category):
    #判断是那个级别分类
    breadcrumb = {}
    if category.parent == None:
        # 一级类别
        breadcrumb["cat1"] = category
    elif category.subs.count() == 0:
        # 三级类别
        cat2 = category.parent
        breadcrumb["cat1"] = cat2.parent
        breadcrumb["cat2"] = cat2
        breadcrumb["cat3"] = category
    else:
        # 二级类别
        breadcrumb["cat1"] = category.parent
        breadcrumb["cat2"] = category
    return breadcrumb