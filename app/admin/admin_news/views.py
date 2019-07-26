from . import admin_news
from flask import render_template
from flask import request
from flask import jsonify
from flask import

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


@admin_news.route('/edit')
def edit():
    return render_template('admin/news_edit.html')


@admin_news.route('/type')
def type():
    return render_template('admin/news_type.html')

# 将review_detail分为两种请求
@admin_news.route('/review_detail',methods=['GET','POST'])
def review_detail():
    from app.models import News
    from app.models import Category

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
        action = request.json.get("action")
        news_id = request.json.get("news_id")
        # if not action and not news_id:



@admin_news.route('/edit_detail')
def edit_detail():
    return render_template('admin/news_edit_detail.html')
