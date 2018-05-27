from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


class Config(object):
    """配置文件的加载"""

    # 加载debug
    DEBUG = True

    # 配置mysql数据库的连接信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:gphmysql@127.0.0.1:3306/information"
    # 不去追踪数据库的修改
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置Redis数据库信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    SECRET_KEY = "qwert"

    # flask_session的配置信息
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒


app = Flask(__name__)

# 获取配置信息
app.config.from_object(Config)

# 创建连接到数据库的对象
db = SQLAlchemy(app)

# 创建连接到redis数据库的对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# 开启CSRF保护
CSRFProtect(app)

# 指定session数据存储在后端的位置
Session(app)

# 创建脚本管理器对象
manager = Manager(app)
# 让迁移和app和db建立关联
Migrate(app, db)
# 将数据库迁移的脚本添加到manager
manager.add_command("mysql", MigrateCommand)

@app.route('/')
def index():

    # 测试session
    from flask import session
    session["age"] = 2

    return "index"

if __name__ == '__main__':
    manager.run()
