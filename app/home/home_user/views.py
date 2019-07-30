from . import home_user
from flask import render_template, request, redirect, session, flash, jsonify, url_for, current_app
from .forms import UserBaseForm, ModifyPassowrd
from app.utils.response_code import RET
from app import constants

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


@home_user.route('/logout')
def logout():
    session.pop("user_id", None)
    # return render_template("news/index.html")
    return "该功能尚未协调完成"


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




def getUser():
    from app.models import User
    id = session["user_id"]
    user = User.query.filter_by(id=id).first()
    return user


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


@home_user.route('/examine_news_list/<int:page>')
def examine_news_list(page):
    from app.models import User,News

    # 1. 取参数
    examine_id = session["user_id"]

    # 2. 判断参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        examine = User.query.get(examine_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not examine:
        return jsonify(errno=RET.NODATA, errmsg="当前用户不存在")

    try:
        paginate = examine.news_list.order_by(News.create_time.desc()).paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        news_li = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    news_dict_li = []
    for news_li_item in news_li:
        news_dict_li.append(news_li_item.to_review_dict())


    # data = {
    #     "news_list": news_dict_li,
    #     "total_page": total_page,
    #     "current_page": current_page
    # }
    return render_template('news/user_news_list.html', news_list=news_dict_li, total_page = total_page, current_page  = current_page)


@home_user.route('/news_release', methods=["GET", "POST"])
def user_news_release():
    from app.models import User,Category, News

    from app.utils.qiniu.image_storage import storage

    from app import db


    if request.method == "GET":
        # 加载新闻分类数据
        categories = []
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)

        category_dict_li = []
        for category in categories:
            category_dict_li.append(category.to_dict())

        # 移除最新的分类
        category_dict_li.pop(0)

        return render_template('news/user_news_release.html', data={"categories": category_dict_li})

    # 取参数
    user_id = session["user_id"]
    # 1. 取到请求参数
    source = "个人发布" # 来源
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    index_image = request.files.get("index_image")
    content = request.form.get("content")
    # 参数转换
    try:
        category_id = int(category_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="参数有误")

    # 上传七牛云
    try:
        index_image_data = index_image.read()
        key = storage(index_image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="参数有误")

    # 2. 判断参数
    if not all([title, category_id, digest, index_image, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    new = News()
    new.title = title
    new.digest = digest
    new.source = source
    new.content = content
    new.index_image_url = "http://pv875q204.bkt.clouddn.com/" + key
    new.category_id = category_id
    new.user_id = user_id
    # 1代表待审核状态
    new.status = 1

    try:
        # 插入提交数据
        db.session.add(new)
        db.session.commit()
    except Exception as e:
        # 数据库回滚
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库操作有误")

    return jsonify(errno=RET.OK, errmsg="OK")


@home_user.route('/news_release1/<int:new_id>', methods=["GET", "POST"])
def user_news_release1(new_id):
    from app.models import User,Category, News

    from app.utils.qiniu.image_storage import storage

    from app import db

    if request.method == "GET":
        # 加载新闻数据
        news = News.query.get(new_id)
        session["new_id"] = new_id
        category = Category.query.get(news.category_id)
        print(category)
        data = {
            "news": news.to_dict(),
            "category": category.to_dict()
        }

        return render_template('news/user_news_release1.html', data=data)


@home_user.route('/news_release2', methods=["GET", "POST"])
def user_news_release2():
    from app.models import User, Category, News

    from app.utils.qiniu.image_storage import storage

    from app import db

    # 取参数
    new_id = session.get("new_id")
    news = News.query.get(new_id)
    user_id = session["user_id"]
    # 1. 取到请求参数
    source = "个人发布" # 来源
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    index_image = request.files.get("index_image")
    content = request.form.get("content")
    # 参数转换
    try:
        category_id = int(category_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="参数误")

    # 上传七牛云
    if index_image:
        index_image_data = index_image.read()
        key = storage(index_image_data)

    # # 2. 判断参数
    # if not all([title, category_id, digest, index_image, content]):
    #     return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    news.title = title
    news.digest = digest
    news.source = source
    news.content = content
    if not index_image:
        news.index_image_url = news.index_image_url
    else:
        news.index_image_url = "http://pv875q204.bkt.clouddn.com/" + key
    news.category_id = category_id
    news.user_id = user_id
    # 1代表待审核状态
    news.status = 1

    try:
        db.session.commit()
    except Exception as e:
        # 数据库回滚
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库操作有误")

    return jsonify(errno=RET.OK, errmsg="OK")