# coding=utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import Config

app = Flask(__name__)

# 加载配置文件
app.config.from_object(Config)
# 创建连接到mysql数据库的对象
db = SQLAlchemy(app)
# 开启csrf保护
CSRFProtect(app)
Session(app)
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
