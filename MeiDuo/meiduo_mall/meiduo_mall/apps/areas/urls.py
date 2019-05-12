from django.conf.urls import url,include
from rest_framework.routers import DefaultRouter
from .views import AreasViewSet

router=DefaultRouter()
router.register('areas',AreasViewSet,base_name='area')

urlpatterns = [
   #url('',include(router.urls))

]
urlpatterns+=router.urls