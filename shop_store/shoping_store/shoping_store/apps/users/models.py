from django.db import models
#django的contrib组件auth认证系统models模型类AbstractUser抽象类
#用户认证系统--auth，它默认使用 auth_user 表来存储用户数据
from django.contrib.auth.models import AbstractUser
# Create your models here.

#关于为什么要类里面写一个类，AbstractUser中的写发就是这样
class User(AbstractUser):
    """
    用户信息
    """
    #多加了一个手机字段
    mobile=models.CharField(max_length=11,unique=True,verbose_name="手机号")

    class Meta:
        #表名
        db_table="tb_users"
        verbose_name = '用户'
        verbose_name_plural = verbose_name