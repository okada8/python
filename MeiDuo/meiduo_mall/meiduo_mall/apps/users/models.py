from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from django.conf import settings
from meiduo_mall.utils.models import BaseModel
from .constants import SEND_SMS_CODE_TOKEN_EXPIRES, SET_PASSWORD_TOKEN_EXPIRES, VERIFY_EMAIL_TOKEN_EXPIRES


# Create your models here.

class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')

    class Meta:
        # 新建立一张表
        db_table = "tb_user"
        verbose_name = "用户信息"
        # 管理员后台要把注册的这个功能叫什么
        verbose_name_plural = verbose_name

    # 发送短信验证码生成access_token并返回
    def generate_send_sms_code_token(self):  # self是user
        # 创建itsdangerous模型的转换工具
        serializer = TJWSSerializer(settings.SECRET_KEY, SEND_SMS_CODE_TOKEN_EXPIRES)
        # 将手机号字典放在token中
        data = {
            "mobile": self.mobile
        }
        # 生成token
        token = serializer.dumps(data)  # type:bytes
        # 返回非二进制token
        return token.decode()

    # 校验access_token的时候时没有user对象的，所以做成静态方法
    @staticmethod
    def check_send_sms_token(token):
        # 创建itsdangerous模型的转换工具
        serializer = TJWSSerializer(settings.SECRET_KEY, SEND_SMS_CODE_TOKEN_EXPIRES)
        try:
            # 检验token
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            # 取出手机号码
            mobile = data.get('mobile')
            return mobile

    def generate_set_password_token(self):  # self是user本身
        """
        忘记密码部分生成修改密码的token
        :return: token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, SET_PASSWORD_TOKEN_EXPIRES)
        # 将用户id放在token中
        data = {
            "user_id": self.id
        }
        # 生成token
        token = serializer.dumps(data)  # type:bytes
        # 返回非二进制token
        return token.decode()

    # 校验更改密码token
    @staticmethod
    def check_set_password_token(token, user_id):
        # 创建itsdangerous模型的转换工具
        serializer = TJWSSerializer(settings.SECRET_KEY, SEND_SMS_CODE_TOKEN_EXPIRES)
        try:
            # 检验token
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            # 取出手机号码
            if user_id != str(data.get('user_id')):
                return False
            else:
                return True

    # 生成邮件激活链接
    def generate_verify_email_url(self):
        """
        生成验证邮箱的url
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, VERIFY_EMAIL_TOKEN_EXPIRES)
        # 将用户id放在token中
        data = {
            "user_id": self.id,
            "email": self.email
        }
        # 生成token
        token = serializer.dumps(data)  # type:bytes
        # 生成url
        verify_url = 'http://246856ih33.wicp.vip/success_verify_email.html?token=' + token.decode()
        return verify_url

    # 验证邮箱token
    @staticmethod
    def check_verify_email_token(token):
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=VERIFY_EMAIL_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return False
        else:
            email = data.get('email')
            user_id = data.get('user_id')
            try:
                User.objects.filter(id=user_id, email=email).update(email_active=True)
            except User.DoesNotExist:
                return False
            else:
                # user.email_active=True
                # user.save()
                return True


class Address(BaseModel):
    """
    用户地址
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses',
                                 verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses',
                                 verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        # 排序按照时间的倒序
        ordering = ['-update_time']
