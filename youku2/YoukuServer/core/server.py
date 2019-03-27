import socket,select,struct,json
from conf.server_settings import *
from core.func_mapping import map_dic
from core.response import FileResponse

# 定义一个容器保存正在上传的文件信息   正在上传的文件信息 key是socket对象    value是文件信息  包含了 文件对象  已上传的大小
loading_data = {}

# 正在下载文件的socket 以及 其对应文件对象
downloading_data = {}


# 接收请求数据
def recv_request(c_socket):
    # 接收请求
    len_data = c_socket.recv(8)
    if not len_data:  # 无论对方是强行下线还是正常下线 处理方式都一样
        raise ConnectionResetError() # 当对方正常下线也抛出该异常  外界就可以统一处理
    lens = struct.unpack("q", len_data)[0]
    request_data = json.loads(c_socket.recv(lens).decode("utf-8"))
    return request_data

#返回响应数据
def sen_response(c_socket,response):
    json_bytes = json.dumps(response).encode("utf-8")
    c_socket.send(struct.pack("q", len(json_bytes)))
    c_socket.send(json_bytes)


def upload(request_data,c_socket):
    # 需要写入数据到文件中
    if request_data.get("fp"):  # 如果已经打开了文件则直接获取文件对象进行写入
        f = request_data["fp"]
    else:  # 如果没有则打开新文件
        temp_path = os.path.join(TEMP_DIR, request_data["filename"])
        request_data["temp_path"] = temp_path
        f = open(temp_path, "wb")
        request_data["fp"] = f


    if not request_data.get("recv_size"):
        request_data["recv_size"] = 0



    buffer_size = 1024
    if request_data.get("recv_size") < request_data["size"]:
        if request_data["size"] - request_data.get("recv_size") < buffer_size:
            buffer_size = request_data["size"] - request_data.get("recv_size")
        data = c_socket.recv(buffer_size)
        f.write(data)
        request_data["recv_size"] += len(data)


    if request_data.get("recv_size") == request_data["size"]:
        print("文件完毕")
        # 文件接收完成
        f.close()  #
        loading_data.pop(c_socket)  # 已经处理完成的则删除

        # 调用业务逻辑来处理这个文件
        func_name = request_data["func"]
        func = map_dic[func_name]
        resp = func(request_data)
        # 发送业务逻辑中返回的结果
        sen_response(c_socket,resp)


def working(c_socket):
    """接收请求  处理业务  返回响应"""
    # 判断这个saoket 在干什么  如果在上传文件则不应该接收json数据
    if c_socket in loading_data:
        upload(loading_data[c_socket],c_socket)
        return

    try:
        request_data = recv_request(c_socket)
    except ConnectionResetError:
        print("客户端断开了连接!")
        c_socket.close()
        r_list.remove(c_socket)
        return

    # 判断当前是上传文件 还是普通请求
    if request_data.get("file"):
        # 将文件的信息进行存储,并且需要知道那个socket正在接收文件数据
        loading_data[c_socket] = request_data
        return


    # 1.要获取请求中的 请求方法是什么
    func_name = request_data.get("func")
    if not func_name:
        response = {"msg":"error: must have a key : 'func'!"}
    # 2.根据请求方法 找到对应的函数并调用 并且需要请求数据交给这个函数
    elif func_name not in map_dic:
        response = {"msg": "error: funcName not exists!"}
    # 3.获取业务逻辑函数的返回值 发送给客户端
    else:
        handler_func = map_dic[func_name]
        # 调用处理函数 传入请求数据
        response = handler_func(request_data)

    # 判断响应类型
    if response.__class__ == FileResponse:
        sen_response(c_socket,response.resp)
        # 开始发送文件数据
        # 不能直接发送数据 应该每一次发送一部分数据 保证select可以一直循环处理所有请求
        f = open(response.file_path,"rb")
        downloading_data[c_socket] = f
        # 将需要发送文件的socket交给select来检测  每一次检测如果可以写入 那就写入一部分 然后判断是否写入完毕
        w_list.append(c_socket)
        pass
    else:
        sen_response(c_socket,response)

    # 发送响应之后在发送文件数据


    



r_list = []
w_list = []

def run_server():
    s_socket =  socket.socket()
    s_socket.bind((host,port))
    s_socket.listen()
    print("server is running....")
    # 接收连接请求
    # 多进程 多线程 协程  多路复用
    # 采用多路复用  可以支持一定的并发
    # 多路复用的实现:  将所有的socket装入列表中  在把列表交给select 来进行检测 select 会返回准备就绪的socket

    r_list.append(s_socket)

    while True:
        readables,writeables,_ =  select.select(r_list,w_list,[])
        # 发送数据是把数据丢到缓冲区 所以 一般 只有连接建立成功 所有socket都是可写的
        for c_socket in readables:
            if c_socket == s_socket:
                new_c,addr = s_socket.accept()
                r_list.append(new_c)
            else:
                working(c_socket)
        for c in writeables:
            # 取出socket 发送数据
            f = downloading_data[c]
            data = f.read(1024)
            if not data: # 判断如果发送完成  将这个socket从w_list中删除
                print("传输完成!")
                f.close()
                w_list.remove(c)
                downloading_data.pop(c)
            c.send(data)


