from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from users.views import UsernameCountView,MobileCountView,UserView

urlpatterns = [
    url(r'^usernames/(?P<username>\w{5,20})/count/$', UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', MobileCountView.as_view()),
    url(r'^users/$', UserView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),
]