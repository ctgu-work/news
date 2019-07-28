#coding=utf-8
import datetime

from . import admin_user
from flask import render_template,request,session,json
from app.constants import *

@admin_user.route('/login' , methods = ['GET','POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "admin" and password == "admin":
            return render_template('admin/index.html')

    return render_template('admin/login.html')

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
        if (now -i.create_time).days < 30:
            total_month += 1
        if (now - i.create_time).days < 1:
            total_day += 1
    i = 1
    times = []
    nums = []
    while(i <= 12):
        t = now + datetime.timedelta(days=-i+1)
        times.append(str(t.strftime('%Y-%m-%d')))
        i += 1
    times = times[::-1]
    i = 0
    user_list = User.query.all()
    while(i < 12):
        count = 0
        for j in user_list:
            if (now - j.last_login).days > i-1 and (now - j.last_login).days < i + 1:
                count += 1
        nums.append(count)
        i += 1
    nums = nums[::-1]
    return render_template('admin/user_count.html' , total = total , total_month = total_month , total_day = total_day , times = times , nums = nums)

@admin_user.route('/list')
def list():
    from app.models import User
    cur_page = int(1)
    page = User.query.order_by(User.create_time.desc()).paginate(cur_page, ADMIN_USER_PAGE_MAX_COUNT)
    user_list = page.items
    total_page = page.pages
    return render_template('admin/user_list.html',user_list = user_list , cur_page = cur_page , total_page = total_page)


@admin_user.route('/getList')
def getList():
    from app.models import User
    cur_page = int(request.args.get('p'))
    page = User.query.order_by(User.create_time.desc()).paginate(cur_page, ADMIN_USER_PAGE_MAX_COUNT)
    user_list = page.items
    total_page = page.pages
    return render_template('admin/user_list.html',user_list = user_list , cur_page = cur_page , total_page = total_page)

