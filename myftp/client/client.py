import socket
import json
import struct
import os
import file_tool
"""
    request表示请求(就是客户端给服务器发的)  
    response表示响应(服务器给客户端返回的)
    0.建立与服务器的连接 
    1.显示所有的功能
    2.接收用户输入 通过TCP 发给服务器
    3.接收服务器返回的响应数据
    4.将结果输出给用户    
    
    客户端用于验证是否登录的装饰器 
    服务器需要加健壮性判断  例如 客户端没有传输 需要的数据 username
    
"""

server_IP = "127.0.0.1"
server_Port = 8888

# 当前用户
current_user = None


# 建立连接
c = socket.socket()
try :
    c.connect((server_IP,server_Port))
    print("连接服务器成功!")
except:
    print("连接服务器失败 请检查网络设置..")
    exit(-1)



# 由于每一个函数都需要发送数据给服务器 并接收响应数据 可以提取为公共的函数

def send_request(dic):
    # 把字典转为json 统计长度 并发送
    json_data = json.dumps(dic).encode("utf-8")
    c.send(struct.pack("q",len(json_data)))
    c.send(json_data)

    # 接受服务器的响应数据
    l = struct.unpack("q",c.recv(8))[0]
    resp = json.loads(c.recv(l).decode("utf-8"))
    # 将接受到的响应数据返回给调用者自己来处理
    return resp


def login():
    global current_user
    # 接受用户输入
    user = input("用户名:")
    pwd = input("密码:")

    # 组装数据
    # 每一个请求必须都有一个固定key  func表示要执行的服务器端功能
    info = {"username":user,"pwd":pwd,"func":"login"}
    # 发送请求并获得响应
    resp = send_request(info)
    if resp["stat"]: # 登录成功记录当前用户
        current_user = user
    # 输出结果
    print(resp)


def register():
    # 接受用户输入
    user = input("用户名:")
    pwd = input("密码:")

    # 组装数据
    # 每一个请求必须都有一个固定key  func表示要执行的服务器端功能
    info = {"username": user, "pwd": pwd, "func": "register"}
    # 发送请求并获得响应
    resp = send_request(info)
    # 输出结果
    print(resp)


def download():
    """
    0.展示所有的文件名称
    1.输入文件名称
    2.把名字发给服务器
    my.py  my(1).py my(2).py
    3.判断是否存在,如果文件已存在 修改文件名加上[1]
    4.等着服务器返回文件数据
    """
    dic = {"username":current_user,"func":"list_file"}
    resp = send_request(dic)
    if not resp["names"]:
        print("您的服务器没有任何文件....")
        return

    print("您有以下文件:")
    for name in resp["names"]:
        print(name)

    while True:
        name = input("请输入文件名称:(q 退出)").strip()
        if name =="q":return
        if name in resp["names"]:
            # 开始下载前 判断文件名是否已经存在本地了
            if file_tool.exists_file(name,current_user):# 已经存在该文件了
                res = input("该文件已经下载过了 是否要重复下载?  y 继续 / 其他 取消").strip()
                if res != "y":
                    print("操作已取消!")
                    return
                else: # 需要重复下载
                    download_file(name,True)
            else:# 本地没有该文件 直接下载
                download_file(name)


def download_file(name,repeat=False):
    info = {"filename": name, "func": "download","username":current_user}
    resp = send_request(info)
    # 开始收文件数据
    recv_size = 0
    full_size = resp["size"]

    file_path = os.path.join("data",current_user,name)

    with open(file_path,"wb") as f:
        while recv_size < full_size:
            #90  100
            buffer = 1024
            # 剩余未收的数据 如果小于缓冲区大小  缓冲区大小就等于未收的数据大小
            if full_size - recv_size < buffer:
                buffer = full_size - recv_size
            data = c.recv(buffer)
            f.write(data)
            recv_size += len(data)
            print("\r已下载: %s%%" % str(recv_size / full_size * 100)[:4], end="")


    # 服务器最后会返回一个下载成功的字典
    # 接受服务器的响应数据
    l = struct.unpack("q", c.recv(8))[0]
    resp = json.loads(c.recv(l).decode("utf-8"))
    # 将接受到的响应数据返回给调用者自己来处理
    print(resp)


def upload():
    """
    1.接收需要上传的文件路径
    2.将需要上传的文件信息发送给服务器   服务器判断该文件是否已经上传
    3.服务器返回可以上传
        否则 打印错误信息
    4.开始上传文件
    """
    path = input("请输入要上传文件路径:").strip()
    # 路径必须是存在的  并且 不是一个文件夹
    if os.path.exists(path) and os.path.isfile(path):
        # 打包文件信息md5 文件名字 大小
        file_info = {}
        file_info["md5"] = file_tool.getMD5(path)
        file_info["filename"] = os.path.basename(path)
        file_info["size"] = os.path.getsize(path)
        file_info["func"] = "upload"
        file_info["username"] = current_user

        # 服务器必须返回一个key表示是否可以上传
        resp = send_request(file_info)
        if resp["ready"]:
            # 开始上传
            resp = send_file(path)
            print(resp)
        else:
            print("error: ",resp["msg"])
    else:
        print("error:  路径必须存在 并且不能是一个文件夹!")


    pass

def list_file():
    dic = {"username":current_user,"func":"list_file"}
    resp = send_request(dic)
    print(resp)


# 发送数据文件
def send_file(path):
    # 文件总大小
    full_size = os.path.getsize(path)
    send_size = 0
    with open(path,"rb") as f:
        while True:
            data = f.read(1024)
            if not data:break
            c.send(data)
            send_size += len(data)
            print("\r已上传: %s%%" % str(send_size / full_size * 100)[:4],end="")

    # 接受服务器的响应数据
    l = struct.unpack("q", c.recv(8))[0]
    resp = json.loads(c.recv(l).decode("utf-8"))
    # 将接受到的响应数据返回给调用者自己来处理
    return resp



while True:
    func_dic = {"1":login,"2":register,"3":upload,"4":download,"5":list_file}

    print("""
    请选择功能
    1.登录
    2.注册
    3.上传
    4.下载
    5.查看列表
    q.退出
    """)
    res = input(">>>>:")
    if res == "q":
        print("再见勇士...")
        break
    if res in func_dic:
        func_dic[res]()
    else:
        print("输入有误请重试!")

# 如果循环被跳过了 那就直接关闭连接
c.close()




