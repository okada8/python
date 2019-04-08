import socket,json,struct
from concurrent.futures import ThreadPoolExecutor

current_line = []
user = {}

pool = ThreadPoolExecutor(30)


def task(c,ip_addr):
    while True:
        try:
            lens = struct.unpack("q",c.recv(8))[0]
            data_bytes = c.recv(lens)  # 刚收到的字节数据
            data_dic = json.loads(data_bytes.decode("utf-8"))
            user[data_dic["name"]] = c
            user[c] = data_dic["name"]
            # 建一个字典 专门存名称对应socket    为了@时候的需求方便
            print(user)
            if "@"  not in data_dic["msg"]:
                for soc in current_line:
                    if soc!= c:
                        soc.send(struct.pack("q",len(data_bytes)))
                        soc.send(data_bytes)
            else:
                data = data_dic["msg"]
                msg_lst = data.split("@")
                # 找到对应的socket 然后发数据过去
                c_soc = user[msg_lst[1]]
                c_soc.send(struct.pack("q", len(data_bytes)))
                c_soc.send(data_bytes)
        except ConnectionResetError as e:
            current_line.remove(c)
            # data_dic["name"], data_dic["msg"]
            data_dic = {"name":user[c],"msg":"客户端已下线"}
            data_bytes = json.dumps(data_dic).encode("utf-8")
            for soc in current_line:
                soc.send(struct.pack("q", len(data_bytes)))
                soc.send(data_bytes)
            c.close()
            print("客户端已下线")
# 用@ 昵称找到 (建一个字典 专门存名称对应socket) 对应的socket
# 然后发  {"msg":msg,"name":name}  你好@兄弟
while True:
    s = socket.socket()
    s.bind(("127.0.0.1",8888))
    s.listen()
    c,addr = s.accept()
    #看一下有多少客户端连了过来
    print(addr)
    ip_fack = addr[1]
    current_line.append(c)
    # 看一下关闭的socket 还在不在
    print(current_line)
    pool.submit(task,c,ip_fack)
