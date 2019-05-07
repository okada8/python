"""
建立连接
发送数据
接收响应
"""
import socket,json,struct
from conf.client_settings import *

c_socket = None
def connect_server():
    global c_socket
    c_socket = socket.socket()
    c_socket.connect((host,port))
    print("connect server success!")


def send_request(request_dic):
    if not c_socket:
        connect_server()

    # 发送请求
    json_bytes = json.dumps(request_dic).encode("utf-8")
    c_socket.send(struct.pack("q", len(json_bytes)))
    c_socket.send(json_bytes)


    # 接收响应数据
    try:
        len_data = c_socket.recv(8)
        if not len_data:  # 无论对方是强行下线还是正常下线 处理方式都一样
            raise ConnectionResetError()  # 当对方正常下线也抛出该异常  外界就可以统一处理
        lens = struct.unpack("q", len_data)[0]
        response = json.loads(c_socket.recv(lens).decode("utf-8"))
        return response
    except ConnectionResetError:
        print("服务器端断开了连接!")
        c_socket.close()





