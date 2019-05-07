"""
 用户功能：1、登录 2、注册 3、查看所有视频 4、下载普通视频 5、下载收费视频 6、查看公告 7、查看观影记,8.开通会员,9.充值
"""
from conf.client_settings import DOWN_DIR
from lib.tool import print_error
from TCP import client
import os
def download():
    # 获取文件列表
    req = {"func":"get_videos"}

    resp = client.send_request(req) # {"videos":[{v1},{v2},{v3}]}
    names = [v["name"] for v in resp["videos"]]
    if not names:
        print("还没有电影  过会儿再来看看!")
        return


    for i in names:
        print(i)

    n = input("video_name:").strip()
    if n not in names:
        print("电影不存在!")
        return

    file_info = client.send_request({"filename":n,"func":"download_video"})
    print(file_info)
    # file_info == {"filename":"上年黄飞鸿!","md5":"xxxx","size":1028}
    # TODO:调用下载

    recv_video(file_info)


def recv_video(file_info):
    soc = client.c_socket
    recv_size = 0
    size = file_info["size"]
    buuffer_size = 1024
    with open(os.path.join(DOWN_DIR,file_info["filename"]),"wb") as f:
        while recv_size < size:
            if size-recv_size < buuffer_size:
                buuffer_size = size-recv_size
            data = soc.recv(buuffer_size)
            f.write(data)
            recv_size += len(data)
            print("\r已下载%s%%" % (recv_size / size * 100),end="")

    print("%s下载完成!" % file_info["filename"])


















def views():
    func_dic = {"4": download}
    while True:
        print("""请选择功能
    4、下载视频 
    q.退出""")
        res = input(">>>:").strip()
        if res == "q": return
        if res in func_dic:
            func_dic[res]()
        else:
            print_error("输入有误!")


if __name__ == '__main__':
    names = ["我是黄飞鸿","你是渣渣辉","一起砍人吧"]
    # print(list(enumerate(names)))

    # for i,v in enumerate(names):
    #     i = str(i)
    #     print(i,v)
    # index = input("video index:")
    #


