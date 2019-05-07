from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, CreateAPIView,RetrieveAPIView,UpdateAPIView
from users.models import User
from users.serializers import CreateUserSerializer
from .serializers import CheckSMSCodeSerializer,RestePasswordSerializer,UserDetailSerializer,EmailSerializer

from verifications.serializers import CheckImageCodeSerialzier
from .utils import get_user_by_account
from rest_framework import status,mixins
from rest_framework.permissions import IsAuthenticated
import re
# Create your views here.

# POST /users/
# class UserView(GenericAPIView):
class UserView(CreateAPIView):
    #用户注册,也是我们自己定义的序列化器，拿到数据有，用户名，手机号，
    serializer_class = CreateUserSerializer

#用户注册时验证用户名是否以存在，regist.js会请求
# GET:/usernames/(?P<username>\w{5,20})/count/,
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
# GET: /mobiles/(?P<mobile>1[3-9]\d{9})/count/,
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
#GET:/accounts/(?P<account>\w{4,20})/sms/token/
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
#GET:/accounts/(?P<account>\w{4,20})/password/token/
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
#POST:/users/(?P<pk>\d+)/password/
class PasswordView(mixins.UpdateModelMixin,GenericAPIView):
    """修改密码"""
    #要指出要更改的user来自于哪里
    queryset = User.objects.all()
    serializer_class = RestePasswordSerializer
    def post(self,request,pk):
        return self.update(request,pk)

#用户详情信息，个人中心
#GET /user/
class UserDetailView(RetrieveAPIView):

    serializer_class =UserDetailSerializer
    #只有登陆成功后才能查看用户中心
    permission_classes = [IsAuthenticated]

    #因为现访问路径是/user/，不是/users/(?P<pk>\d+)/，所以要重写get_object方法，
    #类视图对象里有request对象
    def get_object(self):
        #返回请求用户对象user,self是类视图对象，里面有request属性,user是jwt机制先查询后然后加在request对象的属性
        return self.request.user

#邮箱验证，邮箱更新
#POST /emails/
class EmailView(UpdateAPIView):
    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]
    #1重写get_object，序列化器才能知道是哪个用户的邮箱
    def get_object(self):
        return self.request.user
    #2重写get_serializer
    # def get_serializer(self, *args, **kwargs):
    #     return EmailSerializer(self.request.user,self.request.data)


#邮箱验证接口
class EmailVerifyView(APIView):
    def get(self,request):
        #获取token
        token=request.query_params.get('token')
        if not token:
            return Response({"缺少的token"}, status=status.HTTP_400_BAD_REQUEST)
        #校验token,保存
        result=User.check_verify_email_token(token)
        #返回
        if result:
            return Response({"message":"ok"})
        else:
            return Response({"非法的token"},status=status.HTTP_400_BAD_REQUEST)





































