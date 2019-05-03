from django.template import Library
from app01 import models
from django.db.models import Count
from django.db.models.functions import TruncMonth

register = Library()


@register.inclusion_tag('left_menu.html')
def left_menu(username):
    user = models.UserInfo.objects.filter(username=username).first()
    blog = user.blog
    # 每一个分类及分类下的文章数
    # category_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values('name','c')
    # 查询当前个人站点下的每一个分类及分类下的文章数
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values_list('name', 'c',
                                                                                                       'pk')
    # print(category_list)

    # 查询当前个人站点下的每一个标签及标签下的文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count('article')).values_list('name', 'c', 'pk')
    # print(tag_list)
    # 按日期归档  # 需要加filter(blog=blog)
    date_list = models.Tag.objects.filter(blog=blog).annotate(month=TruncMonth('article__create_time')).values(
        'month').annotate(c=Count('article')).values_list('month', 'c')
    # 正常应该从article表去做日期归档
    # date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values('month').annotate(
    #     c=Count('pk')).values_list('month', 'c')
    return {'username': username, 'category_list': category_list, 'tag_list': tag_list, 'date_list': date_list}
