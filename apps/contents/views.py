from django.shortcuts import render
from django.views import View

from .models import Content,ContentCategory
from .utils import get_categories
# Create your views here.


class IndexView(View):

    def get(self,request):
        """首页"""

        # 获取三级联动商品
        categories = get_categories()
        # 获取广告内容
        # 1.获取所有广场类别
        c_categories = ContentCategory.objects.all()
        contents_group = {}
        for cate in c_categories:
            #contents = cate.content_set.all() # 获取所有
            contents = cate.content_set.filter(status=True).order_by("sequence")
            contents_group[cate.key] = contents

        context ={
            "categories":categories,
            "contents" : contents_group
        }
        return  render(request,'index.html',context)

