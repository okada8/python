from django.shortcuts import render
from carts.utils import merge_cart_cookie_to_redis
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, CreateAPIView,RetrieveAPIView,UpdateAPIView
from users.models import User
from users.serializers import CreateUserSerializer
from .serializers import CheckSMSCodeSerializer,RestePasswordSerializer,UserDetailSerializer,EmailSerializer,\
UserAddressSerializer,AddressTitleSerializer,AddUserBrowsingHistorySerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from .constants import USER_ADDRESS_COUNTS_LIMIT
from verifications.serializers import CheckImageCodeSerialzier
from .utils import get_user_by_account
from rest_framework import status,mixins
from rest_framework.permissions import IsAuthenticated
from django_redis import get_redis_connection
from goods.serializers import SKU,SKUSerializers
from rest_framework_jwt.views import ObtainJSONWebToken
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



class AddressViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """
    用户地址新增与修改
    """
    serializer_class = UserAddressSerializer
    permissions = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    # GET /addresses/
    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })

    # POST /addresses/
    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        """
        # 检查用户地址数据数目不能超过上限
        count = request.user.addresses.filter(is_deleted=False).count()
        if count >= USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已达到上限'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    # delete /addresses/<pk>/
    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    # put /addresses/pk/status/
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    # put /addresses/pk/title/
    # 需要请求体参数 title
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserBrowsingHistoryView(mixins.CreateModelMixin,GenericAPIView):
    """
    用户浏览历史记录
    """
    serializer_class = AddUserBrowsingHistorySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return self.create(request)

    def get(self, request):
        """
        获取
        """
        user_id = request.user.id

        redis_conn = get_redis_connection("history")
        history = redis_conn.lrange("history_%s" % user_id, 0, 4)
        skus = []
        # 为了保持查询出的顺序与用户的浏览历史保存顺序一致
        for sku_id in history:
            sku = SKU.objects.get(id=sku_id)
            skus.append(sku)

        s = SKUSerializers(skus, many=True)
        return Response(s.data)




#登录的时候需要调取购物车,因为登录是用jwt验证机制，要调取购物车数据，要重写方法
class UserAuthorizationView(ObtainJSONWebToken):

    def post(self, request, *args, **kwargs):
        #调用jwt扩展的方法，对用户登录数据进行验证
        response=super().post(request)
        #用户登录成功，进行购物车数据合并
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            user=serializer.validated_data.get('user')
            #河滨购物车
            response =merge_cart_cookie_to_redis(request,response,user)
        return response
























