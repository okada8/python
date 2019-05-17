from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import CartSerializer
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework import status
import pickle,base64
# Create your views here.


#购物车
class CartView(APIView):
    #不要检验jwttoken
    def perform_authentication(self,request):
        pass


    #保存购物车数据，用户可能登陆可能不登陆
    def post(self,request):
        #检查数据
        serializer=CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id=serializer.data.get("sku_id")
        count=serializer.data.get("count")
        selected=serializer.data.get("selected")
        #判断用户是否登录
        try:
            user=request.user # type:User
        except Exception:
            #前方携带错误的jwttoken 用户没有登录
            user =None
        #保存数据,以登陆保存redis，为登陆保存cookie
        if user is not None and user.is_authenticated:
            #用户已经登录
            # 2. 保存用户的购物车记录
            redis_conn = get_redis_connection('cart')
            pipeline = redis_conn.pipeline()
            cart_key = 'cart_%s' % user.id

            # 保存购物车中商品及数量
            pipeline.hincrby(cart_key, sku_id, count)

            # 保存购物车中商品的选中状态
            cart_selected_key = 'cart_selected_%s' % user.id
            if selected:
                pipeline.sadd(cart_selected_key, sku_id)

            pipeline.execute()

            # 3. 返回应答，保存购物车记录成功
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            #保存到cookie中
            # 获取客户端发送的cookie信息
            cookie_cart = request.COOKIES.get('cart')#type:str

            if cookie_cart:
                # 对cookie数据进行解析
                cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))
            else:
                cart_dict = {}

            if sku_id in cart_dict:
                count += cart_dict[sku_id]['count']

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 对cart_dict数据进行处理
            cart_data = base64.b64encode(pickle.dumps(cart_dict)).decode()

            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            #保存到cookie的有效期
            response.set_cookie('cart', cart_data, max_age=365 * 24 * 60 * 60)
            return response
