import json,socket,struct
from  concurrent.futures import ThreadPoolExecutor


def send_msg(soc,msg):
    print(msg)
    soc.send(struct.pack("q",len(msg)))
    soc.send(msg.encode("utf-8"))


def task(c):
    while True:
        l=c.recv(8)
        ls=struct.unpack("q",l)[0]
        j_data=json.loads(c.recv(ls).decode("utf-8"))
        # 客户端发过来的数据
        # 数据有两种情况 一种是发给所有人的 另一种单独发给某一个人的
        if j_data.get("to_addr"):
            to_addr=j_data["to_addr"]
            soc=clients.get(to_addr)
            send_msg(soc,j_data["msg"])
        else:
            # 遍历所有客户端 发给每一个人
            for k, soc in clients.items():
                send_msg(soc, j_data["msg"])


if __name__ == '__main__':
    s=socket.socket()
    s.bind(("127.0.0.1",8848))
    s.listen()
    clients={}
    pool=ThreadPoolExecutor(100)
    while True:
        c,add=s.accept()
        print("%s" % add[0], "连接到服务器!")#ip
        clients[add[0]] =c#将ip和socket绑定到字典
        pool.submit(task,c)


