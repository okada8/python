from django.conf.urls import url
from .views import HotSKUListView,SKUListView,SKUSearchViewSet
from rest_framework.routers import DefaultRouter



urlpatterns = [
    url(r'^categories/(?P<category_id>\d+)/skus/$',SKUListView.as_view()),#通过类别获取商品列表数据
    url(r'^categories/(?P<category_id>\d+)/hotskus/$',HotSKUListView.as_view()),#热销商品

]



router=DefaultRouter()
router.register('skus/search',SKUSearchViewSet,base_name='skus-search')
urlpatterns += router.urls