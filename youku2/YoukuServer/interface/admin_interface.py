from db.NB_DB.models import User,Video
from lib.file_tool import getMD5
def login(req):
    print(req,"admin_login")
    # 查询数据
    users = User.get("name = %s and password = %s and is_admin = 1",(req["username"],req["pwd"]))
    if not users:
        return  {"msg":"用户名或密码不正确!"}
    return {"msg":"登录成功!","stat":True}


def register(req):
    users = User.get("name = %s", (req["username"],))
    if users:
        return {"msg": "用户名已存在!"}
    else:
        u = User(name=req["username"],password=req["pwd"],is_admin=1)
        if u.save():
            return {"msg": "注册成功!"}
        else:
            return {"msg": "未知错误!"}

def check_video(req):
    # 查询数据库 是有相同的文件
    md5 = req["md5"]
    vs = Video.get("md5 = %s",(md5,))
    if vs: #已经存在相同的MD5文件
        return {"stat": False, "msg": "文件已存在!"}
    return {"stat": True, "msg": "服务器准备接受数据!"}



def upload_video(req):
    md5 = getMD5(req["temp_path"])
    v = Video(req["filename"],req["author"],req["temp_path"],md5,req["is_free"])
    if v.save():
        return  {"msg":"文件上传成功!"}
    return {"msg": "未知错误!"}













