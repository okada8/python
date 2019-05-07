from db.old_db import Mymateclass,Field
class User(metaclass=Mymateclass):
    id=Field("id","int",True,True)
    name=Field("name","char(20)")
    password=Field("password","char(20)")
    isvip=Field("isvip","tinyint",default=0)
    locked=Field("locked","tinyint",default=0)
    user_type=Field("user_type","tinyint",default=0)
    def __init__(self,name,password,user_type=0,isvip=0,locked=0):
        self.name = name
        self.password = password
        self.user_type = user_type
        self.isvip = isvip
        self.locked = locked
class Notice(metaclass=Mymateclass):
    id = Field("id", "int", True, True)
    title = Field("title", "varchar(100)")
    content = Field("content", "varchar(1000)")
    send_time = Field("send_time","timestamp")
    user_id = Field("user_id", "int")
    def __init__(self,title,content,user_id):
        self.title = title
        self.content = content
        self.user_id = user_id

class Movie(metaclass=Mymateclass):
    id = Field("id","int",True,True)
    name = Field("name","char(20)")
    user_id = Field("user_id","int")
    up_time = Field("up_time","timestamp")
    size = Field("size","char(10)")
    MD5 = Field("md5","char(32)")
    path = Field("path","varchar(100)")
    vip = Field("vip","tinyint",default=0)

    def __init__(self,name,user_id,size,MD5,path):
        self.name = name
        self.user_id = user_id
        self.size = size
        self.MD5 = MD5
        self.path = path
