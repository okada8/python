from  db.old_db import Olddb
from db.models import *
from threading import Thread

olddb=Olddb()
unknown_error = {"status": "error", "msg": "系统繁忙 请重试!"}

def open_vip(dic):
    u=olddb.get(User,dic["user_id"])
    u.isvip=1
    if olddb.update(u):
        return {"status":"ok","msg":"恭喜成为高级会员!"}
    return unknown_error

def show_notice(dic):
    noices=olddb.select_many(Notice)
    return {"notices":[i.__dict__ for i in noices] if noices else []}


def check_download(dic):
    u=olddb.get(User,dic["user_id"])
    m=olddb.get(Movie,dic["movie_id"])
    if u.isvip == 1:
        return {"status": "ok", "msg": "尊敬的快播会员 开始下载!"}
    elif u.isvip == 0 and m.vip == 0:
        return {"status": "ok", "msg": "免费的拿去看吧 臭屌丝!"}
    else:
        return {"status": "error", "msg": "这是收费的 傻屌!"}

def download(dic):
    m=olddb.get(Movie,dic["movie_id"])
    conn=dic["conn"]
    def task():
        size=int(m.size)
        send_size=0
        f=open(m.path,"rb")
        while send_size < size:
            data=f.read(1024)
            conn.send(data)
            send_size+=len(data)
        print("视频发送结束")
    Thread(target=task).start()

