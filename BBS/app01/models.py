from django.db import models
from django.contrib.auth.models import AbstractUser#导入auth模块创建用户的类
# Create your models here.



class UserInfo(AbstractUser):
    phone = models.BigIntegerField(null=True,blank=True)  # blank是用来告诉admin该字段可以为空.跟数据库没有关系,不要数据库迁移
    create_time = models.DateField(auto_now_add=True)
    avatar = models.FileField(upload_to='avatar/',default='avatar/default.jpg')
    blog = models.OneToOneField(to='Blog',null=True)

    class Meta:
        db_table = 'bs_user'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name


class Blog(models.Model):
    site_name = models.CharField(max_length=32)
    site_title =models.CharField(max_length=32)
    # 存css样式文件的路径
    theme = models.CharField(max_length=32)

    class Meta:
        db_table = 'bs_blog'
        verbose_name = '个人站点表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.site_name

class Category(models.Model):
    name = models.CharField(max_length=32)
    blog = models.ForeignKey(to='Blog')

    class Meta:
        db_table = 'bs_category'
        verbose_name = '文章分类表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=32)
    blog = models.ForeignKey(to='Blog')

    class Meta:
        db_table = 'bs_tag'
        verbose_name = '文章标签表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=32)
    desc = models.CharField(max_length=256)
    # 存大段文本
    content = models.TextField()
    create_time = models.DateField(auto_now_add=True)

    # 文章的评论数,点赞数,点踩数(优化点)
    comment_num = models.IntegerField(default=0)
    up_num = models.IntegerField(default=0)
    down_num = models.IntegerField(default=0)

    blog = models.ForeignKey(to='Blog',null=True)
    category = models.ForeignKey(to='Category',null=True)
    tags = models.ManyToManyField(to='Tag',through='Article2Tag',through_fields=('article','tag'))

    class Meta:
        db_table = 'bs_article'
        verbose_name = '文章表'
        verbose_name_plural = verbose_name


    def __str__(self):
        return self.title


class UpAndDown(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    is_up = models.BooleanField()

    class Meta:
        db_table = 'bs_upanddown'
        verbose_name = '点赞点踩表'
        verbose_name_plural = verbose_name

class Comment(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    content = models.CharField(max_length=128)
    parent = models.ForeignKey(to='self',null=True)
    create_time = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'bs_comment'
        verbose_name = '点赞点踩表'
        verbose_name_plural = verbose_name


class Article2Tag(models.Model):
    article = models.ForeignKey(to='Article')
    tag = models.ForeignKey(to='Tag')


