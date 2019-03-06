from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from blog import models
from utils.pagination import Pagination
from django.urls import reverse
from django.http import JsonResponse
import json
from django.db.models import F

# Create your views here.
def index(request, *args, **kwargs):
    # 查询所有的文章列表
    # article_list = models.Article.objects.all().order_by('-create_time')
    article_list = models.Article.objects.exclude(category__title='default').order_by('-create_time')
    data_count = article_list.count()
    page = Pagination(request.GET.get('p', 1), data_count)
    article_list = article_list[page.start:page.end]
    page_str = page.page_str(reverse('blog:index', kwargs=kwargs))
    return render(request, "index.html", {"article_list": article_list,
                                          "page_str": page_str})

def home(request, blog_site, *args, **kwargs):
    blog = models.Blog.objects.filter(site=blog_site).first()
    if not blog:
        return HttpResponse('404')
    user = blog.userinfo
    if not args:
        article_list = models.Article.objects.filter(user=user).exclude(category__title='default').order_by('-create_time')
    elif args[0] == "category":
        article_list = models.Article.objects.filter(user=user).filter(category__title = args[1]).exclude(category__title='default').order_by('-create_time')
    elif  args[0] == "tag":
        article_list = models.Article.objects.filter(user=user).filter(tags__title = args[1]).exclude(category__title='default').order_by('-create_time')
    else:
        # 按照日期归档
        try:
            year, month = args[1].split("-")
            article_list = models.Article.objects.filter(user=user).filter(
                create_time__year=year, create_time__month=month
            ).exclude(category__title='default').order_by('-create_time')
        except Exception as e:
            return HttpResponse("404")

    data_count = article_list.count()
    page = Pagination(request.GET.get('p', 1), data_count)
    article_list = article_list[page.start:page.end]
    page_str = page.page_str('/blog/%s.html'%blog.site)
    return render(request, 'home.html',{'user': user,
                               'blog': blog,
                               'article_list': article_list,
                                'page_str': page_str})

def get_article_detail(request, blog_site, article_index):
    blog = models.Blog.objects.filter(site=blog_site).first()
    if not blog:
        return HttpResponse(404)
    user = blog.userinfo
    article = models.Article.objects.filter(user=user, nid=article_index).first()
    article_detail = models.ArticleDetail.objects.filter(article=article).first()
    tag_list = models.Article2Tag.objects.filter(article=article).all()
    comment_list = models.Comment.objects.filter(article=article).all()
    prev_article = models.Article.objects.filter(user=user).filter(create_time__gt=article.create_time).first()
    next_article = models.Article.objects.filter(user=user).filter(create_time__lt=article.create_time).order_by('-create_time').first()
    return render(request, "article_detail.html", {'user': user,
                                                    'blog': blog,
                                                    'article': article,
                                                    'article_detail': article_detail,
                                                   'article_tags': tag_list,
                                                   'comment_list': comment_list,
                                                   'prev_article': prev_article,
                                                   'next_article': next_article})

def up_down(request):
    article_id = request.POST.get('article_id')
    is_up = json.loads(request.POST.get('is_up'))
    user = request.user
    response = {'state': True}

    try:
        models.ArticleUpDown.objects.create(user=user, article_id=article_id, is_up=is_up)
        if is_up:
            models.Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
        else:
            models.Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)

    except Exception as e:
        response["state"] = False
        response["fisrt_action"] = models.ArticleUpDown.objects.filter(user=user, article_id=article_id).first().is_up

    return JsonResponse(response)


def comment(request):
    pid = request.POST.get("pid")
    article_id = request.POST.get("article_id")
    content = request.POST.get("content")
    user_pk = request.user.pk
    response = {}
    if not pid:  # 根评论
        comment_obj = models.Comment.objects.create(article_id=article_id, user_id=user_pk, content=content)
    else:
        comment_obj = models.Comment.objects.create(article_id=article_id, user_id=user_pk, content=content,
                                                    parent_comment_id=pid)

    response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d")
    response["content"] = comment_obj.content
    response["username"] = comment_obj.user.username

    return JsonResponse(response)