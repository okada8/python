from django.conf.urls import url
from .views import OAuthQQURLView,OAuthQQUserView

urlpatterns = [
    url(r'^qq/authorization/$',OAuthQQURLView.as_view()),#qq登陆
    url(r'^qq/user/$',OAuthQQUserView.as_view()),#用胡选择完qq登陆后，我们需要和qq交互
]