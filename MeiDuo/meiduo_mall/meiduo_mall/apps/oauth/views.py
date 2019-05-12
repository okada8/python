from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import OAuthQQ
from rest_framework import status
from .exceptions import QQAPIException
from .models import OAuthQQUser
from rest_framework_jwt.settings import api_settings
from rest_framework.generics import GenericAPIView
from .serializers import OAuthQQUserSerializer
# Create your views here.

#提供qq登陆的接口 /oauth/qq/authorization/?state=xxx
class OAuthQQURLView(APIView):
    def get(self,request):
        #提取state参数
        state=request.query_params.get('state')
        #前端没有指明登陆成功后调转到哪里
        if not state:
            state='/'
        #拼接qq登陆的地址
        oauth_qq=OAuthQQ(state=state)
        login_url=oauth_qq.generate_qq_login_url()
        #返回地址
        return Response({"oauth_url":login_url})

#提供qq登陆后，判断用户是否是第一次用qq登陆的接口
class OAuthQQUserView(GenericAPIView):
    serializer_class = OAuthQQUserSerializer
    """
    获取qq用户对应的商城用户，当用户用qq登陆后，qq会把code传给我们
    """
    def get(self,request):
        #提取code参数
        code=request.query_params.get('code')
        if not code:
            return Response({"message":'缺少参数'},status=status.HTTP_400_BAD_REQUEST)
        #向qq服务器发起请求获取accesstoken
        oauth_qq=OAuthQQ()
        try:
            access_token=oauth_qq.get_access_token(code)
            #凭借token向qq服务器发送请求获取openid
            openid=oauth_qq.get_openid(access_token)
        except QQAPIException:
            return Response({'message':'获取qq用户数据异常'},status=status.HTTP_503_SERVICE_UNAVAILABLE)
        #根据openid查询此用户是否之前绑定过
        try:
            oauth_user=OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            #如果为绑定，我们手动创建绑定身份使用的access token，返回
            access_token=OAuthQQUser.generate_save_user_token(openid)
            return Response({'access_token':access_token})
        else:
            # 如果已经绑定，直接生成JWT token 并且直接返回
            # 由服务器签发一个jwt token，保存用户身份信息
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            # 生成载荷信息(payload)
            payload = jwt_payload_handler(oauth_user.user)
            # 生成jwt token
            token = jwt_encode_handler(payload)
            return Response({
                'token':token,
                'username':oauth_user.user.username,
                'user_id':oauth_user.user.id
            })

    """
    处理第一次用qq登陆的用户的请求，会把的手机号，短信验证码，密码用post方式传过来
    """
    def post(self,request):
        #调用序列化器校验数据并且保存数据
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.save()
        #返回用户登陆的jwt token
        # 由服务器签发一个jwt token，保存用户身份信息
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        # 生成载荷信息(payload)
        payload = jwt_payload_handler(user)
        # 生成jwt token
        token = jwt_encode_handler(payload)
        # 返回
        return Response({
            'token':token,
            'username':user.username,
            'user_id':user.id
        })























