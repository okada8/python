import pymysql
import time
from datetime import datetime

class Field:
    def __init__(self,name,column_type,pri_key=False,increment=False,default=None):
        self.name=name
        self.colum_type=column_type
        self.pri_key=pri_key
        self.increment=increment
        self.default=default

class Mymateclass(type):
    def __init__(self,classname,bases,namespace):
        table_name=classname
        colums=[]
        for k,filed in namespace.items():
            if isinstance(filed,Field):
                fs="%s %s" %(filed.name,filed.colum_type)
                if filed.pri_key:
                    fs += " primary key"
                    self.pri_key=filed.name
                if filed.increment:
                    fs+=" auto_increment"
                if filed.default != None:
                    if isinstance(filed.default,int):
                        fs+=" default %s" %filed.default
                    elif isinstance(filed.default,str):
                        fs+=" default '%s'" %filed.default
                    else:
                        raise TypeError("默认值是整形或字符串")
                colums.append(fs)
        colums=",".join(colums)
        sql = "create table %s(%s)" %(table_name,colums)
        olddb=Olddb()
        print(sql)
        olddb.conn.execute(sql)

class OldDBSingle(type):
    instance =None
    def __call__(cls, *args, **kwargs):
        if  OldDBSingle.instance == None:
            obj=object.__new__(cls)
            obj.__init__(*args, **kwargs)
            OldDBSingle.instance=obj
        return OldDBSingle.instance

class Olddb(metaclass=OldDBSingle):
    def __init__(self):
        self.conn = Connection()

    def save(self,obj):
        colums=[]
        valies=[]
        for k,v in obj.__dict__.items():
            colums.append(k)
            valies.append(v)
        colums=",".join(colums)
        fmt=["%s" for i in valies]
        fmt=",".join(fmt)
        sql="insert into %s(%s) values(%s)"%(obj.__class__.__name__,colums,fmt)
        return self.conn.execute(sql,valies)

    def delete(self,obj):
        table_name=obj.__class__.__name__
        sql="delete from %s where %s = %s"%(table_name,obj.__class__.pri_key,obj.id)
        return self.conn.execute(sql)

    def update(self,obj):
        cs=[]
        vs=[]
        for k,v in obj.__dict__.items():
            c="%s = "%k
            c+="%s"
            cs.append(c)
            vs.append(v)
        cs=",".join(cs)
        sql="update %s set %s where %s = %s"%(obj.__class__.__name__,cs,obj.__class__.pri_key,obj.id)
        return self.conn.execute(sql,tuple(vs))

    def get(self,cls,id):
        sql = "select * from %s where %s=%s"%(cls.__name__,cls.pri_key,id)
        res = self.conn.select(sql)
        if not res:return
        obj=object.__new__(cls)
        for k,v in res[0].items():
            obj.__dict__[k]=v
        return obj

    def select_many(self,cls,condition=None,args=None,limit=None):
        table_name=cls.__name__
        sql="select * from %s" %table_name
        if condition:
            sql +=" where %s"%condition
        if limit:
            sql+=" limit %s,%s"%(limit[0],limit[1])
        res=self.conn.select(sql,args)
        if not res:return
        objs=[]
        for dic in res:
            obj=object.__new__(cls)
            for k,v in dic.items():
                if isinstance(v,datetime):
                    v=str(v)
                obj.__dict__[k]=v
            objs.append(obj)
        return objs

class Connection:
    current_connect_count=0
    host="127.0.0.1"
    user="root"
    password="qwer1234"
    database="youku"
    charset="utf8"
    autocommit=True

    def create_conn(self):
        return pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset,
            autocommit=self.autocommit)

    def __init__(self,max_cconnect=10,retry_time=0.2):
        self.pool=[]
        self.retry_time=retry_time
        self.max_cconnect=max_cconnect
        try:
            for i in range(2):
                conn=self.create_conn()
                self.current_connect_count+=1
                self.pool.append(conn)
        except Exception as e:
            print("连接失败:",e)

    def execute(self,sql,args=None,is_select=False):
        while True:
            if not self.pool:
                if self.current_connect_count < self.max_cconnect:
                    conn=self.create_conn()
                    self.current_connect_count+=1
                    self.pool.append(conn)
                else:
                    time.sleep(self.retry_time)
            else:
                break
        conn = self.pool.pop()
        cursor=conn.cursor(pymysql.cursors.DictCursor)
        affect_row=0
        try:
            affect_row=cursor.execute(sql,args)
        except Exception as e:
            print(e)
            pass
        self.pool.append(conn)
        if is_select:
            return cursor.fetchall()
        return affect_row

    def select(self,sql,args=None):
        return self.execute(sql,args,is_select=True)


