# coding=utf-8
from redis import StrictRedis
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import Config
from info import create_app, db




app = create_app('dev')
# 集成flask_script
manager = Manager(app)
# 在迁移时让app和db建立关联
Migrate(app, db)
# 添加迁移脚本到脚本管理器
manager.add_command("db", MigrateCommand)


if __name__ == '__main__':
    manager.run()
