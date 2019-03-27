from db.models import *
from db.old_db import Olddb

olddb=Olddb()

def login(dic):
    condition = "name = '%s' and password = '%s' and user_type = %s" % (dic["name"], dic["password"], dic["user_type"])
    objs = olddb.select_many(User,condition)
    if objs and objs[0].locked==0:
        return {"status": "ok", "msg": "登录成功!", "user": objs[0].__dict__}
    return {"status": "error", "msg": "登录失败!"}

def register(dic):
    condition ="name = %s and user_type = %s"
    args=(dic["name"],dic["user_type"])
    objs = olddb.select_many(User, condition, args)
    if objs:
        return {"status": "error", "msg": "用户名已存在!"}
    u1 = User(dic["name"], dic["password"], user_type=dic["user_type"])
    if olddb.save(u1):
        return {"status": "ok", "msg": "注册成功!"}
    return {"status": "error", "msg": "注册失败!"}

def push_notice():
    ns = olddb.select_many(Notice, condition="1 = 1 order by send_time desc", limit=(0, 1))
    return ns[0].__dict__









