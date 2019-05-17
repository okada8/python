from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter
from users.views import UsernameCountView,MobileCountView,UserView,SMSCodeToKenView,PasswordTokenView,\
    PasswordView,UserDetailView,EmailView,EmailVerifyView,AddressViewSet,UserBrowsingHistoryView

urlpatterns = [
    url(r'^usernames/(?P<username>\w{5,20})/count/$', UsernameCountView.as_view()),#注册时判断用户名是否存在
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', MobileCountView.as_view()),#注册时判断手机号码是否存在
    url(r'^users/$', UserView.as_view()),#注册表单提交
    url(r'^authorizations/$', obtain_jwt_token),#注册成功后，用jwt的token,直接登陆成功,登陆页面直接请求
    url(r'^accounts/(?P<account>\w{4,20})/sms/token/$',SMSCodeToKenView.as_view()),#忘记密码找回密码需要发送短信
    url(r'^accounts/(?P<account>\w{4,20})/password/token/$',PasswordTokenView.as_view()),#忘记密码找回密码需要修改密码的token
    url(r'^users/(?P<pk>\d+)/password/$', PasswordView.as_view()),#忘记密码找回密码需要修改密码
    url(r'^user/$', UserDetailView.as_view()),#用户个人中心接口
    url(r'^emails/$', EmailView.as_view()),#邮箱验证
    url(r'^emails/verification/$', EmailVerifyView.as_view()),#邮箱激活
    url(r'^browse_histories/$', UserBrowsingHistoryView.as_view()),#历史浏览记录保存


]

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, base_name='addresses')

urlpatterns += router.urls
# POST /addresses/ 新建  -> create
# PUT /addresses/<pk>/ 修改  -> update
# GET /addresses/  查询  -> list
# DELETE /addresses/<pk>/  删除 -> destroy
# PUT /addresses/<pk>/status/ 设置默认 -> status
# PUT /addresses/<pk>/title/  设置标题 -> title