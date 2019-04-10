# # a="permanent_session_lifetime"
# # print(a.upper())
# from info.utils.captcha import captcha
# from redis import StrictRedis
# REDIS_HOST = "127.0.0.1"
# REDIS_PORT = 6379
# REDIS_PASSWD = "qwer1234"
# redis_store=StrictRedis(host=REDIS_HOST,port=REDIS_PORT,password=REDIS_PASSWD,decode_responses=True)
# # name,text,image= captcha.generate_captcha()
# res=redis_store.get("imageCodeId_6a80adce-f529-412e-b044-053a80704caa")
# print(res)
# with open("a.jpg","wb") as line:
#     line.write(image)
#print(name,text)
#添加测试用户
from info.models import User
from manage import app
from datetime import datetime,timedelta
import random
from info import db
def add_test_user():
    users=[]
    now=datetime.now()
    for num in range(3,10001):
        user = User()
        user.nick_name=num
        user.mobile=num
        users.append(user)
        user.last_login=now-timedelta(seconds=random.randint(0,2678400))
        user.password_hash="pbkdf2:sha256:50000$TYODLpnZ$28c863d49de09d6655a0c1d586d7a2964a6bb35794ba43d12a3e9fcdda5be52d"
    with app.app_context():
        db.session.add_all(users)
        db.session.commit()


if __name__ == '__main__':
    add_test_user()












# print(base64.b64encode(os.urandom(48)))