# coding=utf-8

# 抽取配置到配置文件中
# 创建配置文件
class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information_01"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    # 配置csrf秘钥 使用一组随机数作为'盐'
    SECRET_KEY = "q7pBNcWPgmF6BqB6b5VICF7z7pI+90o0O4CaJsFGjzRsYiya9SEgUDytXvzFsIaR"
    # 配置session数据
    # 配置存储session数据的数据库类型为redis
    SESSION_TYPE = "redis"
    # 开启用户签名
    SESSION_USE_SIGNER = True
    # 设置session有效期 为一天
    PERNAMENT_SESSION_LIFETIME = 3600*24
