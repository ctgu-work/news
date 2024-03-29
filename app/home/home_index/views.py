from . import home_index
from flask import render_template, session, request, make_response, jsonify, current_app
from app.constants import CLICK_RANK_MAX_NEWS, HOME_PAGE_MAX_NEWS, SMS_CODE_REDIS_EXPIRES
from app.utils.response_code import RET, error_map
from app.utils.captcha.captcha import captcha
from app.lib.yuntongxun.sms import CCP
from datetime import datetime
# 引入正则表达验证 , 随机数
import re, random
import redis


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
    return render_template("news/index.html", user=user, categories=categories, news_list=news_list)


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
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 新闻的状态需要是 0 ，这样才是审核通过
    # 判断分类id是否等于1 ，1 表示 最新 新闻，不需要按类别查询 ，应该按时间排序所有的新闻
    filter_list = [News.status == 0]
    if cid != 1:
        filter_list.append(News.category_id == cid)
    try:
        # filter是python内置过滤函数
        # paginate是分页函数
        everypage = News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(cur_page, per_count)
    except BaseException as e:
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
    img_name, img_content, img_data = captcha.generate_captcha()
    response = make_response(img_data)
    response.content_type = "image/jpeg"
    # 将验证码存入redis
    # set_redis_data()
    # 将验证码存入session
    session[img_code_id] = img_content
    # 返回验证码图片
    return response


# 获取短信验证码
@home_index.route('/get_sms_code', methods=['POST'])
def getSmsCode():
    from app.models import User
    mobile = request.json.get("mobile")
    img_code = request.json.get("image_code")
    img_code_id = request.json.get("image_code_id")
    # 校验参数
    if not all([mobile, img_code, img_code_id]):
        # 返回参数错误
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    if not re.match(r"1[356789]\d{9}$", mobile):
        # 返回参数错误
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    real_img_code = session.get(img_code_id)
    print('发送短信验证码： ', real_img_code, img_code)
    if real_img_code != img_code.upper():
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    user = User.query.filter_by(mobile=mobile).first()
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg=error_map[RET.DATAEXIST])
    # 先从redis中获取
    sms_code = None
    try:
        sms_code = get_redis_data(mobile)
        print("先获取", sms_code)
    except Exception as e:
        print(e)

    if sms_code is None:  # 改手机号未设置验证码
        sms_code = random.randint(100000, 999999)  # 生成验证码
        response_code = CCP().send_template_sms(mobile, [sms_code], 1)  # 发送验证码
        # 存入redis
        set_redis_data(mobile, sms_code, SMS_CODE_REDIS_EXPIRES)  # 把验证码存在redis里
    else:
        time = None
        try:
            time = get_redis_time(mobile)
        except Exception as e:
            current_app.logger.exception('%s', e)
        if time == None:  # 为空
            return jsonify(errno=RET.UNKOWNERR, errmsg=error_map[RET.UNKOWNERR])
        elif time == -2:
            current_app.logger.exception('%s', user, "验证码过期")
            return jsonify(errno=RET.UNKOWNERR, errmsg="验证码过期")
        return jsonify(errno=RET.DATAEXIST, errmsg=("请在" + str(time) + "秒后重新发送"))
    print("response_code: ", response_code)
    print("sms_code: ", sms_code)
    print("获取设置的key: ", get_redis_data(mobile))
    session[mobile] = sms_code
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 注册
@home_index.route('/register', methods=['POST'])
def userRegister():
    from app.models import User
    from app import db
    mobile = request.json.get("mobile")
    password = request.json.get("password")
    sms_code = request.json.get("smsCode")
    # 校验参数
    if not all([mobile, password, sms_code]):
        # 返回参数错误
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    # 从redis中获取
    # real_sms_code = session.get(mobile)
    real_sms_code = get_redis_data(mobile)
    if str(real_sms_code) != str(sms_code):
        return jsonify(errno=RET.PARAMERR, errmsg="短信验证码错误")
    user = User()
    user.mobile = mobile
    user.password = password
    user.nick_name = mobile
    user.last_login = datetime.now()
    db.session.add(user)
    db.session.commit()
    session["user_id"] = user.id
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 登录
@home_index.route('/login', methods=['POST'])
def userLogin():
    from app.models import User
    mobile = request.json.get("mobile")
    password = request.json.get("password")
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    if not re.match(r"1[356789]\d{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    user = User.query.filter_by(mobile=mobile).first()
    # 不存在用户
    if not user:
        return jsonify(errno=RET.USERERR, errmsg=error_map[RET.USERERR])
    if not user.check_password(password):
        return jsonify(errno=RET.PARAMERR, errmsg="用户名或者密码错误")
    user.last_login = datetime.now()
    session["user_id"] = user.id
    current_app.logger.info('%s', user)
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 退出登录
@home_index.route('/logout')
def logout():
    # 删除session中的user_id
    session.pop("user_id", None)
    # 将结果以json返回
    return jsonify(errno=RET.OK, errmsg=error_map[RET.OK])


# 设置键值对存入redis
def set_redis_data(key, value, time):
    from app.utils.redis.redis import connect_redis
    conn = connect_redis()
    data = value
    conn.set(
        name=key,
        value=data,
        ex=time  # 第三个参数表示Redis过期时间,不设置则默认不过期
    )


# 获取key对应的value
def get_redis_data(key):
    from app.utils.redis.redis import connect_redis
    conn = connect_redis()
    v = conn.get(key)
    if v != None:
        value = v.decode()
    return value


# 获取key对应的事件
def get_redis_time(key):
    from app.utils.redis.redis import connect_redis
    conn = connect_redis()
    time = None
    try:
        time = conn.ttl(key)
    except Exception as e:
        print(e)
    return time
