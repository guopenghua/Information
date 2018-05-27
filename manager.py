from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import Config
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


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
