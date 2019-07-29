from . import home_user
from flask import render_template, request, redirect, session, flash, jsonify
from .forms import UserBaseForm, ModifyPassowrd, UserImg
from app.utils.qiniu.image_storage import storage


# /user
# user的默认界面
@home_user.route('/')
def index():
    from app.models import User
    id = session["user_id"]
    user = User.query.filter_by(id=id).first()
    return render_template("news/user.html", user=user)


@home_user.route('/logout')
def logout():
    session.pop("user_id", None)
    return redirect("/index/")


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
@home_user.route('/user_pic_info/', methods=["POST", "GET"])
def user_pic_info():
    form = UserImg()
    print("img")
    if request.method == "POST":
        print("POST")
        if form.validate_on_submit():
            file = request.files.get('url').read()
            key = storage(file)
            print(key)
            print(type(key))
            user = getUser()
            url_str = "http://pv875q204.bkt.clouddn.com/" + key
            user.avatar_url = url_str
            from app import db
            db.session.commit()
            # flash("修改失败！ ", "error")
    return render_template('news/user_pic_info.html', form=form, user=getUser())


# 我的关注
@home_user.route('/user_follow/<int:page>')
def user_follow(page=None):
    from app.models import User, News
    if page is None:
        page = 1
    # 获取当前用户
    user = getUser()
    # 获取粉丝并按照id升序排列,前者页码，后者每页最大数量
    # page_data = user.followers.order_by(User.id.asc()).paginate(page=page, per_page=4)
    # 获取所有关注
    page_data = user.followed.order_by(User.id.asc()).paginate(page=page, per_page=4)

    # 关注列表
    user_list = []
    # 关注用户的发布新闻数量
    news_count = []
    # 关注的人的新闻
    attention_count = []
    for v in page_data.items:
        user_list.append(v)
        # 单个关注人的新闻数量
        count = News.query.filter(News.user_id == v.id).count()
        news_count.append(count)
        # 取出单个关注的人
        attention = User.query.filter(User.id == v.id).first()
        # 关注的人的粉丝数量
        count = attention.followers.count()
        attention_count.append(count)
    return render_template('news/user_follow.html', user=getUser(), user_list=user_list, news_count=news_count,
                           attention_count=attention_count, page_data=page_data)


# 修改密码
@home_user.route('/user_pass_info/', methods=["GET", "POST"])
def user_pass_info():
    from app.models import User
    if request.method == "GET":
        form = ModifyPassowrd()
        print("GET")
    else:

        print("POST")
        form = ModifyPassowrd(formdata=request.form)
        if form.validate_on_submit():
            user = getUser()
            # 验证密码
            if user.check_password(form.data["oldPassword"]):
                user.password = form.data["newPassword"]
                from app import db
                db.session.commit()
                flash("提交成功", "ok")
            else:
                flash("密码错误", "error")

        print(form.errors)
    return render_template('news/user_pass_info.html', form=form)


# 我的收藏
@home_user.route('/user_collection/<int:page>')
def user_collection(page=None):
    from app.models import News
    if page is None:
        page = 1
    user = getUser()
    # 我收藏的新闻 一夜最多6项
    page_data = user.collection_news.order_by(News.id.asc()).paginate(page=page, per_page=6)
    return render_template('news/user_collection.html', page_data=page_data)


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


# 取关
@home_user.route('/unattention/<name>', methods=["GET", "POST"])
def unattention(name):
    from app.models import User
    print("取关...")
    # 取关的人
    usr = getUser()
    # 被取关的人
    user = User.query.filter(User.nick_name == name).first()
    # print(user.followers)
    print(usr)
    print(user)
    user.followers.remove(usr)
    from app import db
    db.session.commit()
    return jsonify({"msg": "true"})


# 关注
@home_user.route('/attention/<name>', methods=["POST", "GET"])
def attention(name):
    from app.models import User
    print("关注")
    # 关注的人
    usr = getUser()
    # 被关注的人
    user = User.query.filter(User.nick_name == name).first()
    user.followers.append(usr)
    from app import db
    db.session.commit()
    return jsonify({"msg": "true"})


# 进入别人的界面
@home_user.route('/atnuser/<name>,<int:page>')
def atnuser(name, page):
    from app.models import User, News
    user = getUser()
    idol = User.query.filter(User.nick_name == name).first()
    list = idol.followers.filter(User.id == user.id).first()
    if list is not None:
        is_attention = 'True'  # 记录是否被关注
    else:
        is_attention = "False"

    print(is_attention)
    page_data = idol.news_list.order_by(News.id.asc()).paginate(page=page, per_page=6)
    return render_template("news/other.html", user=user, idol=idol, page_data=page_data, is_attention=is_attention)


@home_user.before_request
def before_request():
    if "user_id" in session:
        pass
    else:
        return redirect("/index")
