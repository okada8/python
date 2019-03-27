import socket,select,struct,subprocess

w_list=[]
data_dic={}

def recv1(i,r_list):
    """
    接收请求
    :param i:有信息要接收的socket
    :param r_list: 有信息要接收的socket和等待接收信息的socket
    :return: 无返回值
    """
    datas = i.recv(8)
    if not datas:
        i.close()
        r_list.remove(i)
        return
    data_len=struct.unpack("q",datas)[0]
    data=i.recv(data_len).decode("utf-8")
    w_list.append(i)
    data_dic[i] = data




def send1():
    """
    执行命令并发送结果
    :return:
    """
    for q in w_list:
        try:
            obj=subprocess.Popen(data_dic[q],shell=True,stderr=-1,stdout=-1)
            res=obj.stderr.read()+obj.stdout.read()
            obj_len=struct.pack("q",len(res))
            q.send(obj_len)
            q.send(res)
        except ConnectionResetError as e:
            print(e)
            q.close()
        finally:
            data_dic.pop(q)
            w_list.remove(q)


if __name__ == '__main__':
    s=socket.socket()
    s.bind(("127.0.0.1",8848))
    s.listen()
    r_list=[s] #将socket加入空列表
    while True:
        red,wri,_=select.select(r_list,w_list,[])#监听发来的请求和能发送的请求
        for i in red:
            if i == s:#如果列表里的i是socket
                c,_=i.accept()#阻塞
                r_list.append(c)
            else:
                try:
                   recv1(i,r_list)
                except ConnectionResetError as e:
                    print(e)
                    i.close()
                    r_list.remove(i)

        if w_list: #如果有能发送的请求
            send1()