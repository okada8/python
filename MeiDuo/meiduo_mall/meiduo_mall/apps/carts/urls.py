from django.conf.urls import url
from .views import CartView

urlpatterns = [
    url(r'^cart/$',CartView.as_view()),#购物车

]