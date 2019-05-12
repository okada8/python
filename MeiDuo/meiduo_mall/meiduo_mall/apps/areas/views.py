from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin#使用缓存，减少数据库交互
from .models import Area
from . import serializers
# Create your views here.

#城市区域信息
class AreasViewSet(CacheResponseMixin,ReadOnlyModelViewSet):
    """
    list:返回所有省份
    retrieve:返回特定省的下属
    """
    #取消分页，返回列表的时候不需要分页的
    pagination_class = None

    #指明数据范围分省和市区
    # queryset = Area.objects.all()
    def get_queryset(self):
        #省
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
        #市
            return Area.objects.all()
    #重写获取序列化器的函数，区别到底是获取省份的序列化器还是获取市区的序列化器
    def get_serializer_class(self):
        if self.action == 'list':
            #省的序列化器
            return serializers.AreaSerializer
        else:
            #市的序列化器
            return serializers.SubAreaSerializer










