import pickle,base64
from django_redis import get_redis_connection



#登录合并购物车
def merge_cart_cookie_to_redis(request,response,user):
    # 从cookie中取出购物车数据
    cookie_cart = request.COOKIES.get('cart')  # type:str
    if not cookie_cart:
        return response
    # 对cookie数据进行解析
    cookie_cart = pickle.loads(base64.b64decode(cookie_cart.encode()))#type:dict
    # 从redis中取出购物车数据
    redis_conn=get_redis_connection('cart')
    cart_redis=redis_conn.hgetall('cart_%s' %user.id)#type:dict
    #将cart_redis中的数据即键值对(bytes)转换int
    cart = {}
    for sku_id,count in cart_redis.items():
        cart[int(sku_id)]=int(count)

    #{
    #  "sku_id":count,
    #  "sku_id":count
    # }
    #遍历cookie中数据
    selected_list=[]
    for sku_id,selected_count_dict in cookie_cart.items():
        #相当于覆盖redis中的数据，如果有相同的键，那么覆盖它的值，如果没有，新添加
        cart[sku_id]=selected_count_dict['count']
        #处理勾选状态
        if selected_count_dict['selected']:
            selected_list.append(sku_id)
    # 将cookie的数据合并到redis中
    pl=redis_conn.pipeline()
    pl.hmset("cart_%s" %user.id,cart)
    pl.sadd('selected_count_%s' %user.id,*selected_list)
    pl.execute()
    # 清除cookie中的购物车数据
    response.delete_cookie('cart')
    return response




