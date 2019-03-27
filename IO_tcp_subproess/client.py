import socket,struct

def recv1(c):
    """
    用于接收服务端发来的劫夺
    :param c: 传入socket
    :return: 无返回值打印命令执行结果
    """
    data=c.recv(8)
    lens=struct.unpack("q",data)[0]#防止粘包
    res=c.recv(lens)
    print(res.decode("GBK"))#windows是gbk编码


def sendd(c,nsg):
    """
    用于发送命令
    :param c: socket
    :param nsg: 输入的命令
    :return:无返回值
    """
    lens_p=struct.pack("q",len(nsg))#防止粘包
    c.send(lens_p)
    c.send(nsg.encode("utf-8"))


if __name__ == '__main__':
    c=socket.socket()
    c.connect(("127.0.0.1",8848))
    while True:
        nsg=input(">>>:").strip()
        if not nsg:continue
        sendd(c,nsg)
        recv1(c)
