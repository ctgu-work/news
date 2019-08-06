# coding=utf-8
import datetime
from . import admin_user
from flask import render_template, request, session, json, url_for, redirect, jsonify
from app.constants import *
from sqlalchemy import and_
from app.utils.response_code import RET


# 登录拦截
@admin_user.before_request
def check():
    if 'admin_name' not in session and "admin/user/login" not in request.url:
        return redirect("/admin/user/login")
    else:
        pass


# 登录
@admin_user.route('/login', methods=['GET', 'POST'])
def login():
    from app.models import User
    import app.models
    # POST请求
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter(and_(User.is_admin == 1, User.nick_name == username)).first()
        if user != None and user.check_password(password):
            session['admin_name'] = username
            return render_template('admin/index.html', user=user)
        else:
            msg = "用户名或密码错误"
            return render_template('admin/login.html', user=user, msg=msg)
    # GET请求
    if request.method == "GET":
        if 'admin_name' in session:
            session.pop('admin_name')
    return render_template('admin/login.html')


# 获取用户统计界面
@admin_user.route('/count')
def count():
    from app.models import User
    # 总人数
    total = User.query.count()
    # 月新增用户
    total_month = 0
    # 日新增用户
    total_day = 0
    user_list = User.query.all()
    now = datetime.datetime.now()
    for i in user_list:
        if (now - i.create_time).days < 30:
            total_month += 1
        if (now - i.create_time).days < 1:
            total_day += 1
    i = 1
    times = []
    nums = []
    # 获取最近12天的日期，并转化为str格式存到数组中
    while (i <= 12):
        t = now + datetime.timedelta(days=-i + 1)
    while (i <= 12):
        t = now + datetime.timedelta(days=-i + 1)
        times.append(str(t.strftime('%Y-%m-%d')))
        i += 1
    times = times[::-1]
    i = 0
    user_list = User.query.all()
    # 计算最近12天的用户活跃数量
    while (i < 12):
        count = 0
        for j in user_list:
            if (now - j.last_login).days > i - 1 and (now - j.last_login).days < i + 1:
                count += 1
        nums.append(count)
        i += 1
    nums = nums[::-1]
    return render_template('admin/user_count.html', total=total, total_month=total_month, total_day=total_day,
                           times=times, nums=nums)


# 获取用户列表界面
@admin_user.route('/list')
def list():
    from app.models import User
    cur_page = int(1)
    page = User.query.order_by(User.create_time.desc()).paginate(cur_page, ADMIN_USER_PAGE_MAX_COUNT)
    user_list = page.items
    total_page = page.pages
    return render_template('admin/user_list.html', user_list=user_list, cur_page=cur_page, total_page=total_page)


# 分页请求
@admin_user.route('/getList')
def getList():
    from app.models import User
    # 请求哪一页
    cur_page = int(request.args.get('p'))
    page = User.query.order_by(User.create_time.desc()).paginate(cur_page, ADMIN_USER_PAGE_MAX_COUNT)
    user_list = page.items
    total_page = page.pages
    return render_template('admin/user_list.html', user_list=user_list, cur_page=cur_page, total_page=total_page)
