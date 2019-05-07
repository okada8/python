from django.shortcuts import render,HttpResponse,redirect
from django.views.generic import View
from . import myforms,models
from django.http import JsonResponse
from django.contrib import auth
from django.db.models import Count,F
from app01.utils.my_page import Pagination
from io import BytesIO, StringIO
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models.functions import TruncMonth
import random,json
import logging
# Create your views here.
logger=logging.getLogger('bbs')



#注册
class Register(View):

    def get(self,request):
        #利用forms组件
        form_obj = myforms.RegForm(request.GET)
        return render(request, 'register.html',locals())

    def post(self,request):
        response_msg = {'code': 100, 'msg': ''}
        #获取form对象
        form_obj = myforms.RegForm(request.POST)
        if form_obj.is_valid():
            #拿到传过来的值
            clean_data = form_obj.cleaned_data#type:dict
            # 删除确认密码的键值对
            clean_data.pop("confirm_password")
            # 获取用户上传的头像
            user_avatar = request.FILES.get('myfile')
            #如果用户上传了头像，没有就是默认值，在models中
            if user_avatar:
                #在字典中添加avatar键
                clean_data['avatar'] = user_avatar
            #创建用户
            models.UserInfo.objects.create_user(**clean_data)
            #组织上下文
            response_msg['msg'] = '注册成功'
            response_msg['url'] = '/login/'
        else:
            response_msg['code'] = 101
            response_msg['msg'] = form_obj.errors
        return JsonResponse(response_msg)

#登录
class Login(View):

    def get(self,request):
        return render(request, 'login.html')

    def post(self,request):
        response_dic = {'code': 100, 'msg': ''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        # 1.校验步骤1:比对验证码是否正确
        if request.session.get('code').upper() == code.upper():  # 统一转大写或者小写进行比对,实现忽略大小写
            # 2.校验用户名密码
            user = auth.authenticate(username=username, password=password)
            if user:
                # 3.验证通过 保存用户登录状态
                auth.login(request, user)  # request.session['user']  = user
                response_dic['msg'] = '登录成功'
                response_dic['url'] = '/home/'
            else:
                response_dic['code'] = 101
                response_dic['msg'] = '用户名或密码错误'
        else:
            response_dic['code'] = 102
            response_dic['msg'] = '验证码错误'
        return JsonResponse(response_dic)

#生成随机
def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

#图片验证码
class ImageCodeView(View):
    """
    图片验证码
    """
    def get(self,request):

        img = Image.new('RGB', (280, 35), get_random())
        img_draw = ImageDraw.Draw(img)  # 生成一个画笔,可以在img图片上为所欲为
        img_font = ImageFont.truetype('static/font/ooxx.ttf', 40)  # 定义字体样式

        # 写验证码  数字+小写字母+大写字母
        code = ''  # 存取验证码
        for i in range(5):
            random_num = str(random.randint(0, 9))
            random_upper = str(chr(random.randint(65, 90)))
            random_lower = str(chr(random.randint(97, 122)))
            # 随机选择一个字符写入图片上
            random_code = random.choice([random_num, random_upper, random_lower])
            img_draw.text((45 + i * 45, -10), random_code, get_random(), img_font)
            code += random_code
        logger.info(code)
        io_obj = BytesIO()
        # 将生成好的带有验证码的图片存入io_obj
        img.save(io_obj, 'png')
        # 将验证码记录下来以便后续比对  存入session以便后续比对
        request.session['code'] = code
        return HttpResponse(io_obj.getvalue())

#首页
class Home(View):
    def get(self,request):
        #查出所有文章列表
        article_list=models.Article.objects.all()
        return render(request,'home.html',locals())

#注销
class Logout(View):
    def get(self,request):
        auth.logout(request)
        return redirect('/home')

#修改密码
class Set_Password(View):
    def get(self,request):
        return render(request,'set_password.html')

    def post(self,request):
        #原始密码
        old_password = request.POST.get('old_password')
        #新密码
        new_password = request.POST.get('new_password')
        #第二次密码
        confirm_password = request.POST.get('confirm_password')
        #如果老密码验证通过
        if request.user.check_password(old_password):
            #如果两次密码一样
            if new_password == confirm_password:
                #更新密码
                request.user.set_password(new_password)
                request.user.save()  # 修改密码一定记得要save()一下
                return redirect('/login')



#添加文章
class Add_article(View):
    def post(self,request):
        title = request.POST.get('title')
        content = request.POST.get('content')
        soup = BeautifulSoup(content, 'html.parser')
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.decompose()

        desc = soup.text[0:150]
        # # 添加文章
        models.Article.objects.create(title=title, content=str(soup), desc=desc, blog=request.user.blog)
        # 用str(soup)传入数据库,
        return redirect('/backend/')

    def get(self,request):

        return render(request, 'backend/add_article.html')

def site(request,username,*args,**kwargs):
    print(kwargs)
    # 查询当前用户
    user = models.UserInfo.objects.filter(username=username).first()
    # 如果当前用户不存在,返回我们自定制的404页面
    if not user:
        return render(request,'errors.html')
    username = user.username
    blog = user.blog
    article_list = models.Article.objects.filter(blog=blog).all()
    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__id=param)
        else:
            year,month = param.split('-')
            article_list = article_list.filter(create_time__year=year,create_time__month=month)
    return render(request,'site.html',locals())


def article_detail(request, username, article_id):
    article = models.Article.objects.filter(pk=article_id).first()
    comment_list = models.Comment.objects.filter(article=article)
    return render(request, 'article_detail.html', locals())


def up_or_down(request):
    # print(request.is_ajax())  # 判断当前请求是否是一个ajax请求
    """
    1.先校验用户是否登录
    2.再校验用户是否已经点过
        2.1扩张功能,自己不能给自己文章点赞点踩
    3.存数据:你需要两个地方 一个是文章表普通字段,一个是点赞点踩表
    :param request:
    :return:
    """
    response_dic = {'code': 100, 'msg': ''}
    if request.is_ajax():
        # 1.先校验用户是否登录
        if request.user.is_authenticated():
            # 2.校验用户是否已经点过赞或者踩
            article_id = request.POST.get('article_id')
            is_up = request.POST.get('is_up')
            is_up = json.loads(is_up)  # 利用json序列化字符串形式的布尔值转成python后端的布尔值类型
            # print(type(is_up),is_up)
            res = models.UpAndDown.objects.filter(user=request.user, article_id=article_id)
            if not res:
                # 2.1 判断当前用户是否就是当前文章的作者
                article = models.Article.objects.filter(pk=article_id).first()
                if not article.blog.userinfo.pk == request.user.pk:
                    # 存数据 两个地方需要存
                    if is_up:
                        # 先去文章表操作点赞字段
                        models.Article.objects.filter(pk=article_id).update(up_num=F("up_num") + 1)
                        response_dic['msg'] = '点赞成功'
                    else:
                        # 先去文章表操作点踩字段
                        models.Article.objects.filter(pk=article_id).update(down_num=F("down_num") + 1)
                        response_dic['msg'] = '点踩成功'
                    # 去点赞点踩表记录数据
                    models.UpAndDown.objects.create(user=request.user, article_id=article_id, is_up=is_up)
                else:
                    response_dic['code'] = 103
                    response_dic['msg'] = '你个臭不要脸的,不能点自己的文章'
            else:
                # 小作业:提示用户到底是点赞还是点踩
                response_dic['code'] = 101
                response_dic['msg'] = '你已经点过了'
        else:
            # 扩展:用户点击登录可以直接跳转到登录页面
            response_dic['code'] = 102
            response_dic['msg'] = '请先登录'
        return JsonResponse(response_dic)


"""
事务:ACID
    原子性:全部成功才成功,一个失败全体回滚
    一致性
    隔离性
    持久性
django开启事务操纵评论数据更改

"""


def comment(request):
    response_dic = {'code': 100, 'msg': ''}
    if request.user.is_authenticated():
        article_id = request.POST.get('article_id')
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        # 利用django事务操作
        with transaction.atomic():
            # 文章表里面的评论字段加1
            models.Article.objects.filter(pk=article_id).update(comment_num=F("comment_num") + 1)
            # 新增评论表里面的数据
            models.Comment.objects.create(user=request.user, article_id=article_id, content=content,
                                          parent_id=parent_id)
        response_dic['msg'] = '评论成功'
    else:
        response_dic['code'] = 101
        response_dic['msg'] = '请登录'
    return JsonResponse(response_dic)


# 后台管理
# @login_required(login_url='/login/')
@login_required
def backend(request):
    article_list = models.Article.objects.filter(blog=request.user.blog).all()
    # 先生成一个分页器对象
    page_obj = Pagination(current_page=request.GET.get('page', 1), all_count=article_list.count())
    # 对整个queryset对象进行切片操作
    page_query = article_list[page_obj.start:page_obj.end]
    return render(request, 'backend/backend.html', locals())




from BBS import settings
import os


def upload_img(request):
    response_dic = {'error': '', 'message': ''}
    if request.method == 'POST':
        # print(request.FILES)  先打印查看键值对
        file_obj = request.FILES.get("imgFile")
        if file_obj:
            # 手动拼接文件存储路径
            path = os.path.join(settings.BASE_DIR, 'media', 'article_img')
            if not os.path.exists(path):
                # 文件夹不存在,手动创建
                os.mkdir(path)
            # 文件名
            file_path = os.path.join(path, file_obj.name)
            # 文件操作存储附文本编辑器上传的图片
            with open(file_path, 'wb') as f:
                for line in file_obj:
                    f.write(line)
            response_dic['error'] = 0
            response_dic['url'] = '/media/article_img/%s' % file_obj.name
            """
            //成功时
                {
                        "error" : 0,
                        "url" : "http://www.example.com/path/to/file.ext"
                }
                //失败时
                {
                        "error" : 1,
                        "message" : "错误信息"
                }

            """

        else:
            response_dic['error'] = 1
            response_dic['message'] = '文件不存在'
        return JsonResponse(response_dic)
    return HttpResponse("ooooook!")


def set_img(request):
    blog = request.user.blog
    username = request.user.username
    if request.method == 'POST':
        file = request.FILES.get('myfile')
        # 修改用户头像,必须使用用户对象点的方式来修改,不能用queryset的update方法
        user_obj = models.UserInfo.objects.get(blog=blog)
        user_obj.avatar = file
        user_obj.save()
        # models.UserInfo.objects.filter(blog=blog).update(avatar=file)  # 这种方式修改头像,不会自动再在图片前面加avatar前缀
    return render(request, 'set_img.html', locals())

#删除文章视图
class DelteView(View):
    def get(self,request,article_id):
        # 查出所有该id文章
        try:
            article = models.Article.objects.get(id=article_id)
        except models.Article.DoesNotExist:
            return render(request, 'errors.html')
        models.Article.delete(article)
        return redirect('/backend/')

#编辑文章
def EditArticle(request,article_id):
    #要修改哪篇文章
    if request.method == 'GET':
        # 查出所有该id文章
        try:
            article = models.Article.objects.get(id=article_id)
        except models.Article.DoesNotExist:
            return render(request, 'errors.html')
        #将该文章返回给前端
        return render(request,'edit_html.html',locals())
    #拿出数据
    article_title=request.POST.get('title')
    article_content=request.POST.get('content')
    #查到要修改的文章
    article=models.Article.objects.get(id=article_id)
    #更改属性
    article.title=article_title
    article.content=article_title
    #直接保存
    article.save()
    return redirect('/backend/')


































