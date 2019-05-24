from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import CartSerializer,CartSKUSerializer,CartDeleteSerializer
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework import status
from goods.models import SKU
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

    #查询购物车
    def get(self,request):
        #获取用户，判断是否登录
        try:
            user=request.user # type:User
        except Exception:
            #前方携带错误的jwttoken 用户没有登录
            user =None
        #获取数据,以登陆在redis，为登陆在cookie
        if user is not None and user.is_authenticated:
            #登陆了，redis查询数据
            redis_conn = get_redis_connection('cart')
            redis_cart=redis_conn.hgetall("cart_%s" %user.id)
            # 获取购物车被选中的商品的id
            cart_selected_key = 'cart_selected_%s' % user.id
            redis_cart_selected = redis_conn.smembers(cart_selected_key)
            #讲redis的数据整合，和cookie中一致，方便查询
            cart_dict = {}
            # 组织数据
            # {
            #     '<sku_id>': {
            #         'count': '<count>',
            #         'selected': '<selected>'
            #     },
            #     ...
            # }

            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_cart_selected#返回Ture或者False
                }

        else:
            #未登录，cookie查询数据
            # 获取客户端发送的cookie信息
            cookie_cart = request.COOKIES.get('cart')#type:str

            if cookie_cart:
                # 对cookie数据进行解析
                cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))
            else:
                cart_dict = {}
        #数据库查询sku对象
        sku_id_list=cart_dict.keys()
        sku_obj_list=SKU.objects.filter(id__in=sku_id_list)
        #补充count，selected
        for sku in sku_obj_list:
            sku.count=cart_dict[sku.id]['count']
            sku.selected=cart_dict[sku.id]['selected']
        #返回
        serializers=CartSKUSerializer(sku_obj_list,many=True)
        return Response(serializers.data)

    #修改购物车
    def put(self,request):
        # 检查数据
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.data.get("sku_id")
        count = serializer.data.get("count")
        selected = serializer.data.get("selected")
        # 判断用户是否登录
        try:
            user = request.user  # type:User
        except Exception:
            # 前方携带错误的jwttoken 用户没有登录
            user = None
        # 保存数据,以登修改redis，为登陆修改cookie
        if user is not None and user.is_authenticated:
        # 用户已经登录,直接覆盖原数据，数据是幂等的
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hset("cart_%s" % user.id,sku_id,count)
            # 如果是勾选了的，没有的直接添加未勾选直接删除
            if selected:
                pl.sadd('cart_selected_%s' % user.id,sku_id)
            else:
                pl.srem('cart_selected_%s' % user.id,sku_id)

            pl.execute()
            return Response(serializer.data)
        #用户未登录
        else:
            # 获取客户端发送的cookie信息
            cookie_cart = request.COOKIES.get('cart')  # type:str
            if cookie_cart:
                # 对cookie数据进行解析
                cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))
            else:
                cart_dict = {}
            #更改数据
            cart_dict[sku_id]={
                "count":count,
                "selected":selected
            }
            # 对cart_dict数据进行处理
            cart_data = base64.b64encode(pickle.dumps(cart_dict)).decode()

            response = Response(serializer.data)
            #保存到cookie的有效期
            response.set_cookie('cart', cart_data, max_age=365 * 24 * 60 * 60)
            return response

    #购物车删除
    def delete(self,request):
    #检查参数
        serializer=CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id=serializer.validated_data['sku_id']
    #判断用户登录
        try:
            user = request.user  # type:User
        except Exception:
            # 前方携带错误的jwttoken 用户没有登录
            user = None
    #分别处理,如果用户登录了从redis中删除，未登录从cookie中删除

        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hdel("cart_%s" % user.id,sku_id)
            pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            #返回
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # 获取客户端发送的cookie信息
            cookie_cart = request.COOKIES.get('cart')  # type:str
            if cookie_cart:
                # 对cookie数据进行解析
                cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))
            else:
                cart_dict = {}
            response = Response(serializer.data)
            if sku_id in cart_dict:
                # cart_dict.pop(sku_id)
                del cart_dict[sku_id]
                # 对cart_dict数据进行处理
                cart_data = base64.b64encode(pickle.dumps(cart_dict)).decode()
                # 保存到cookie的有效期
                response.set_cookie('cart', cart_data, max_age=365 * 24 * 60 * 60)
            return response

















