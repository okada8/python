from rest_framework import serializers
from .models import OAuthQQUser
from django_redis import get_redis_connection
from users.models import User

#qq登陆用户的序列化器
class OAuthQQUserSerializer(serializers.Serializer):
    access_token=serializers.CharField(label='操作凭证')
    mobile=serializers.RegexField(label='手机号',regex=r'^1[3-9]\d{9}$')
    password=serializers.CharField(label='密码',max_length=20,min_length=8)
    sms_code=serializers.CharField(label='短信验证码')
    #用户用qq登陆
    def validate(self, attrs):
        #验证token
        access_token=attrs['access_token']
        openid=OAuthQQUser.check_save_user_token(access_token)
        #判断openid
        if openid is None:
            raise serializers.ValidationError('无效的access_token')
        attrs['openid']=openid
        #校验短信验证码
        mobile=attrs['mobile']
        sms_code=attrs['sms_code']
        redis_conn=get_redis_connection('verify_codes')
        relay_sms_code=redis_conn.get('sms_%s'%mobile)
        if relay_sms_code.decode() !=sms_code:
            raise serializers.ValidationError('短信验证码错误')
        #判断用户是否存在，检查密码
        try:
            user=User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            #如果用户不存在，会走return attrs
            pass
        else:
            password=attrs['password']
            if not user.check_password(password):
                raise serializers.ValidationError('密码错误')
            attrs['user']=user
        return attrs

    #创建用户
    def create(self, validated_data):#validated_data就是上面的attrs，
        user=validated_data.get('user')
        #如果用户不存在
        if not user:
            user=User.objects.create_user(
                username=validated_data['mobile'],
                password=validated_data['password'],
                mobile=validated_data['mobile']
            )
        #保存用户和qq的对应关系，如果没有user，上面已经创建好了，如果有，会直接走下面
        OAuthQQUser.objects.create(
            openid=validated_data['openid'],
            user=user
        )
        return user















