from django.conf.urls import url
from .views import ImageCodeView,SMSCodeView,SMSCodeByToKenView
urlpatterns=[
    url(r'^image_codes/(?P<image_code_id>.+)/$',ImageCodeView.as_view()),#注册获取图片验证码
    url(r'sms_codes/(?P<mobile>1[3-9]\d{9})/$',SMSCodeView.as_view()),#注册获取短信验证码
    url(r'sms_codes/$',SMSCodeByToKenView.as_view()),
]