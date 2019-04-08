# a="permanent_session_lifetime"
# print(a.upper())
from info.utils.captcha import captcha
from redis import StrictRedis




REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PASSWD = "qwer1234"

redis_store=StrictRedis(host=REDIS_HOST,port=REDIS_PORT,password=REDIS_PASSWD,decode_responses=True)
# name,text,image= captcha.generate_captcha()
res=redis_store.get("imageCodeId_6a80adce-f529-412e-b044-053a80704caa")
print(res)







#
# with open("a.jpg","wb") as line:
#     line.write(image)
#
#
# print(name,text)


















# print(base64.b64encode(os.urandom(48)))