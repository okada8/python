"""
    生成建表语句
    在创建类的时候
"""
import pymysql
from db.NB_DB.DB_settings import *
import logging

class MyMeta(type):
    def __init__(self,cls_name,bases,namespace):
        table_name = cls_name # 把类名作为表名
        sql = "create table %s(" % table_name
        # 读取所有字段信息
        for k,v in namespace.items():
            # 包含了一些不是字段信息的值
            if isinstance(v,Field):
                text = ""
                text += v.name
                text = text + " " + v.column_type
                # 判断字段是否为主键
                if v.is_primary:
                    text = text + " primary key"
                if v.auto_increment:
                    text = text + " auto_increment"
                if v.default != None:
                    # 默认值是整型还是 字符串
                    if type(v.default) == int or type(v.default) == float:
                        text = text + " default " + str(v.default)
                        pass
                    elif type(v.default) == str:
                        text = text + (" default '%s'" % str(v.default))
                        pass
                    else:
                        raise TypeError("默认值必须为 字符或是数字")

                    # 把默认值拿出来判断是否mysql中的函数

                if v.constraint:
                    text = text + " " + v.constraint

                text += ","
                sql += text

        sql = sql.strip(",")
        sql += ");"
        # 创建一个连接器 执行sql创建表
        conn = Connector()
        try:
            count = conn.excute_sql(sql)
            if count:
                print("创建 %s 成功!" % table_name)
        except Exception as e:
            if debug:
                print("表已存在!!")
                print(type(e),e)

        super().__init__(cls_name,bases,namespace)
# 用于描述字段信息的类
class Field:
    def __init__(self,name,column_type,is_primary=False,auto_increment=False,default=None,constraint=None):
        """
        :param name:  字段名称
        :param column_type:  字段类型
        :param is_primary:  是否是主键
        :param auto_increment:  是否自增
        :param default:  默认值
        """
        self.name = name
        self.column_type = column_type
        self.is_primary = is_primary
        self.auto_increment = auto_increment
        self.default = default
        self.constraint =  constraint
class Connector:
    """
    用于连接数据库并执行sql语句
    """

    # 初始化  用于连接数据库
    def __init__(self):
        try:
            # 将连接对象作为属性  因为其他的函数中需要使用
            self.conn = pymysql.connect(host=host,
                                   port=port,user=user,
                                   password=password,
                                   database=database,
                                   autocommit=auto_commit)
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor) # 获取游标
            if debug:
                print("连接mysql成功!!!")
        except Exception as e:
            # 输出颜色为红色
            logging.error("连接数据库失败!")
            logging.error(type(e))
            logging.error(e)


    # 用于执行  删除 添加 修改  返回值是受影响的行数
    def excute_sql(self,sql,args=None,is_select = False):
        count = self.cursor.execute(sql,args) # count 表示受影响的行数  delete insert  update
        #self.conn.commit()
        if is_select:
            return self.cursor.fetchall()
        return count
class BaseModel:
    # 创建工具时 直接创建连接器 避免重复创建
    conn = Connector()
    """
    封装一个生成insert 语句的功能
    插入语句需要接受一个对象作为 参数 然后将对象中包含的数据 拿出来拼接成sql语句
    """
    def save(self):
        # print(obj.__dict__)
        #表名来自于类名
        # %s的个数 由对象的属性决定 id数据不需要从obj获取    总的属性个数-1
        ks = []
        vs = []
        for k,v in self.__dict__.items():
            ks.append(k)
            vs.append("%s")
        ks =  ",".join(ks)
        vs = ",".join(vs)

        sql = "insert into %s(%s) values (%s);" % (self.__class__.__name__,ks,vs)
        count = self.conn.excute_sql(sql,list(self.__dict__.values()))
        if count:
            return True

    def delete(self):
        """
        表名,条件 和 值
        :param obj: 要删除的对象
        :return:
        """
        t_name = self.__class__.__name__
        sql = "delete from "+t_name+" where id  = %s;"

        count = self.conn.excute_sql(sql,self.id)
        if count:
            print("删除成功!")
    def update(self):
        """
        :param new_obj:  包含了所有数据
        :return:
        """
        # u = User("张三","123")
        t_name = self.__class__.__name__
        ks = []
        vs = []
        for k,v in self.__dict__.items():
            if k == "id":continue
            t = "%s = %%s" % k
            ks.append(t)
            vs.append(v)

        kstext = ",".join(ks)
        sql = "update "+t_name+" set "+kstext+" where id = %s" % self.id
        # print(kstext)
        # print(vs)
        # print(sql)
        count = self.conn.excute_sql(sql,vs)
        if count:
            print("更新成功!")

    @classmethod
    def get(cls,condition=None,args=None,order_column=None,asc=True,limit=None):
        """
        :param cls:  要查询的类
        :param condition:  要查询的条件
        :param args: 查询的参数
        :param order_column:  排序的列
        :param asc:  默认为升序
        :param limit: 要获取的条数  (0,10)  (10,)
        :return:
        """
        t_name = cls.__name__
        sql = "select *from %s" % t_name
        if condition: #如果有条件
            sql += " where %s" % condition
        if order_column:#如果需要排序
            sql += " order by %s" % order_column
            if not asc: # 如果是降序
                sql += " desc"
        if limit:#如果需要分页
            if len(limit) == 1:# 仅有条数
                sql += " limit %s,%s" % (0, limit[0])
            elif len(limit) == 2: # 既有开始为止又有条数
                sql += " limit %s,%s" % (limit[0], limit[1])
            else:
                raise TypeError("limit 仅能接收1-2个值")

        print(sql)
        # 字典转对象
        objs = []
        data = cls.conn.excute_sql(sql,args,is_select=True) # 查询结果为一个列表 里面一堆字典
        for dic in data: #遍历字典 把每一个字典都转为以个对象 存储到列表中并返回
            obj = object.__new__(cls) # 创建空对象
            obj.__dict__.update(dic) #设置一系列属性
            objs.append(obj) # 加到列表中

        return objs # 返回列表























