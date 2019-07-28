from . import admin_news
from flask import render_template


@admin_news.route('/review')
def review():
    return render_template('admin/news_review.html')

@admin_news.route('/edit')
def edit():
    return render_template('admin/news_edit.html')

@admin_news.route('/type')
def type():
    return render_template('admin/news_type.html')