from django.db import models
from meiduo_mall.utils.models import BaseModel
from django.conf import settings
from .constants import SAVE_QQ_USER_TOKEN_EXPIRES
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer,BadData
# Create your models here.

class OAuthQQUser(BaseModel):
    """qq登陆用户数据"""
    user=models.ForeignKey('users.User',on_delete=models.CASCADE,verbose_name='用户')
    openid=models.CharField(max_length=64,verbose_name='openid',db_index=True)

    class Meta:
        db_table='tb_oauth_qq'
        verbose_name='qq登陆用户数据'
        verbose_name_plural=verbose_name

    # 用户用首次用qq登陆后需要生成token
    @staticmethod
    def generate_save_user_token(openid):
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=SAVE_QQ_USER_TOKEN_EXPIRES)
        # 将用户id放在token中
        data = {
            "openid": openid
        }
        # 生成token
        token = serializer.dumps(data)  # type:bytes
        # 返回非二进制token
        return token.decode()
    #校验access_token
    @staticmethod
    def check_save_user_token(token):
        # 创建itsdangerous模型的转换工具
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=SAVE_QQ_USER_TOKEN_EXPIRES)
        try:
            # 检验token
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            # 取出openid
            openid = data.get('openid')
            return openid










