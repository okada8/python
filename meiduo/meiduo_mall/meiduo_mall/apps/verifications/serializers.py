from rest_framework import serializers
from django_redis import get_redis_connection
from redis.exceptions import RedisError
import logging

logger=logging.getLogger('django')

class CheckImageCodeSerialzier(serializers.Serializer):
    """图片验证码校验序列化器"""
    #验证是不是uuid类型
    image_code_id=serializers.UUIDField()
    #验证是不是四位
    text=serializers.CharField(min_length=4,max_length=4)

    def validate(self, attrs):
        """校验图片验证码是否正确"""
        #查询redis，获取真实验证码
        #从attrs字典中拿到图片验证码id
        image_code_id=attrs.get("image_code_id")
        #从attrs字典中拿到图片验证码的值
        text=attrs.get("text")
        #获取图片验证码redis连接
        redis_conn=get_redis_connection("verify_codes")
        #拿到redis中对应的真实验证码文本
        image_code_text=redis_conn.get("img_%s"%image_code_id)
        #如果没拿到，会返回NONE
        if image_code_text is None:
            #过期或不存在
            raise serializers.ValidationError('无效的图片验证码')
        #删除redis中个图片验证码，防止用户对同一个进行多次请求
        try:
            redis_conn.delete("img_%s"%image_code_id)
        except RedisError as e:
            logger.error(e)
        #对比
        #拿到的文本是bytes类型
        real_text=image_code_text.decode()
        #将真实文本信息和输入的文本信息小写
        if real_text.lower() != text.lower():
            raise serializers.ValidationError('图片验证码错误')
        #redis中发送短信验证码的标志 send_flag_<mobile>:1,由redis维护60妙
        #该字段从对应视图函数中获取
        mobile=self.context.get('view').kwargs.get('mobile')
        #查看redis中是否有发送过短信的标志
        send_flag=redis_conn.get('send_flag_%s'%mobile)
        if send_flag:
            raise serializers.ValidationError('发送短信过于频繁')
        return attrs