"""
    1.创建socket服务器
    2.接收客户端的连接请求
    3.接收客户端发送的请求数据
    4.从请求数据中获取客户端需要执行的操作
    5.进行相应的处理
    6.返回处理的结果

"""
import socket
import struct
import json
import os
import file_tool

# 服务器地址
server_IP = "127.0.0.1"
server_Port = 8888

# 用户数据的路径
udata_path = os.path.join(os.path.dirname(__file__),"user.json")
if not os.path.exists(udata_path):
    with open(udata_path,"wb")as f:
        pass


# 创建TCP服务器
s = socket.socket()
s.bind((server_IP, server_Port))
s.listen()


# 无论客户端的请求是什么内容 都必须返回响应数据
def send_response(dic):
    # 把字典转为json 统计长度 并发送
    json_data = json.dumps(dic).encode("utf-8")
    c.send(struct.pack("q", len(json_data)))
    c.send(json_data)


# 一堆业务逻辑
def login(req):
    with open(udata_path,"rt",encoding="utf-8") as f:
        users = json.load(f)

    for u in users:
        if req["username"] == u["username"] and req["pwd"] == u["pwd"]:
            return {"msg": "登录成功!", "stat": True}
    return {"msg": "登录失败! 用户名或密码不正确!", "stat": False}



def register(req):
    # 先判断是否存在相同的用户名
    with open(udata_path, "rt", encoding="utf-8") as f:
        users = json.load(f)

    for u in users:
        if u["username"] == req["username"]:
            return {"msg": "注册失败! 用户名已存在!", "stat": False}

    # 把数据写回文件
    users.append({"username":req["username"],"pwd":req["pwd"]})
    with open(udata_path,"wt",encoding="utf-8") as f:
        json.dump(users,f)
    # 创建home
    file_tool.create_home_dir(req["username"])

    return {"msg": "注册成功!", "stat": True}


def download(req):
    """
    1.获取用户名 已经 文件名称 拼接完整路径
    2.打开文件发送即可
    3.返回一个传输完成..
    """
    path = os.path.join("root",req["username"],req["filename"])

    # 组装一个文件信息返回给客户端
    info = {"size":os.path.getsize(path)}
    send_response(info)

    # 发送文件数据
    c = req["client"]

    with open(path,"rb") as f:
        while True:
            data = f.read(1024)
            if not data:break
            c.send(data)

    return {"msg":"文件传输完成!","stat":True}


def upload(req):
    # 从req中读取文件大小 以及文件名称
    # 拼接路径   root+home+filename
    path = os.path.join("root",req["username"],req["filename"])
    if os.path.exists(path):
        return {"msg":"服务器已存在该文件!","ready":False}

    # 如果可以上传 必须返回ready为True
    # 函数的返回值 会自动返回客户端,
    # 问题是 一旦return 接收文件就无法处理了
    # 必须要返回数据 并且不能return 所以直接返回数据
    send_response({"ready":True})
    # 已接收的大小
    recv_size = 0
    # 总大小
    full_size = req["size"]
    # 从字典中拿出socket
    c = req["client"]
    # 打开文件
    with open(path,"wb") as f:
        while recv_size < full_size:
            buffer = 1024
            # 剩余未收的数据 如果小于缓冲区大小  缓冲区大小就等于未收的数据大小
            if full_size - recv_size < buffer:
                buffer = full_size - recv_size
            data = c.recv(buffer)
            f.write(data)
            recv_size += len(data)
    # 返回上传结果
    return  {"msg":"文件上传成功","stat":True}


def list_file(req):
    # 获取当前用户目录下的所有文件名 返回给客户端
    # 1.拼接home目录
    path = os.path.join("root",req["username"])
    # 2.遍历得到所有文件名称
    names = os.listdir(path)
    return {"names":names}


# 接收客户端的连接请求
while True:
    c,addr = s.accept()
    while True:
        try:
            # 先收长度
            length = struct.unpack("q", c.recv(8))[0]
            # 在收json
            request_dic = json.loads(c.recv(length).decode("utf-8"))
            # print(request_dic)
            # 判断客户单要执行的功能是否存在
            func_name = request_dic["func"]
            # globals 获取当前全局名称空间中所有可用的名称
            if func_name in globals():
                func = globals()[func_name]
                # 由于upload需要使用socket来读数据 所以把socket塞到字典里
                request_dic["client"] = c
                info = func(request_dic)
            else:
                # 返回错误信息
                info = {"msg": "功能不存在!!!", "stat": False}
            send_response(info)
        except ConnectionResetError:
            print("连接中断。。。。。")
            c.close()
            break
