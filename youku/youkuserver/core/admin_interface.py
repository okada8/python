from db.models import *
from db.old_db import Olddb
from conf import settings
import os.path,json,struct
from threading import Thread

olddb=Olddb()
unknow_err={"status":"error","msg":"系统繁忙，请重试"}

def send_notice(dic):
    notice=Notice(dic["title"],dic["content"],dic["user_id"])
    if olddb.save(notice):
        return {"status":"ok","msg":"你的公告已发送到全世界!"}
    return unknow_err

def get_all_user(dic):
    users=olddb.select_many(User,condition="user_type=0")
    res={"users":[i.__dict__ for i in users]}
    return res

def lock_user(dic):
    u=olddb.get(User,dic["user_id"])
    u.locked=1
    if olddb.update(u):
        return {"status":"ok","msg":"锁定成功!"}
    return unknow_err

def unlock_user(dic):
    u=olddb.get(User,dic["user_id"])
    u.locked=0
    if olddb.update(u):
        return {"status": "ok", "msg": "解锁成功!"}
    return unknow_err

def check_movie(dic):
    md5=dic["md5"]
    ms=olddb.select_many(Movie,"md5 = %s",(md5,))
    if ms:
        return {"status": "error", "msg": "文件已经存在!"}
    return {"status": "ok", "msg": "服务器准备接受文件!"}

def upload(dic):
    conn=dic["conn"]
    size=dic["size"]
    name=dic["name"]
    md5=dic["md5"]
    user_id=dic["user_id"]
    vip=dic["vip"]
    if not os.path.exists(settings.MOVIES_PATH):
        os.mkdir(settings.MOVIES_PATH)
    path=os.path.join(settings.MOVIES_PATH,name)

    def task():
        f=open(path,"wb")
        receive_size=0
        while receive_size <size:
            if size-receive_size<1024:
                data=conn.recv(size-receive_size)
            else:
                data=conn.recv(1024)
            receive_size+=len(data)
            f.write(data)
        m=Movie(name,user_id,size,md5,path)
        olddb.save(m)
        f.close()
        dic["rlist"].append(conn)
        json_data=json.dumps({"status":"ok","msg":"上传成功!"}).encode("utf-8")
        len_data = struct.pack("q", len(json_data))
        conn.send(len_data)
        conn.send(json_data)
    t=Thread(target=task)
    t.start()

def get_movie(dic):
    ms=olddb.select_many(Movie)
    return {"stats": "ok", "movies": [i.__dict__ for i in ms] if ms else []}
def delete_movie(dic):
    m=olddb.get(Movie,dic["id"])
    if olddb.delete(m):
        os.remove(m.path)
        return {"status":"ok"}
    return unknow_err