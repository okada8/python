from db.NB_DB.models import Video
import os
from core import response

# 视图函数 == 业务逻辑处理函数
def login(request_data):
    """
    :param request_data: 请求数据
    :return: 响应数据
    """
    print("login")
    print(request_data)
    return  {"msg":"login success!"}


def register(request_data):
    """
    :param request_data: 请求数据
    :return: 响应数据
    """
    print("register")
    print(request_data)
    return  {"msg":"register success!"}



def get_videos(request_data):
    # 获取所有视频列表
    vs = Video.get()
    vs2 = [v.to_json_dict() for v in vs]

    resp = {"videos":vs2}
    return resp



def download_video(request_data):
    # 根据文件名称 获取文件信息 返回给客户端
    vs = Video.get("name = %s",(request_data["filename"],))
    if not vs:
        return {"msg":"视频 不存在!"}
    v = vs[0]
    size = os.path.getsize(v.file_path)
    resp = {"filename":v.name,"md5":v.MD5,"size":size}

    fsp = response.FileResponse(v.file_path,resp)
    return fsp










