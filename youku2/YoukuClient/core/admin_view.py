from lib.tool import print_error
from TCP import client
import os,json,struct
from lib.file_tool import getMD5
"""
1、登录 2、注册 3、上传普通视频，收费视频 4、删除视频 5、发布公告
"""

user_name = "rose"

def login():
    global user_name
    username = input("用户名:").strip()
    password= input("密码:").strip()
    # 打包json
    req = {"username":username,"pwd":password,"func":"admin_login"}
    response = client.send_request(req)
    if response["stat"]:
        user_name = username
    print(response)

def register():
    req = {"username": "rose", "pwd": "123", "func": "admin_register"}
    response = client.send_request(req)
    print(response)
    pass


def upload():
    if not user_name:
        print("请先登录!")
        return

    # 输入文件路径 进行判断
    path = input("请输入路径:").strip()
    if not(os.path.exists(path) and os.path.isfile(path)):
        print("路径错误! 必须保证是一个文件!!!!1")
    else:
        free = input("是否为免费视频(y:免费,输入其他其他表示收费):").strip()
        # 1表示 免费  0表示收费
        if free == "y":
            is_free = 1
        else:
            is_free = 0


        # 先检查是否可以上传
        check_info = {
                     "md5": getMD5(path),
                     "func": "check_video"}

        resp = client.send_request(check_info)

        print(resp)
        # 接收服务器返回的响应 来判断是否可以发送
        if resp["stat"]:
            # 如果可以发送 则打开文件 读取数据 发送到socke
            # 发送一条消息 包含两个信息  一个是告知服务器 要开始上传文件了 另一个是文件传完后 要交给哪个业务逻辑来处理
            # func 表示文件上传完成后交给一个upload_video这个函数处理 file表示这个请求不是一个普通请求是一个文件上传
            file_info = {"func":"upload_video",
                   "file":True,
                   "filename": os.path.basename(path),
                   "size": os.path.getsize(path),
                   "author": user_name,
                   "is_free": is_free}

            #client.send_request(file_info)

            upload_file(file_info,path)
        else:
            print(resp["msg"])

def upload_file(file_info,path):
    # 先发送文件信息
    soc = client.c_socket
    json_bytes = json.dumps(file_info).encode("utf-8")
    soc.send(struct.pack("q", len(json_bytes)))
    soc.send(json_bytes)

    # 发送文件数据
    full_size = os.path.getsize(path)

    send_size = 0
    with open(path,"rb") as f:
        while True:
            data = f.read(1024)
            if not data:break
            soc.send(data)
            send_size  += len(data)
            print("\r %s%%" % (send_size / full_size * 100),end="")

    print("上传完成!")

    # 接收响应数据
    len_data = soc.recv(8)
    lens = struct.unpack("q", len_data)[0]
    response = json.loads(soc.recv(lens).decode("utf-8"))
    print(response)















def delete():
    pass


def send_notice():
    pass


def views():
    func_dic = {"1": login, "2":register,"3":upload,"4":delete,"5":send_notice}
    while True:
        print("""请选择功能
1、登录 
2、注册 
3、上传视频
4、删除视频 
5、发布公告
q.退出""")
        res = input(">>>:").strip()
        if res == "q": return
        if res in func_dic:
            func_dic[res]()
        else:
            print_error("输入有误!")