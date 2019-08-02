from . import admin_news
from flask import render_template,session,redirect
from flask import request
from flask import jsonify
from app.utils.response_code import RET
from app.utils.qiniu.image_storage import storage
from app import constants

@admin_news.before_request
def check():
    if 'admin_name' not in session and "admin/user/login" not in request.url:
        return redirect("/admin/user/login")
    else:
        pass

@admin_news.route('/index')
def index():
    return render_template("admin/index.html")

# 返回待审核页面
@admin_news.route('/review')
def review():
    from app.models import News
    # page:当前页，默认为1
    page = int(request.args.get("currentPage",1))
    # keywords:需要查询的标题，默认为空
    keywords = request.args.get("keywords","")

    # filters初始化为空，如果keywords不为空，则将keywords append 到filters
    filters = []
    try:
        if keywords != "":
            filters.append(News.title.contains(keywords))

        pageinate = News.query.filter(*filters).paginate(page,10,False)

        total = pageinate.pages
        currentPage = pageinate.page
        items = pageinate.items
    except Exception as e:
        print(e)
    # 查询逻辑到此结束

    # 初始化新闻List，并将每一项加入List
    newsList = []
    for new in items:
        newsList.append(new.to_review_dict())

    # 封装前端所需数据
    data = {
        "totalPage" : total,
        "currentPage" : currentPage,
        "newsList" : newsList
    }
    return render_template('admin/news_review.html',data=data)

# 将review_detail分为两种请求
@admin_news.route('/review_detail',methods=['GET','POST'])
def review_detail():
    from app.models import News
    from app.models import Category
    from app import db
    # GET
    if request.method == 'GET':
        # 取出新闻的Id
        news_id = request.args.get("news_id")
        try:
            # 查询
            news = News.query.get(news_id)
        except Exception as e:
            print(e)
            # 查询失败，返回错误信息。
            return render_template('admin/news_review_detail.html',data={"msg":"新闻查询失败"})
        if not news:
            # 没有这条新闻，返回不存在信息。
            return render_template('admin/news_review_detail.html',data={"msg":"新闻不存在"})
        # 查询分类名
        category = Category.query.get(news.category_id)
        # 封装新闻和分类
        data = {
            "news": news.to_dict(),
            "category" : category.name
        }
        # 返回data
        return render_template('admin/news_review_detail.html',data=data)
    # POST
    else:
        # 获取action和news_id
        action = request.json.get("action")
        news_id = request.json.get("news_id")
        # 判断参数是否正确
        if not all([news_id,action]):
            return jsonify(errno=RET.PARAMERR,msg="参数不全")
        # 判断action是否为["accept","reject"]
        if not action in["accept","reject"]:
            return jsonify(errno=RET.DATAERR,msg="操作类型错误")
        try:
            # 通过news_id查询新闻
            news = News.query.get(news_id)
        except Exception as e:
            # 获取失败返回
            return jsonify(errno=RET.DBERR,msg="新闻获取失败")
        if not news:
            # 不存在
            return jsonify(errno=RET.NODATA,msg="新闻不存在")
        # 通过验证，修改status
        if action == "accept":
            news.status = 0
        else:
            reason = request.json.get("reason")
            if not reason:
                return jsonify(errno=RET.PARAMERR,msg="参数不全")
            news.reason = reason
            news.status = -1

        try:
            # commit()
            db.session.commit()
        except Exception as e:
            # 回滚
            db.session.rollback()
            return jsonify(errno=RET.DBERR,msg="数据提交失败")
        # 返回成功
        return jsonify(errno=RET.OK,msg="success")

# 返回新闻编辑列表页面
@admin_news.route('/edit')
def edit():
    from app.models import News
    page = int(request.args.get("currentPage",1))
    # keywords:需要查询的标题，默认为空
    keywords = request.args.get("keywords","")

    # filters初始化为空，如果keywords不为空，则将keywords append 到filters
    filters = []
    try:
        if keywords != "":
            filters.append(News.title.contains(keywords))

        pageinate = News.query.filter(*filters).paginate(page,10,False)

        total = pageinate.pages
        currentPage = pageinate.page
        items = pageinate.items
    except Exception as e:
        print(e)
    # 查询逻辑到此结束

    # 初始化新闻List，并将每一项加入List
    newsList = []
    for new in items:
        newsList.append(new.to_dict())
    # 封装前端所需数据
    data = {
        "totalPage" : total,
        "currentPage" : currentPage,
        "newsList" : newsList
    }

    return render_template('admin/news_edit.html',data=data)

# 将edit_detail分为两种请求
@admin_news.route('/edit_detail',methods=['GET','POST'])
def edit_detail():
    from app.models import News
    from app.models import Category
    from app import db
    # 如果是GET请求
    if request.method == 'GET':
        news_id = request.args.get("news_id")
        if not news_id:
            return render_template("admin/news_edit_detail.html",data={"msg":"参数不全"})
        try:
            news = News.query.get(news_id)
        except Exception as e:
            return render_template('admin/news_edit_detail.html',data={"msg":"新闻获取失败"})
        if not news:
            return render_template('admin/news_edit_detail.html',data={"msg":"新闻不存在"})
        try:
            categories = Category.query.filter(Category.id != 1).all()
        except Exception as e:
            return render_template('admin/news_edit_detail.html',data={"msg":"分类查询失败"})
        category_list = []
        for category in categories:
            c = category.to_dict()
            c["selected"] = False
            if news.category_id == category.id:
                c["selected"] = True
            category_list.append(c)
        data = {
            "news":news.to_dict(),
            "category_list":category_list
        }
        return render_template('admin/news_edit_detail.html',data=data)

    # 如果是POST请求
    else:
        news_id = request.form.get("news_id")
        title = request.form.get("title")
        digest = request.form.get("digest")
        content = request.form.get("content")
        index_image = request.files.get("index_image")
        category_id = request.form.get("category_id")

        if not all([news_id,title,digest,content,category_id]):
            return jsonify(errno=RET.PARAMERR,msg="参数不全")
        try:
            news = News.query.get(news_id)
        except Exception as e:
            return jsonify(errno=RET.NODATA,msg="新闻不存在")
        if index_image:
            try:
                index_image_name = storage(index_image.read())
            except Exception as e:
                return jsonify(errno=RET.THIRDERR,msg="网络异常")
            if not index_image_name:
                return jsonify(errno=RET.NODATA,msg="上传图片失败")
            news.index_image_url = "http://pv875q204.bkt.clouddn.com/" + index_image_name



    news.title = title
    news.digest = digest
    news.category_id = category_id
    news.content = content
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    # 2.9: 返回响应
    return jsonify(errno=RET.OK,msg="操作成功")

# 返回新闻分类页面
@admin_news.route('/type')
def type():
    from app.models import Category

    categories = Category.query.filter(Category.id != 1).all()
    category_list = []
    for category in categories:
        category_list.append(category.to_dict())
    return render_template('admin/news_type.html',category_list=category_list)

# 修改/添加 新闻分类的操作
@admin_news.route('/type_handle',methods=['POST'])
def type_handle():
    from app.models import Category
    from app import db
    # 先将id和name取出，如果没有id，则为添加，反之为修改
    category_id = request.json.get("id")
    name = request.json.get("name")
    print(category_id)
    # 参数校验
    if not name:
        return  jsonify(errno=RET.PARAMERR,msg="参数不全")
    try:
        categories = Category.query.all()
    except Exception as e:
        return jsonify(errno=RET.DBERR,msg="分类查询失败")
    category_name = []
    for category in categories:
        category_name.append(category.name)
    # 判断是否有id
    if category_id:
        try:
            category = Category.query.get(category_id)
        except Exception as e:
            return jsonify(errno=RET.DBERR,msg="分类查询失败")

        if not category:
            return jsonify(errno=RET.NODATA, errmsg="分类不存在")
        # 判断更改的name是否存在
        if name in category_name:
            return jsonify(errno=RET.DATAEXIST, errmsg="分类重复,不能修改")
        # 更改
        category.name = name
    else:
        # 如果name已存在，则不能添加
        if name in category_name:
            return jsonify(errno=RET.DATAEXIST, errmsg="分类重复,不能添加")
        # 新建一个category
        category = Category()
        # 注入name
        category.name = name
        # 添加到数据库
        db.session.add(category)
    try:
        # 提交
        db.session.commit()
    except Exception as e:
        # 回滚
        db.session.rollback()
        return jsonify(errno=RET.DBERR,msg="数据保存失败")

    return jsonify(errno=RET.OK,msg="操作成功")


