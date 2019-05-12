from rest_framework import serializers
from .models import Area

#行政区域信息
class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model=Area
        fields=('id','name')


class SubAreaSerializer(serializers.ModelSerializer):
    """
    子行政区划信息序列化器
    """
    subs = AreaSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ('id', 'name', 'subs')