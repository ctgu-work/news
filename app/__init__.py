# coding:utf8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import config


def create_app():
    app = Flask(__name__)
    # 加载配置文件
    app.config.from_object(config["development"])

    # 注册蓝图

    # 初始化mysql

    return app


# 创建flask应用程序
app = create_app()
db = SQLAlchemy(app)
