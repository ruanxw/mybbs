from django import template
from blog import models
from django.db.models import Count

register = template.Library()


def month_list(user):
    articles = models.Article.objects.filter(user=user).all()
    year_month = set()   #设置集合，无重复元素
    for a in articles:
        year_month.add((a.create_time.year,a.create_time.month))  #把每篇文章的年、月以元组形式添加到集合中
    counter = {}.fromkeys(year_month,0)  #以元组作为key，初始化字典
    for a in articles:
        counter[(a.create_time.year,a.create_time.month)]+=1  # 按年月统计文章数目
    year_month_number = []  #初始化列表
    for key in counter:
        year_month_number.append([key[0],key[1],counter[key]])  # 把字典转化为（年，月，数目）元组为元素的列表
    year_month_number.sort(reverse=True)  # 排序
    return year_month_number  #返回字典context

@register.inclusion_tag("left_menu.html")
def get_left_menu(username):
    user = models.UserInfo.objects.filter(username=username).first()
    blog = user.blog
    # 查询文章分类及对应的文章数
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c").exclude(title='default')
    # 查文章标签及对应的文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c").exclude(title='default')

    # 按日期归档 #mysql
    # archive_list = models.Article.objects.filter(user=user).extra(
    #     select={"archive_ym": "date_format(create_time,'%%Y-%%m')"}
    # ).values("archive_ym").annotate(c=Count("nid")).values("archive_ym", "c")
    # 按日期归档 #sqlite3
    # archive_list = models.Article.objects.filter(user=user).raw(
    #     'select nid, count(nid) as num,strftime("%Y-%m",create_time) as ctime from blog_article group by strftime("%Y-%m",create_time) order by create_time desc' )
    archive_list = month_list(user)
    return {
        "blog_site": blog.site,
        "category_list" :category_list,
        "tag_list": tag_list,
        "archive_list": archive_list
    }
