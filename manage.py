# coding=utf-8
from logging.handlers import RotatingFileHandler
from redis import StrictRedis
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import Config
from info import create_app, db
import logging

# 设置⽇日志的记录等级
logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建⽇日志记录器器，指明⽇日志保存的路路径、每个⽇日志⽂文件的最⼤大⼤大⼩小、保存的⽇日志⽂文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建⽇日志记录的格式 ⽇日志等级 输⼊入⽇日志信息的⽂文件名 ⾏行行数 ⽇日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的⽇日志记录器器设置⽇日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的⽇日志⼯工具对象（flask app使⽤用的）添加⽇日志记录器器
logging.getLogger().addHandler(file_log_handler)




app = create_app('dev')
# 集成flask_script
manager = Manager(app)
# 在迁移时让app和db建立关联
Migrate(app, db)
# 添加迁移脚本到脚本管理器
manager.add_command("db", MigrateCommand)

redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
@app.route('/')
def index():
    return 'index page'


if __name__ == '__main__':
    redis_store.set("name", "zoro")
    manager.run()
