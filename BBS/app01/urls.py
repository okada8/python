from django.conf.urls import url
from django.views.static import serve
from django.conf import settings
from . import views

urlpatterns = [
    url(r'^register/', views.Register.as_view()),
    url(r'^login/', views.Login.as_view()),

    # 图片验证码相关路由
    url(r'^get_code/', views.ImageCodeView.as_view()),

    url(r'^home/',views.Home.as_view()),
    url(r'^set_password/',views.Set_Password.as_view()),
    url(r'^logout/',views.Logout.as_view()),

    # 手动添加对外开放的后端服务器资源
     url(r'^media/(?P<path>.*)',serve,{'document_root':settings.MEDIA_ROOT}),  # 固定写法 对外界开放服务器内部资源

    # 死亡的边缘试验  切记不要瞎试探
     #url(r'^app01/(?P<path>.*)',serve,{'document_root':settings.MEDIA_ROOT}),  # 固定写法 对外界开放服务器内部资源

    # 点赞点踩接口
     url(r'^up_or_down/',views.up_or_down),

    # 文章评论接口
     url(r'^comment/',views.comment),
    # 文章后台管理
     url(r'^backend/',views.backend),
    # 添加文章
     url(r'^add_article/',views.Add_article.as_view()),
    # 富文本编辑器上传图片
     url(r'^upload_img/',views.upload_img),

    # 修改用户头像
    url(r'^set_img/',views.set_img),

    # 个人站点  这个路径建议你放在最下面!!!
    url(r'^(?P<username>\w+)/$',views.site),
    # 左侧菜单栏筛选文章功能
    # url(r'(?P<username>\w+)/(?P<category>category)/(?P<param>\d+)/',views.site),
    # url(r'(?P<username>\w+)/tag/(?P<param>tag)/',views.site),
    # url(r'(?P<username>\w+)/archive/(?P<param>archive)/',views.site)
    # 一条搞定上面三条
    url(r'^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/',views.site),

    # 文章详情
    url(r'^(?P<username>\w+)/article/(?P<article_id>\d+)/',views.article_detail),


]