from django.shortcuts import render
from django.views import View
from django import http
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import logging
from django.utils import timezone

from .models import GoodsCategory, SKU,GoodsVisitCount
from ..contents.utils import get_categories
from .utils import get_breadcrumb
from . import constants
from utils.response_code import RETCODE

# Create your views here.

logger = logging.getLogger("django")


class DetailVisitView(View):
    """统计商品分类"""

    def post(self,request,category_id):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden("商品类别不存在")
        try:
            today_date = timezone.localdate()
            # counts_data = category.goodsvisitcount_set.filter(date=today_date)[0]
            counts_data = GoodsVisitCount.objects.get(category_id=category_id,date=today_date)  # 查询当天的日期
        except GoodsVisitCount.DoesNotExist:
            # 当天记录不存在
            counts_data = GoodsVisitCount()
        counts_data.counts += 1
        counts_data.date = today_date
        counts_data.category = category
        try:
            counts_data.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden("统计失败")
        return http.HttpResponse("统计成功")


class DetailGoodsView(View):
    """详情页"""

    def get(self, request, sku_id):
        """获取详情页面"""
        try:
            sku = SKU.objects.select_related("category").get(id=sku_id)
            # sku = SKU.objects.get(id=sku_id)
        except Exception:
            # return http.HttpResponseNotFound("商品不存在")
            return render(request, "404.html")

        # 获取商品分类
        categories = get_categories()
        # 面包屑
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        context = {
            "categories": categories,
            "breadcrumb": breadcrumb,
            "category_id": sku.category.id,
            "sku": sku,
            "specs":goods_specs,
        }
        return render(request, "detail_org.html", context)


class HotGoodsView(View):
    """热销商品"""

    def get(self, request, category_id):
        # 获取参数，校验参数
        # 获取数据
        skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by("-sales")[:2]
        # 拼接数据
        # 响应json数据
        hot_skus = []
        for sku in skus:
            sku_dict = {
                "id": sku.id,
                "name": sku.name,
                "price": sku.price,
                "image": sku.default_image.url,
            }
            hot_skus.append(sku_dict)

        context = {
            "code": RETCODE.OK,
            "errmsg": "ok",
            "hot_skus": hot_skus
        }
        return http.JsonResponse(context)


class GoodsListView(View):
    """列表页"""

    def get(self, request, category_id, page_num):
        """获取列表页的资源"""
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden("商品不存在")
        sort = request.GET.get("sort", 'default')
        if sort == 'price':
            sort_field = 'price'  # 按照价格排序
        elif sort == "hot":
            sort_field = '-sales'  # 按照销量倒序
        else:
            sort = "default"
            sort_field = 'create_time'

        # 商品分类
        categories = get_categories()
        # 面包屑
        breadcrumb = get_breadcrumb(category)
        # 分页，查出所有的sku数据
        skus = category.sku_set.filter(is_launched=True).order_by(sort_field)
        paginator = Paginator(skus, constants.PER_PAGE_COUNT)
        try:
            current_page_sku = paginator.get_page(page_num)
        except (PageNotAnInteger, EmptyPage) as e:
            logger.error(e)
            return http.HttpResponseForbidden("分页错误")
        total = paginator.num_pages  # 总的记录
        context = {
            "category": category,
            "categories": categories,
            "breadcrumb": breadcrumb,
            "skus": current_page_sku,
            "total": total,
            "current_page": page_num,
            "sort": sort
        }
        return render(request, 'list.html', context)
