# coding:utf8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import config

from app.home.home_user import home_user
from app.home.home_news import home_news
from app.home.home_index import home_index
from app.admin.admin_user import admin_user
from app.admin.admin_news import admin_news

from app.home.home_index import *
from app.home.home_news import *
from app.home.home_user import *


def create_app():
    app = Flask(__name__)
    # 加载配置文件
    app.config.from_object(config["development"])

    # 注册蓝图
    app.register_blueprint(home_news, url_prefix="/news")
    app.register_blueprint(home_index, url_prefix="/index")
    app.register_blueprint(home_user, url_prefix="/user")

    admin = NestableBlueprint('admin', __name__, url_prefix='/admin')
    admin.register_blueprint(admin_user, url_prefix="/user")
    admin.register_blueprint(admin_news, url_prefix="/news")
    app.register_blueprint(admin)


    return app


# 创建flask应用程序
app = create_app()
db = SQLAlchemy(app)
