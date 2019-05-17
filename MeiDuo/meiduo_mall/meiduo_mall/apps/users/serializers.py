import re
from celery_tasks.email.tasks import send_verify_email
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from users.models import User,Address
from goods.models import SKU
from .utils import get_user_by_account

#注册的时候用
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
        real_sms_code = redis_conn.get('sms_%s' % mobile) # type:bytes

        if not real_sms_code:
            raise serializers.ValidationError('短信验证码已过期')

        # 对比
        sms_code = attrs['sms_code'] # type:str
        real_sms_code = real_sms_code.decode() # type:str
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

#用户忘记密码当他把短信验证码发送到后段的时候需要校验
class CheckSMSCodeSerializer(serializers.Serializer):
    #检验sms_code是否时6位
    sms_code=serializers.CharField(min_length=6,max_length=6)
    #value就是sms_code
    def validate_sms_code(self,value):
        account=self.context['view'].kwargs['account']
        #获取user
        user=get_user_by_account(account)
        if user is None:
            raise serializers.ValidationError('用户不存在')
        #把user对象保存到序列化器对象当中
        self.user=user
        #从redis中拿出真实短信验证码
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code=redis_conn.get("sms_%s" % user.mobile)
        #如果拿出来的值不存在
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        #客户输入的值和真实值不相等
        if value != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')
        return value

#用户忘记密码后更改密码
class RestePasswordSerializer(serializers.ModelSerializer):
    """重至密码序列花器"""
    password2=serializers.CharField(label="确认密码",write_only=True)
    access_token=serializers.CharField(label='操作token',write_only=True)

    class Meta:
        model=User
        fields=("id","password","password2","access_token")
        extra_kwargs = {
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

    def validate(self, attrs):
        """校验数据"""
        #判断两次密码
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码不一致')
        #判断access_token
        pk=self.context['view'].kwargs['pk']#type:str
        allow=User.check_set_password_token(attrs['access_token'],pk)#返回的是ture和false
        if not allow:
            raise serializers.ValidationError('无效的access token')
        return attrs

    def update(self, instance, validated_data):#instance是user对象，validated_data是attrs
        """跟新密码"""
        #调用django用户模型的设置密码方法
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

#用户个人中心
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields = ("id", "username", "mobile", "email","email_active")

#用户绑定邮箱
class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('id','email')
        extra_kwargs ={
            'email':{
            'required':True,
            }
        }

    def update(self, instance, validated_data):#instance=user
        """重写更新方法，添加发送邮件"""
        #取出新的email
        emial=validated_data['email']
        #user对象的email重新设置
        instance.email=emial
        #保存至数据库
        instance.save()
        #发送邮件
        verify_url=instance.generate_verify_email_url()#生成的链接
        send_verify_email.delay(emial,verify_url)
        return instance

class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器
    """
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        """
        验证手机号
        """
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        """
        保存
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """
    class Meta:
        model = Address
        fields = ('title',)

class AddUserBrowsingHistorySerializer(serializers.Serializer):
    """
    添加用户浏览历史序列化器
    """
    sku_id = serializers.IntegerField(label="商品SKU编号", min_value=1)

    def validate_sku_id(self, value):
        """
        检验sku_id是否存在
        """
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('该商品不存在')
        return value

    def create(self, validated_data):
        """
        保存
        """
        user_id = self.context['request'].user.id
        sku_id = validated_data['sku_id']

        redis_conn = get_redis_connection("history")
        pl = redis_conn.pipeline()

        # 移除已经存在的本商品浏览记录
        pl.lrem("history_%s" % user_id, 0, sku_id)
        # 添加新的浏览记录
        pl.lpush("history_%s" % user_id, sku_id)
        # 只保存最多5条记录
        pl.ltrim("history_%s" % user_id, 0, 4)

        pl.execute()

        return validated_data