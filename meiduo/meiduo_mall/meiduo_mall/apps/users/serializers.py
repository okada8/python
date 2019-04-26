import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from users.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    """创建用户序列化器类"""
    password2 = serializers.CharField(label='重复密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='是否同意协议', write_only=True)
    token = serializers.CharField(label='JWT Token', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'mobile', 'password2', 'sms_code', 'allow', 'token')

        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    # (参数完整性，手机号格式，手机号是否已注册，是否同意协议，两次密码是否一致，短信验证码是否正确)
    def validate_username(self, value):
        """用户名不能是纯数字"""
        if re.match(r'^\d+$', value):
            raise serializers.ValidationError('用户名不能都是数字')

        return value

    def validate_mobile(self, value):
        """手机号格式，手机号是否已注册"""
        # 手机号格式
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式不正确')

        # 手机号是否已注册
        count = User.objects.filter(mobile=value).count()
        if count > 0:
            raise serializers.ValidationError('手机号已存在')

        return value

    def validate_allow(self, value):
        """是否同意协议"""
        if value != 'true':
            raise serializers.ValidationError('请同意协议')
        return value

    def validate(self, attrs):
        """两次密码是否一致，短信验证码是否正确"""
        # 两次密码是否一致
        password = attrs['password']
        password2 = attrs['password2']

        if password != password2:
            raise serializers.ValidationError('两次密码不一致')

        # 短信验证码是否正确
        # 获取真实的短信验证码内容
        mobile = attrs['mobile']
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile) # bytes

        if not real_sms_code:
            raise serializers.ValidationError('短信验证码已过期')

        # 对比
        sms_code = attrs['sms_code'] # str
        real_sms_code = real_sms_code.decode() # str
        if sms_code != real_sms_code:
            raise serializers.ValidationError('短信验证码错误')

        return attrs

    def create(self, validated_data):
        """保存注册用户信息"""
        # 清除无用的数据
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # # 调用父类create方法
        user = super().create(validated_data)
        #
        # # 对密码进行加密
        password = validated_data['password']
        user.set_password(password)
        user.save()

        # 调用create_user方法
        # user = User.objects.create_user(**validated_data)

        # 注册成功就让用户处于登录状态
        # 由服务器签发一个jwt token，保存用户身份信息


        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        # 生成载荷信息(payload)
        payload = jwt_payload_handler(user)
        # 生成jwt token
        token = jwt_encode_handler(payload)

        # 给user对象增加一个属性token，保存jwt token信息
        user.token = token

        # 返回user
        return user
