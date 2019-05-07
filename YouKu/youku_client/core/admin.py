from core import common
from Tcpclient import Tcpclient
import time,hashlib,json,struct,os
user={}
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

def get_MD5(path):
    size = os.path.getsize(path)
    f = open(path,"rb")
    # 如果文件小于1MB 就直接计算MD5
    m = hashlib.md5()
    if size < 1024 * 1024:
        m.update(f.read())
    else:
        # 取前1024字节
        data1 = f.read(1024)
        # 取最后1024字节
        f.seek(-1024,2)
        data2 = f.read(1024)
        # 取中间1024字节
        f.seek(size//2, 0)
        data3 = f.read(1024)
        m.update(data1)
        m.update(data2)
        m.update(data3)
    return m.hexdigest()

def login():
    userdata = common.login(1)
    if userdata:
        global user
        user = userdata["user"]

def register():
    common.register(1)

@user_auth
def send_notice():
    while True:
        title = input("请输入标题:>>>>")
        if not title:
            print("标题不能为空!")
            continue
        content = input("请输入内容:>>>>")
        if not content:
            print("内容不能为空!")
            continue
        request_data = {"title":title,
                        "content":content,
                        "user_id":user["id"],
                        "type":"admin",
                        "method":"send_notice"}
        response = Tcpclient.request(request_data)
        return
@user_auth
def lock_user():
    # 第一步 获取所有用户信息
    # 选择一个用户id
    # 发送给服务器
    request_data = {
                    "type": "admin",
                    "method": "get_all_user"}
    response = Tcpclient.request(request_data)
    print("id name locked")
    for u in response["users"]:
        print("%s %s %s" % (u["id"],u["name"],u["locked"]))
    id = int(input("请选择要锁定账户编号:"))
    isd = [u["id"] for u in response["users"]]
    print(isd)
    if id in [u["id"] for u in response["users"]]:
        # 根据id取到用户
        for u in response["users"]:
            if u["id"] == id:
                # 判断这个用户的锁定状态
                if u["locked"] == 1:
                    print("该账户已被锁定!")
                    break
        else:
            # 是一个正确id 并且没有被锁定
            # 将id发送给服务器 进行锁定
            response = Tcpclient.request({"type":"admin","method":"lock_user","user_id":id})
            print(response)
    else:
        print("输入的id不正确")
@user_auth
def unlock_user():
    request_data = {
        "type": "admin",
        "method": "get_all_user"}
    response = Tcpclient.request(request_data)
    print("id name locked")
    for u in response["users"]:
        print("%s %s %s" % (u["id"], u["name"], u["locked"]))
    id = int(input("请选择要锁定账户编号:"))
    if id in [u["id"] for u in response["users"]]:
        # 根据id取到用户
        for u in response["users"]:
            if u["id"] == id:
                # 判断这个用户的锁定状态
                if u["locked"] == 0:
                    print("该账户未锁定")
                    break
        else:
            # 是一个正确id 并且没有被锁定
            # 将id发送给服务器 进行锁定
            response = Tcpclient.request({"type": "admin", "method": "unlock_user", "user_id": id})
            print(response)
    else:
        print("输入的id不正确")


@user_auth
def upload_movie():
    filepath = input("请输入文件路径:").strip()
    if not os.path.exists(filepath):
        print("警告:路径不存在!")
        return
    if not os.path.isfile(filepath):
        print("警告:只能上传文件!")
        return
    suffixs = ["mp4","mkv","mov","rmvb","avi"]
    if not filepath.split(".")[-1] in suffixs:
        print("警告:不支持改格式的上传!")
        return
    md5 = get_MD5(filepath)


    request_data = {
        "type": "admin",
        "method": "check_movie",
        "md5":md5}
    response = Tcpclient.request(request_data)
    if response["status"] == "ok":
        name = os.path.split(filepath)[-1]
        size = os.path.getsize(filepath)
        vip = input("请输入是否收费,Y收费/输入其他免费").strip()
        if vip == "Y":
            vip = 1
        else:
            vip = 0
        print("开始上传")
        # 先发送文件信息给服务器
        file_info = {"name":name,
                     "size":size,
                     "md5":md5,
                     "user_id":user["id"],
                     "vip":vip,
                     "type": "admin",
                     "method": "upload",
                     }
        json_data = json.dumps(file_info).encode("utf-8")
        # 获取数据的长度
        len_data = struct.pack("i", len(json_data))
        # 发送长度 和  数据\
        Tcpclient.conn.send(len_data)
        Tcpclient.conn.send(json_data)
        # 开始上传
        f = open(filepath,"rb")
        #已发送的长度
        send_size = 0
        while send_size < size:
            data = f.read(1024)
            Tcpclient.conn.send(data)
            # time.sleep(0.01)
            send_size += len(data)
            print("\r已上传: %s%%" % str(send_size / size * 100)[:4], end="")
        print("上传完毕!")
        # 接受上传结果!
        len_data = Tcpclient.conn.recv(8)
        length = struct.unpack("q", len_data)[0]
        json_data = Tcpclient.conn.recv(length).decode("utf-8")
        dic = json.loads(json_data)
        print(dic)
    else:
        print(response)
@user_auth
def delete_movie():
    # 先查看所有的视频  选择一个id 传给服务器
    request_data = {
        "type": "admin",
        "method": "get_movies"}
    response = Tcpclient.request(request_data)
    if not response["movies"]:
        print("没有任何视频!")
        return
    ids = [d["id"] for d in response["movies"]]
    print(response)
    for m in response["movies"]:
        print("name:%s id:%s" % (m["name"],m["id"]))
    id = int(input("请输入要删除的视频id:").strip())
    if id in ids:
        request_data = {
            "type": "admin",
            "method": "delete_movie",
            "id":id}
        response = Tcpclient.request(request_data)
        if response["status"] =="ok":
            print("删除成功!")
        else:
            print(response)
    else:
        print(" error id 不存在!")

def admin_view():
    funcs = {"1":login,"2":register,"3":send_notice,"4":lock_user,"5":unlock_user,
             "6":upload_movie,"7":delete_movie}
    while True:
        print("""
1.登录
2.注册
3.发布公告
4.锁定账户
5.解锁账户
6.上传视频
7.删除视频 
""")
        res = input("请选择:>>>")
        if res == "q":
            break
        if res in funcs:
            funcs[res]()
        else:
            print("输入不正确!")