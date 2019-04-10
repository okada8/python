from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import create_app,db
from info.models import User


app=create_app("developement")
manager=Manager(app)
#将app和数据库关联
Migrate(app,db)
#将迁移命令添加到manage
manager.add_command('db',MigrateCommand)
#添加管理员命令行模式
@manager.option('-n','-username',dest="username")
@manager.option('-p','-password',dest="password")
@manager.option('-m','-mobile',dest="mobile")
def createadmin(username,password,mobile):
    if not all([username,password,mobile]):
        print("参数不足")
    user=User()
    user.nick_name=username
    user.password=password
    user.mobile=mobile
    user.is_admin=True
    try:
        db.session.add(user)
        db.session.commit()
        print("注册成功")
    except Exception as e:
        db.session.rollback()
        print("e")




if __name__ == '__main__':
    manager.run()