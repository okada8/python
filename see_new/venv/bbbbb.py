import socket,json,struct
from threading import Thread


c = socket.socket()
c.connect(("127.0.0.1",8888))

name = input("输入你的昵称:").strip()
def recv_msg(c):
    while True:
        lens = struct.unpack("q", c.recv(8))[0]
        data = c.recv(lens)
        data_dic = json.loads(data.decode("utf-8"))
        print("用户 %s 来了新消息: %s"% (data_dic["name"],data_dic["msg"]))


def send_msg(c):
    while True:
        msg = input("聊天信息栏:").strip()
        if not msg:continue
        dic = {"msg":msg,"name":name}

        dic_bytes = json.dumps(dic).encode("utf-8")
        c.send(struct.pack("q", len(dic_bytes)))
        c.send(dic_bytes)

t1 = Thread(target=recv_msg,args=(c,))
t2 = Thread(target=send_msg,args=(c,))

t1.start()
t2.start()
