from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import create_app,db


app=create_app("developement")
manager=Manager(app)
#将app和数据库关联
Migrate(app,db)
#将迁移命令添加到manage
manager.add_command('db',MigrateCommand)







if __name__ == '__main__':
    manager.run()