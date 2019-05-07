import struct
import socket
import json
import select
from core import user_interface,common_interface,admin_interface


r_list=[]
w_list=[]


def resquest_recv(i):
    len_data = i.recv(8)
    length=struct.unpack("q",len_data)[0]
    json_data=i.recv(length).decode("utf-8")
    dic=json.loads(json_data)
    return dic

def response_send(i,response):

    json_data = json.dumps(response).encode("utf-8")
    len_data = struct.pack("q", len(json_data))
    i.send(len_data)
    i.send(json_data)



def working(i):
    dic=resquest_recv(i)
    if not dic:
        raise ConnectionResetError()

    dic["conn"]=i
    if dic["method"] == "upload":
        dic["rlist"] =r_list
        r_list.remove(i)
    if dic["type"] == "user":
        if dic["method"] in user_interface.__dict__:
            response=user_interface.__dict__[dic["method"]](dic)
        else:
            response={"status":"error","msg":"没有这个功能"}
    elif dic["type"] == "admin":
        if dic["method"] in admin_interface.__dict__:
            response =admin_interface.__dict__[dic["method"]](dic)
        else:
            response = {"status": "error", "msg": "没有这个功能"}
    elif dic["type"] == "common":
        if dic["method"] in common_interface.__dict__:
            response = common_interface.__dict__[dic["method"]](dic)
        else:
            response = {"status": "error", "msg": "没有这个功能"}
    else:
        print("请求类型错误")
    if dic["method"] == "upload" or dic["method"] == "download":
        return
    try:
        response_send(i,response)
    except ConnectionResetError as e:
        print(e)
        i.close()
        r_list.remove(i)
        return


def start_server():
    server=socket.socket()
    server.bind(("127.0.0.1",9998))
    server.listen()
    r_list.append(server)
    while True:
        red,wri,_=select.select(r_list,w_list,[])
        for i in red:
            if server == i:
                conn,addr=server.accept()
                r_list.append(conn)
            else:
                try:
                    working(i)
                except ConnectionResetError as e:
                    print(e)
                    i.close()
                    r_list.remove(i)
                    return


