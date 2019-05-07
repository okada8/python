from Tcpclient import Tcpclient
from core import  common
import json,struct,os
from conf import settings


def user_auth(func):
    def inner(*args,**kwargs):
        if not user:
            print("请先登录")
            login()
            if user:
                return func(*args,**kwargs)
        else:
            return func(*args, **kwargs)
    return inner

user = None

def login():
    response = common.login(0)
    if response:
        global user
        user = response["user"]
def register():
    common.register(0)
@user_auth
def open_vip():
    if user["isvip"] == 1:
        print("您已经是会员了 土豪! 钱多可以直接转给我")
        return
    res = input("您开通老男孩视频VIP,价格100/月,输入Y确认,输入其他取消!")
    if res == "Y":
        request_data = {
            "type":"user",
            "method":"open_vip",
            "user_id":user["id"]
        }
        response = Tcpclient.request(request_data)
        print(response)
    else:
        print("操作取消!")
@user_auth
def show_movies():
    request_data = {
        "type": "admin",
        "method": "get_movies"}

    response = Tcpclient.request(request_data)
    if not response["movies"]:
        print("没有任何视频!")
        return
    for m in response["movies"]:
        print("name:%s id:%s" % (m["name"], m["id"]))
    return response
@user_auth
def download_movie():
    # 查看视频列表
    response = show_movies()
    if not response:
        return

    ids = [m["id"] for m in response["movies"]]

    id = input("请输入要下载的视频id:").strip()
    if not id.isdigit():
        print("输入不正确!")
        return
    id = int(id)
    if id not in ids:
        print("输入不正确!")
        return

    # 接收文件 取出文件信息
    movie = None
    for m in response["movies"]:
        if m["id"] == id:
            movie = m
    #判断文件夹是否存在
    if not os.path.exists(settings.MOVIES_PATH):
        os.mkdir(settings.MOVIES_PATH)
    #判断 本地是否已经存在这个文件!
    path = os.path.join(settings.MOVIES_PATH,movie["name"])
    if os.path.exists(path):
        print("文件已经下载!")
        return

    request_data = {"type":"user",
                    "method":"check_download",
                    "user_id":user["id"],
                    "movie_id":id}
    # 判断是否可以下载
    response = Tcpclient.request(request_data)
    if response["status"] != "ok":
        print(response)
        return
    # 确认可以进行下载  请求视频文件数据
    request_data["method"] = "download"
    json_data = json.dumps(request_data).encode("utf-8")
    # 获取数据的长度
    len_data = struct.pack("i", len(json_data))
    # 发送长度 和  数据
    Tcpclient.conn.send(len_data)
    Tcpclient.conn.send(json_data)

    name = movie["name"]
    size = int(movie["size"])
    receive_size = 0
    f = open(path,"wb")

    while receive_size < size:
        if size - receive_size < 1024:
            data = Tcpclient.conn.recv(size-receive_size)
        else:
            data = Tcpclient.conn.recv(1024)
        receive_size += len(data)
        f.write(data)
        print("\r已下载: %s%%" % str(receive_size / size * 100)[:4], end="")
    f.close()
    print("下载完成!")

@user_auth
def show_record():
    pass
@user_auth
def show_notice():
    request_data = {"type":"user",
                    "method":"show_notice"}
    response = Tcpclient.request(request_data)
    for n in response["notices"]:
        print("======%s======" % n["title"])
        print(n["content"])
        print("======%s======" % n["send_time"])

def user_view():
    funcs = {"1":login,"2":register,"3":open_vip,"4":show_movies,"5":download_movie,
             "6":show_record,"7":show_notice}
    while True:
        print("""
1.登录
2.注册
3.开会员
4.查看视频
5.下载视频 
6.查看下载记录    
7.查看公告
""")
        res = input("请选择:>>>")
        if res == "q":
            break
        if res in funcs:
            funcs[res]()
        else:
            print("输入不正确!")