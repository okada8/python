from django.contrib.auth.backends import ModelBackend
from .models import User
import re


#用户登陆
def jwt_response_payload_handler(token,user=None,request=None):
    """
        自定义jwt认证成功返回数据
        """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_account(account):
    """根据帐号信息查找用对象"""
    #account：可以是手机号，用户号
    #return：User对象，不存在返回None
    #判断account是否是是手机号
    try:
        #如果传进来的时候是手机号，通过手机号获取用户对象
        if re.match(r'^1[3-9]\d{9}$',account):
            user=User.objects.get(mobile=account)
        else:
        #传进来的是用户名
            user=User.objects.get(username=account)
    #如果用户不存在
    except User.DoesNotExist:
        return None
    else:
        return user





class UsernameMobileAuthBackend(ModelBackend):
    """自定义的方法认证后端需要重写方法"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        #根据uesrname查询用对象,username有可能是手机号，有可能是用户名，调用自定义方法获取用户对象
        user=get_user_by_account(username)
        #如果用户对象存在，调用check_password方法检查密码
        if user is not None and user.check_password(password):
            #验证成功
            return user


