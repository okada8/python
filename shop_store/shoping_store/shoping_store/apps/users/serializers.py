import re
from django.conf import settings
from django.core.mail import send_mail

from django_redis import get_redis_connection
from rest_framework import serializers

from users.models import User
from users import constants
# from goods.models import SKU


# class UserAddBrowseHistorySerializer(serializers.Serializer):
#     """历史浏览添加序列化器"""
#     sku_id = serializers.IntegerField(label='商品SKU编号', min_value=1)
#
#     def validate_sku_id(self, value):
#         """sku_id对应的商品是否存在"""
#         try:
#             sku = SKU.objects.get(id=value)
#         except SKU.DoesNotExist:
#             raise serializers.ValidationError('商品不存在')
#
#         return value
#
#     def create(self, validated_data):
#         """在redis中保存用户浏览的记录"""
#         # 获取登录用户user
#         user = self.context['request'].user
#
#         # 获取redis链接
#         redis_conn = get_redis_connection('history')
#         history_key = 'history_%s' % user.id
#
#         # 创建redis管道对象
#         pl = redis_conn.pipeline()
#
#         # 去重：如果用户已经浏览过该商品，先将商品id从列表中移除。
#         sku_id = validated_data['sku_id']
#         # lrem(key, count, value): 如果value存在直接移除，不存在就忽略
#         pl.lrem(history_key, 0, sku_id)
#
#         # 左侧加入: 保持浏览顺序
#         # lpush(key, *values): 向列表左侧加入元素
#         pl.lpush(history_key, sku_id)
#
#         # 截取: 只保留最近几条浏览记录。
#         # ltrim(key, start, end): 截取列表元素，只保留指定区间内的元素
#         pl.ltrim(history_key, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT-1)
#
#         # 执行管道命令
#         pl.execute()
#
#         # 返回
#         return validated_data


# class UserAddressSerializer(serializers.ModelSerializer):
#     """
#     用户地址序列化器
#     """
#     province = serializers.StringRelatedField(read_only=True)
#     city = serializers.StringRelatedField(read_only=True)
#     district = serializers.StringRelatedField(read_only=True)
#     province_id = serializers.IntegerField(label='省ID', required=True)
#     city_id = serializers.IntegerField(label='市ID', required=True)
#     district_id = serializers.IntegerField(label='区ID', required=True)
#
#     class Meta:
#         model = Address
#         exclude = ('user', 'is_deleted', 'create_time', 'update_time')
#
#     def validate_mobile(self, value):
#         """
#         验证手机号
#         """
#         if not re.match(r'^1[3-9]\d{9}$', value):
#             raise serializers.ValidationError('手机号格式错误')
#         return value
#
#     def create(self, validated_data):
#         """
#         保存
#         """
#         validated_data['user'] = self.context['request'].user
#         return super().create(validated_data)


# class AddressTitleSerializer(serializers.ModelSerializer):
#     """
#     地址标题
#     """
#     class Meta:
#         model = Address
#         fields = ('title',)


class EmailSerializer(serializers.ModelSerializer):
    """用户邮箱序列化器"""
    class Meta:
        model = User
        fields = ('id', 'email')
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    # def update(self, instance, validated_data):
    #     """设置用户邮箱，给用户邮箱发送激活邮件"""
    #     # 设置用户邮箱
    #     email = validated_data['email']
    #     instance.email = email
    #     instance.save()
    #
    #     # 给用户邮箱发送激活邮件
    #     # 激活邮件中需要包含激活链接：
    #     # http://www.meiduo.site:8080/success_verify_email.html?user_id=<user_id>
    #     # 为了防止用户进行恶意请求，在产生激活链接时，将用户信息进行加密生成token，将加密后的token放在激活链接中
    #     # http://www.meiduo.site:8080/success_verify_email.html?token=<token>
    #     verify_url = instance.generate_verify_email_url()
    #
    #     # TODO: 发送邮件
    #     # subject = "美多商城邮箱验证"
    #     # html_message = '<p>尊敬的用户您好！</p>' \
    #     #                '<p>感谢您使用美多商城。</p>' \
    #     #                '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
    #     #                '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
    #     # send_mail(subject, '', settings.EMAIL_FROM, [email], html_message=html_message)
    #
    #     # 发出发送邮件的任务
    #     from celery_tasks.email.tasks import send_verify_email
    #     send_verify_email.delay(email, verify_url)
    #
    #     return instance


class UserDetailSerializer(serializers.ModelSerializer):
    """用户个人信息序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


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
        # user = super().create(validated_data)
        #
        # # 对密码进行加密
        # password = validated_data['password']
        # user.set_password(password)
        # user.save()

        # 调用create_user方法
        user = User.objects.create_user(**validated_data)

        # 注册成功就让用户处于登录状态
        # 由服务器签发一个jwt token，保存用户身份信息
        from rest_framework_jwt.settings import api_settings

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
