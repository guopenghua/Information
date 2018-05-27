from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import app


# 创建脚本管理器对象
manager = Manager(app)
# # 让迁移和app和db建立关联
# Migrate(app, db)
# # 将数据库迁移的脚本添加到manager
# manager.add_command("mysql", MigrateCommand)


@app.route('/')
def index():

    return "index"

if __name__ == '__main__':
    manager.run()
