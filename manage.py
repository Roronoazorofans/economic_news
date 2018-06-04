# coding=utf-8
from redis import StrictRedis
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import Config
from info import create_app, db, models # 这里导入models仅仅是为了让app知道models的存在
from info.models import User




app = create_app('dev')
# 集成flask_script
manager = Manager(app)
# 在迁移时让app和db建立关联
Migrate(app, db)
# 添加迁移脚本到脚本管理器
manager.add_command("mysql", MigrateCommand)




# 创建脚本, 使用脚本创建管理员用户
@manager.option('-n','-name',dest='name')
@manager.option('-p','-password',dest='password')
def createsuperuser(name, password):
    """创建超级管理员用户"""

    if not all([name, password]):
        print("参数不足")

    # 创建对象
    user = User()
    user.mobile = name
    user.nick_name = name
    user.password = password
    # 限定是管理员
    user.is_admin = True

    # 将创建的管理员用户添加到数据库
    try:
        db.session.add(user)
        db.session.commit()
        print("创建成功")
    except Exception as e:
        db.session.rollback()
        print(e)




if __name__ == '__main__':
    print(app.url_map)
    manager.run()
