from django.conf.urls import url
from .views import OrderSettlementView,SaveOrderView

urlpatterns = [
    url(r'^orders/settlement/$',OrderSettlementView.as_view()),#订单支付
    url(r'^orders/$',SaveOrderView.as_view()),#保存支付

]