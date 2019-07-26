from . import home_user
from flask import render_template, request, redirect, session, flash
from .forms import UserBaseForm, ModifyPassowrd


# 测试
@home_user.route('/test1')
def test1():
    return "user"


# /user
# user的默认界面
@home_user.route('/')
def index():
    from app.models import User
    id = session["user_id"]
    user = User.query.filter_by(id=id).first()
    return render_template("news/user.html", user=user)


# 基本信息
@home_user.route('/user_base/', methods=["GET", "POST"])
def user_base():
    user = getUser()
    user_id = user.id
    if request.method == "GET":
        form = UserBaseForm()
    else:
        form = UserBaseForm(formdata=request.form)
        if form.validate_on_submit():
            data = form.data
            user.signature = data["signature"]
            user.nick_name = data["nick_name"]
            print(data["gender"])
            user.gender = data["gender"]
            print(data["signature"])
            print(user.signature)
            from app import db
            db.session.commit()
            flash("修改成功！ ", "ok")

    return render_template("news/user_base_info.html", form=form, user=user)


# 头像设置
@home_user.route('/user_pic_info/')
def user_pic_info():
    return render_template('news/user_pic_info.html')


# 我的关注
@home_user.route('/user_follow/')
def user_follow():
    return render_template('news/user_follow.html', user=getUser())


# 修改密码
@home_user.route('/user_pass_info/', methods=["GET", "POST"])
def user_pass_info():
    if request.method == "GET":
        form = ModifyPassowrd()
        print("GET")
    else:
        print("POST")
        form = ModifyPassowrd(formdata=request.form)
        if form.validate_on_submit():
            print(form.data)
        print(form.errors)
    return render_template('news/user_pass_info.html', form=form)


# 我的收藏
@home_user.route('/user_collection/')
def user_collection():
    return render_template('news/user_collection.html')


# 新闻发布
@home_user.route('/user_news_release/')
def user_news_release():
    return render_template('news/user_news_release.html')


# 新闻列表
@home_user.route('/user_news_list/')
def user_news_list():
    return render_template('news/user_news_list.html')


def getUser():
    from app.models import User
    id = session["user_id"]
    user = User.query.filter_by(id=id).first()
    return user
