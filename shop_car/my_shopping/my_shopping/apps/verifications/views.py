from rest_framework.views import APIView
from my_shopping.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django.http.response import HttpResponse

from . import constants


class ImageCodeView(APIView):
    """
    图片验证码
    """

def get(self,image_code_id):
        name,text,image=captcha.generate_captcha()
        # print(name)
        # print(text)
        # print(image)
        # 获取redis连接对象
        redis_conn=get_redis_connection("verify_codes")
        redis_conn.setex("img_%s" %image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
        # path=r'G:\python\my_object\shop_car\front_end_pc\images\pic_code.jpg'
        # with open(path,'wb') as line:
        #     line.write(image)
        return HttpResponse(image,content_type="image/jpeg")


# if __name__ == '__main__':
#     s1=ImageCodeView()
    # get()




