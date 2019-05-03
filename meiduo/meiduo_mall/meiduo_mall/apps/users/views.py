from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, CreateAPIView
from users.models import User
from users.serializers import CreateUserSerializer
from .serializers import CheckSMSCodeSerializer,RestePasswordSerializer
from verifications.serializers import CheckImageCodeSerialzier
from .utils import get_user_by_account
from rest_framework import status,mixins
import re
# Create your views here.

# POST /users/
# class UserView(GenericAPIView):
class UserView(CreateAPIView):
    #用户注册,也是我们自己定义的序列化器，拿到数据有，用户名，手机号，
    serializer_class = CreateUserSerializer

#用户注册时验证用户名是否以存在，regist.js会请求
# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
class UsernameCountView(APIView):
    """
    用户名数量
    """
    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()#用户名时唯一的

        data = {
            'username': username,
            'count': count#count要么是0要么是1
        }

        return Response(data)#前端js会根据count是否大于0来判断用户名是否可用

#用户注册时验证手机号码是否以存在，regist.js会请求
# url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
class MobileCountView(APIView):
    """
    手机号数量
    """
    def get(self, request, mobile):
        """
        获取指定手机号数量
        """
        count = User.objects.filter(mobile=mobile).count()#手机号码是唯一的

        data = {
            'mobile': mobile,
            'count': count#要么是0要么是1
        }

        return Response(data)#前端js会根据count是否大于0来判断手机号码是否可用


#登陆时用户忘记了密码获取忘记密码部分用户发的短信秘钥，regist.js会请求
class SMSCodeToKenView(GenericAPIView):
    #获取注册时的图片验证码序列化器，验证图片验证码
    serializer_class = CheckImageCodeSerialzier

    def get(self,request,account):
        """校验图片验证码"""
        serializer=self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        #根据account帐号查询user对象,在utils中定义了如果用户返回的是手机号和用户名的方法
        user=get_user_by_account(account)
        if user is None:
            return Response({"message":'用户不存在'},status=status.HTTP_404_NOT_FOUND)
        #根据user用户对象手机号生成access_token，这是忘记密码部分要验证手机号，需要单独生成token
        access_token=user.generate_send_sms_code_token()#type:str
        #处理手机号，利用正则替换成138****8888
        mobile=re.sub(r'(\d{3})\d{4}(\d{4})',r'\1****\2',user.mobile)
        #返回
        return Response({
            "mobile":mobile,
            "access_token":access_token
        })





#用户忘记了密码然后设置用户密码的token
class PasswordTokenView(GenericAPIView):
    serializer_class = CheckSMSCodeSerializer

    def get(self,request,account):
        """根据用户帐号获取修改密码的token"""
        #校验短信验证码
        serializer=self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        #拿到user对象
        user=serializer.user
        #生成修改密码的token
        access_token=user.generate_set_password_token()

        return Response({"user_id":user.id,"access_token":access_token})


#忘记密码入口的修改密码
class PasswordView(mixins.UpdateModelMixin,GenericAPIView):
    """修改密码"""
    #要指出要更改的user来自于哪里
    queryset = User.objects.all()
    serializer_class = RestePasswordSerializer
    def post(self,request,pk):
        return self.update(request,pk)













