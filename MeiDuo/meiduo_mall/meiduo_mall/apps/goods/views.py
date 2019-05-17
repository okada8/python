from django.shortcuts import render
from rest_framework.generics import ListAPIView
from .serializers import SKUSerializers
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin
from rest_framework.filters import  OrderingFilter
from .models import SKU
from .serializers import SKUIndexSerializer
from drf_haystack.viewsets import HaystackViewSet
# Create your views here.



#热销商品排行,返回热销数据
class HotSKUListView(ListCacheResponseMixin,ListAPIView):
    #使用哪个序列化器
    serializer_class = SKUSerializers
    pagination_class = None
    #指定数据范围 返回什么样的数据
    def get_queryset(self):
        #拿到路径中的category_id
        category_id=self.kwargs.get("category_id")
        return SKU.objects.filter(category_id=category_id,is_launched=True).order_by('-sales')[:2]


#通过类别获取商品列表数据
class SKUListView(ListAPIView):
    # 指明序列化器
    serializer_class = SKUSerializers
    # 排序，按照什么排序，默认价格人气关键字'create_time', 'price', 'sales'
    filter_backends = [OrderingFilter]
    ordering_fields = ('create_time', 'price', 'sales')


    #指明操作数据集和
    # queryset = SKU.objects.all()
    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        return SKU.objects.filter(category_id=category_id, is_launched=True)





class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer
















