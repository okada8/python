from rest_framework.pagination import PageNumberPagination
# #自定义分页器，需要继承父类，自定义属性
class StandarPageNumPagination(PageNumberPagination):
#     #如果你前端没有传每页容量是多少
    page_size = 2
#     #前端访问的路径的参数
    page_size_query_param = 'page_size'
#     #前端请求的每页数量上限
    max_page_size = 20




