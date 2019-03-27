from db.NB_DB.NB_core import *


class User(BaseModel,metaclass=MyMeta):
    # user:  id  name password  VIP   is_admin  is_lock  balance
    # 一个字段不仅仅有 字段名称  还应该有类型  长度 约束 默认值等等  可以将一系列信息封装为对象
    id = Field("id","int",True,True)
    name = Field("name","char(20)",constraint="unique")
    password = Field("password","char(20)")
    VIP = Field("VIP","int",default=0)
    is_admin = Field("is_admin","int",default=0)
    is_lock = Field("is_lock","int",default=0)
    balance = Field("balance","int",default=0)



    # 该方法在创建对象时才执行  但我们需要在创建类的时候就要明确表有哪些字段
    # 必须把字段相关信息存储到类的名称空间中
    def __init__(self,name ,password , VIP=0,is_admin=0,is_lock=0, balance=0):
        self.name = name
        self.password = password
        self.VIP = VIP
        self.is_admin = is_admin
        self.is_lock = is_lock
        self.balance = balance
        pass

    def __str__(self):
        return  " class:%s  obj_name:%s" % (self.__class__.__name__,self.name)


class Video(BaseModel,metaclass=MyMeta):
    # video: name author  uptime  is_free  is_delete
    id = Field("id", "int", True, True)
    name = Field("name", "char(20)", constraint="unique")
    author = Field("author", "char(20)")
    uptime = Field("uptime", "timestamp")
    is_free = Field("is_free", "int")
    is_delete = Field("is_delete", "int",default=0)
    # 查看视频时  有可能要下载 就必须明确文件存在服务器的什么路径
    file_path = Field("file_path","varchar(200)")
    MD5 = Field("MD5","char(32)")

    def __init__(self,name,author,file_path,MD5,is_free=0,is_delete=0):
        self.name = name
        self.author = author
        self.is_free = is_free
        self.is_delete = is_delete
        self.MD5 = MD5
        self.file_path = file_path

    def to_json_dict(self):
        self.uptime = str(self.uptime)
        return self.__dict__