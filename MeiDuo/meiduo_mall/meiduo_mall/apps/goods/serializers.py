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
        fields = ('text', 'object')
