from . import home_news
from flask import render_template, current_app, jsonify, abort, g, session, request, redirect, url_for
from functools import wraps
from app.utils.response_code import RET
from app import constants


# def User_login_req(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if "home_user" not in session:
#             return redirect(url_for("home_user.login", next=request.url))
#         return f(*args, **kwargs)  # 调用完以后给函数继承
#
#     return decorated_function


# 新闻，用户，排行详情展示
@home_news.route('/<int:news_id>')
def news_detail(news_id):
    from app.models import User, Comment, News, CommentLike, Category
    # 查询文章内容
    try:
        news = News.query.get(news_id)
        user_id = session.get("user_id")
        if user_id:
            print(user_id)
            user = User.query.get(user_id)
            session["user_id"] = user.id
        else:
            user = None
        print(user)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询异常")
    if not news:
        abort(404)

    # 浏览量
    news.clicks += 1

    # 查询点击排行数据
    try:
        desc_news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA, errmsg='没有新闻数据')

    # 按照点击量排行
    news_list = []
    for desc_news in desc_news_list if desc_news_list else []:
        news_list.append(desc_news.to_basic_dict())

    # 显示是否收藏
    is_collected = False
    # 显示是否关注
    is_followed = False
    if user:
        if news in user.collection_news:
            is_collected = True

        if news.user.followers.filter(user.id == user.id).count() > 0:
            is_followed = True

    # 查询该文章的评论列表,加用户是否点赞
    try:
        comment_list = Comment.query.filter(Comment.news_id == news_id).order_by(
            Comment.like_count.desc()).all()  # 评论对象列表
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    comment_like_ids = []
    if user:
        try:
            comment_ids = [comment.id for comment in comment_list]  # 获取当前文章的所有评论id
            if len(comment_ids) > 0:
                comments_user = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids),
                                                         CommentLike.user_id == user.id).all()  # 获取当前文章该用户的所有点赞记录
                comment_like_ids = [comment.comment_id for comment in comments_user]  # 从当前文章该用户的所有点赞记录中抽取评论id
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    comment_dict_list = []
    for each_comment in comment_list:
        comment_data = each_comment.to_dict()
        comment_data['is_like'] = False
        if user and comment_data['id'] in comment_like_ids:
            comment_data['is_like'] = True
        comment_dict_list.append(comment_data)

    print(comment_dict_list)
    data = {
        'news': news.to_dict(),
        'user': user.to_dict() if user else None,
        'news_list': news_list,
        'is_collected': is_collected,
        'comment_list': comment_dict_list,
        'is_followed': is_followed
    }

    return render_template("news/detail.html", data=data)


@home_news.route('/news_comment', methods=["POST"])
def new_comment():
    from app.models import User, Comment, News, CommentLike, Category
    from app import db

    user_id = session.get("user_id")
    user = User.query.get(user_id)
    print(user.to_dict())
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 1. 取到请求参数
    news_id = request.json.get("news_id")
    comment_content = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    print(news_id)
    print(comment_content)
    print(parent_id)
    # 2. 判断参数
    if not all([news_id, comment_content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 查询新闻，并判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到新闻数据")

    # 3. 初始化一个评论模型，并且赋值
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_content
    if parent_id:
        comment.parent_id = parent_id

    # 添加到数据库
    print(comment)
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    return jsonify(errno=RET.OK, errmsg="OK", data=comment.to_dict())


@home_news.route('/thumbs_up', methods=["POST"])
def thumbs_up():
    from app.models import User, Comment, News, CommentLike, Category
    from app import db

    user_id = session.get("user_id")
    user = User.query.get(user_id)

    if not user_id:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 获取参数
    comment_id = request.json.get("comment_id")
    # 触发事件
    action_things = request.json.get("action")

    # 判断
    if not all([comment_id, action_things]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有为空")
    # 取消和点赞触发事件
    if action_things not in ["add", "remove"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        comment_id = int(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 查询被点赞的评论
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

    # 判断
    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="没有评论数据")

    if action_things == "add":
        # 选出评论模型
        comment_like_model = CommentLike.query.filter(CommentLike.user_id == user.id,
                                                      CommentLike.comment_id == comment.id).first()

        if not comment_like_model:
            comment_like_model = CommentLike()
            comment_like_model.user_id = user.id
            comment_like_model.comment_id = comment.id
            # 往session中添加数据
            db.session.add(comment_like_model)
            comment.like_count += 1
    else:
        # 再次筛选评论模型
        comment_like_model = CommentLike.query.filter(CommentLike.user_id == user.id,
                                                      CommentLike.comment_id == comment.id).first()

        if comment_like_model:
        # 从session中清除数据
            db.session.delete(comment_like_model)

            comment.like_count -= 1

    try:
        # 插入提交数据
        db.session.commit()
    except Exception as e:
        # 数据库回滚
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库操作有误")

    return jsonify(errno=RET.OK, errmsg="OK")


# 收藏新闻
@home_news.route('/collect_news', methods=["POST"])
def collect_news():
    from app.models import User, Comment, News, CommentLike, Category
    from app import db

    user_id = session.get("user_id")
    user = User.query.get(user_id)
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 1. 接受参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 2. 判断参数
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ["collect", "remove_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到新闻数据")

    # 收藏以及取消收藏
    if action == "remove_collect":
        if news in user.collection_news:
            user.collection_news.remove(news)
    else:
        if news not in user.collection_news:
            user.collection_news.append(news)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存失败")

    return jsonify(errno=RET.OK, errmsg="操作成功")


# 关注用户
@home_news.route('/followed_user', methods=["POST"])
def followed_user():
    from app.models import User, Comment, News, CommentLike, Category
    from app import db

    user_id1 = session.get("user_id")
    user = User.query.get(user_id1)
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 1. 接受参数
    user_id = request.json.get("user_id")
    action = request.json.get("action")

    # 2. 判断参数
    if not all([user_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ["follow", "unfollow"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        user_id = int(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 判断新闻是否存在
    try:
        otherUser = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not otherUser:
        return jsonify(errno=RET.NODATA, errmsg="未查询到用户数据")

    # 收藏以及取消收藏
    if action == "unfollow":
        if otherUser in user.followers:
            user.followers.remove(otherUser)
    else:
        if otherUser not in user.followers:
            user.followers.append(otherUser)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存失败")

    return jsonify(errno=RET.OK, errmsg="操作成功")