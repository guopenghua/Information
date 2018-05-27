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

    SECRET_KEY = "qwert"

    # flask_session的配置信息
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒