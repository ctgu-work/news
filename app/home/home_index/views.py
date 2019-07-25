from . import home_index
from flask import current_app, render_template, session, request,make_response, jsonify
from app.constants import CLICK_RANK_MAX_NEWS, HOME_PAGE_MAX_NEWS
from app.utils.response_code import RET, error_map
from app.utils.captcha.captcha import captcha


# 跳转首页
@home_index.route('/')
def index():
    from app.models import User, News, Category
    user_id = session.get("user_id")
    user = None
    if user_id:
        user = User.query.get(user_id)
    # 将sqlAlchemy的对象转化为何json接近的dict对象(字典对象)
    user = user.to_dict() if user else None
    # 右侧的排行榜
    news_list = News.query.order_by(News.clicks.desc()).limit(CLICK_RANK_MAX_NEWS).all()
    news_list = [news.to_basic_dict() for news in news_list]
    # 查询所有的分类信息
    categories = Category.query.all()
    # 用户信息 ， 导航栏分类 ， 右侧排行榜
    return render_template("news/index.html", user=user , categories=categories , news_list=news_list)


# 获取主题面板新闻
@home_index.route('/get_news_list')
def get_news_list():
    from app.models import News
    # 获取参数
    cid = request.args.get("cid")  # 分类id
    cur_page = request.args.get("cur_page")  # 当前页码
    per_count = request.args.get("per_count", HOME_PAGE_MAX_NEWS)  # 每页条数
    # 传回参数错误响应信息
    if not all([cid, cur_page]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 格式化参数 否侧传回参数错误响应信息
    try:
        cid = int(cid)
        cur_page = int(cur_page)
        per_count = int(per_count)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 新闻的状态需要是 0 ，这样才是审核通过
    # 判断分类id是否等于1 ，1 表示 最新 新闻，不需要按类别查询 ，应该按时间排序所有的新闻
    filter_list = [News.status == 0]
    if cid != 1:
        filter_list.append(News.category_id == cid)
    try:
        # python内置过滤函数
        # paginate是分页函数
        everypage = News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(cur_page, per_count)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    data = {
        "news_list": [news.to_basic_dict() for news in everypage.items],
        "total_page": everypage.pages
    }
    # 返回json数组并返回成功响应
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK], data=data)


# 刷新图片验证码
@home_index.route('/get_image_code')
def getImageCode():
    img_code_id = request.args.get("img_code_id")
    # 打印发现该方法返回对象包括随机名字 , 验证码内容 , 和图片数据
    img_name , img_content , img_data = captcha.generate_captcha()
    response = make_response(img_data)
    response.content_type = "image/jpeg"
    # 将验证码存入session
    session['imgContent'] = img_content
    # 返回验证码图片
    return response

# 获取短信验证


# 登录
@home_index.route('/login')
def userLogin():
    return ""

# 注册
@home_index.route('/register')
def userRegister():
    return ""

# 退出登录
@home_index.route('/logout')
def logout():
    # 删除session中的user_id
    session.pop("user_id", None)
    # 将结果以json返回
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])
