from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
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
app = Flask(__name__)

# 获取配置信息
app.config.from_object(Config)

# 创建连接到数据库的对象
db = SQLAlchemy(app)

# 创建连接到redis数据库的对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)


@app.route('/')
def index():
    return "index"

if __name__ == '__main__':
    app.run()
