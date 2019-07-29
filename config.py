# coding:utf8
class BaseConfig:
    DEBUG = True
    SECRET_KEY = "8A6C0D12FC0C23AE1390F26581CAE57D12B81B4C6C60C3D86D30BD8D77C1D445"

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@127.0.0.1:3306/news"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = "6379"


class DevelopmentConfig(BaseConfig):
    """开发环境"""
    pass


class ProductionConfig(BaseConfig):
    """生产环境"""
    DEBUG = False


class TestingConfig(BaseConfig):
    """生产环境"""
    pass


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}
