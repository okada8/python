"""
存储  请求函数名称 与函数地址的对应关系

"""
from interface import admin_interface,user_interface
map_dic = {
    "user_login":user_interface.login,
    "user_register":user_interface.register,
    "admin_login":admin_interface.login,
    "admin_register":admin_interface.register,
    "check_video":admin_interface.check_video,
    "upload_video":admin_interface.upload_video,
    "get_videos":user_interface.get_videos,
    "download_video":user_interface.download_video
}