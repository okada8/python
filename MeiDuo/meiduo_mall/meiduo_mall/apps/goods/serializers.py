from .models import SKU
from rest_framework import serializers
from drf_haystack.serializers import HaystackSerializer
from .search_indexes import SKUIndex





class SKUSerializers(serializers.ModelSerializer):
    """SKU序列化器"""
    class Meta:
        model=SKU
        fields=('id','name','price','default_image_url','comments')



class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    object = SKUSerializers(read_only=True)

    class Meta:
        index_classes = [SKUIndex]
        #前端传入的参数text，并且检索出数据后再使用这个序列化器返回给前端；
        #object字段是用来向前端返回数据时序列化的字段
        fields = ('text', 'object')
