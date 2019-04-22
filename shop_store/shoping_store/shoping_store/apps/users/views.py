from datetime import datetime

from django.shortcuts import render
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import ObtainJSONWebToken, jwt_response_payload_handler
from django_redis import get_redis_connection

from users import constants
from users import serializers
from users.models import User
from users.serializers import CreateUserSerializer, UserDetailSerializer, EmailSerializer
# from users.serializers import UserAddBrowseHistorySerializer

# from goods.models import SKU
# from goods.serializers import SKUSerializer
# from cart.utils import merge_cookie_cart_to_redis
# Create your views here.


# POST /authorizations/
# class UserAuthorizeView(ObtainJSONWebToken):
#     """登录视图"""
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#
#         if serializer.is_valid():
#             # 登录成功
#             user = serializer.object.get('user') or request.user
#             token = serializer.object.get('token')
#             response_data = jwt_response_payload_handler(token, user, request)
#             response = Response(response_data)
#             if api_settings.JWT_AUTH_COOKIE:
#                 expiration = (datetime.utcnow() +
#                               api_settings.JWT_EXPIRATION_DELTA)
#                 response.set_cookie(api_settings.JWT_AUTH_COOKIE,
#                                     token,
#                                     expires=expiration,
#                                     httponly=True)
#
#             # 补充购物车记录合并的过程: 调用合并购物车记录函数
#             merge_cookie_cart_to_redis(request, user, response)
#
#             return response
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# POST /browse_histories/
# class UserBrowseHistoryView(GenericAPIView):
# class UserBrowseHistoryView(CreateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = UserAddBrowseHistorySerializer
#
#     def get(self, request):
#         """
#         获取用户浏览记录:
#         1. 从redis中获取用户浏览的商品的id
#         2. 根据商品id获取对应商品的信息
#         3. 将商品的信息序列化并返回
#         """
#         # 获取登录user
#         user = request.user
#
#         # 1. 从redis中获取用户浏览的商品的id
#         redis_conn = get_redis_connection('history')
#         history_key = 'history_%s' % user.id
#
#         # lrange(key, start, end): 获取redis列表指定区间内的元素
#         # [b'<sku_id>', b'<sku_id>', ...]
#         sku_ids = redis_conn.lrange(history_key, 0, 4)
#
#         # 2. 根据商品id获取对应商品的信息
#         skus = []
#         for sku_id in sku_ids:
#             sku = SKU.objects.get(id=sku_id)
#             skus.append(sku)
#
#         # 3. 将商品的信息序列化并返回
#         serializer = SKUSerializer(skus, many=True)
#         return Response(serializer.data)
#
#     # def post(self, request):
#     #     """
#     #     request.user: 登录用户
#     #     历史浏览记录添加:
#     #     1. 获取商品sku_id并进行校验(sku_id比传，sku_id对应的商品是否存在)
#     #     2. 在redis中保存用户浏览的记录
#     #     3. 返回应答
#     #     """
#     #     # 1. 获取商品sku_id并进行校验(sku_id必传，sku_id对应的商品是否存在)
#     #     serializer = self.get_serializer(data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #
#     #     # 2. 在redis中保存用户浏览的记录
#     #     serializer.save()
#     #     # 3. 返回应答
#     #     return Response(serializer.data, status=status.HTTP_201_CREATED)


# class AddressViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
#     """
#     用户地址新增与修改
#     """
#     serializer_class = serializers.UserAddressSerializer
#     permissions = [IsAuthenticated]
#
#     def get_queryset(self):
#         return self.request.user.addresses.filter(is_deleted=False)
#
#     # GET /addresses/
#     def list(self, request, *args, **kwargs):
#         """
#         用户地址列表数据
#         """
#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset, many=True)
#         user = self.request.user
#         return Response({
#             'user_id': user.id,
#             'default_address_id': user.default_address_id,
#             'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
#             'addresses': serializer.data,
#         })
#
#     # POST /addresses/
#     def create(self, request, *args, **kwargs):
#         """
#         保存用户地址数据
#         """
#         # 检查用户地址数据数目不能超过上限
#         count = request.user.addresses.filter(is_deleted=False).count()
#         if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
#             return Response({'message': '保存地址数据已达到上限'}, status=status.HTTP_400_BAD_REQUEST)
#
#         return super().create(request, *args, **kwargs)
#
#     # delete /addresses/<pk>/
#     def destroy(self, request, *args, **kwargs):
#         """
#         处理删除
#         """
#         address = self.get_object()
#
#         # 进行逻辑删除
#         address.is_deleted = True
#         address.save()
#
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#     # put /addresses/pk/status/
#     @action(methods=['put'], detail=True)
#     def status(self, request, pk=None):
#         """
#         设置默认地址
#         """
#         address = self.get_object()
#         request.user.default_address = address
#         request.user.save()
#         return Response({'message': 'OK'}, status=status.HTTP_200_OK)
#
#     # put /addresses/pk/title/
#     # 需要请求体参数 title
#     @action(methods=['put'], detail=True)
#     def title(self, request, pk=None):
#         """
#         修改标题
#         """
#         address = self.get_object()
#         serializer = serializers.AddressTitleSerializer(instance=address, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)


# PUT /emails/verification/?token=<token>
class EmailVerifyView(APIView):
    def put(self, request):
        """
        激活用户邮箱:
        1. 获取token参数并进行校验(token必传，token是否有效)
        2. 设置用户邮箱验证标记
        3. 返回应答
        """
        # 1. 获取token参数并进行校验(token必传，token是否有效)
        token = request.query_params.get('token')

        if not token:
            return Response({'message': '缺少token信息'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.check_verify_email_token(token)

        if user is None:
            return Response({'message': '无效的token信息'}, status=status.HTTP_400_BAD_REQUEST)

        # 2. 设置用户邮箱验证标记
        user.email_active = True
        user.save()

        # 3. 返回应答
        return Response({'message': 'OK'})


# PUT /email/
# class EmailView(GenericAPIView):
class EmailView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer

    def get_object(self):
        """返回当前登录用户"""
        return self.request.user

    # def put(self, request):
    #     """
    #     设置用户的邮箱:
    #     1. 获取email并进行校验(email必传，邮箱格式)
    #     2. 设置用户邮箱，给用户邮箱发送激活邮件
    #     3. 返回应答
    #     """
    #     # 获取登录user
    #     user = self.get_object()
    #
    #     # 1. 获取email并进行校验(email必传，邮箱格式)
    #     serializer = self.get_serializer(user, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #     # 2. 设置用户邮箱，给用户邮箱发送激活邮件
    #     serializer.save()
    #
    #     # 3. 返回应答
    #     return Response(serializer.data)


# GET /user/
# class UserDetailView(GenericAPIView):
class UserDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get_object(self):
        """返回当前登录user"""
        return self.request.user

    # def get(self, request):
    #     """
    #     self.request: request对象
    #     request.user:
    #         1. 如果用户已认证，request.user就是登录的用户对象
    #         2. 如果用户未认证，request.user就是匿名用户的对象
    #     获取用户的个人信息:
    #     1. 获取登录用户user
    #     2. 将user序列化并返回
    #     """
    #     # 1. 获取登录用户user
    #     # user = request.user
    #     user = self.get_object()
    #
    #     # 2. 将user序列化并返回
    #     serializer = self.get_serializer(user)
    #     return Response(serializer.data)


# POST /users/
# class UserView(GenericAPIView):
class UserView(CreateAPIView):
    serializer_class = CreateUserSerializer

    # def post(self, request):
    #     """
    #     注册用户信息的保存:
    #     1. 获取参数并进行校验(参数完整性，两次密码是否一致，手机号格式，手机号是否已注册，短信验证码是否正确，是否同意协议)
    #     2. 保存注册用户信息
    #     3. 返回应答，注册成功
    #     """
    #     # 1. 获取参数并进行校验(参数完整性，两次密码是否一致，手机号格式，手机号是否已注册，短信验证码是否正确，是否同意协议)
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #
    #     # 2. 保存注册用户信息(create)
    #     serializer.save()
    #
    #     # 3. 返回应答，注册成功
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)


# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
class UsernameCountView(APIView):
    """
    用户名数量
    """
    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


# url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
class MobileCountView(APIView):
    """
    手机号数量
    """
    def get(self, request, mobile):
        """
        获取指定手机号数量
        """
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)