from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import OrderSettlementSerializer
from rest_framework.response import Response
from goods.models import SKU
from decimal import Decimal
from .serializers import SaveOrderSerializer


from rest_framework.generics import CreateAPIView
# Create your views here.

class OrderSettlementView(APIView):
    """
    订单结算
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        获取
        """
        user = request.user

        # 从购物车中获取用户勾选要结算的商品信息
        redis_conn = get_redis_connection('cart')
        redis_cart = redis_conn.hgetall('cart_%s' % user.id)
        cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)

        cart = {}
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        # 查询商品信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]
            sku.selected=True
        # 运费,吧小数和整数分开，对小数精确度有很大提高
        freight = Decimal('10.00')

        serializer = OrderSettlementSerializer({'freight': freight, 'skus': skus})
        return Response(serializer.data)


class SaveOrderView(CreateAPIView):
    """
    保存订单
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SaveOrderSerializer




