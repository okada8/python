from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.

class User(AbstractUser):
    """用户模型类"""
    mobile=models.CharField(max_length=11,unique=True,verbose_name="手机号")

    class Meta:
        db_table="tb_user"
        verbose_name = "用户信息"
        verbose_name_plural=verbose_name

    # def __str__(self):
    #     return self.username