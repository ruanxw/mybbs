from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from blog import models
from utils.pagination import Pagination
from django.urls import reverse
from backend.forms.article import ArticleForm
from django.db import transaction
from utils.xss import XSSFilter
from backend.auth.auth import check_have_blog
from bs4 import BeautifulSoup
import uuid

# Create your views here.
@login_required
def index(request):
    #print(request.user)
    # user = models.UserInfo.objects.get(username=request.user)
    # print(user)
    return render(request, "backend_index.html")

@login_required
@check_have_blog
def article(request, *args, **kwargs):
    """
    博客个人文章管理
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    user = models.UserInfo.objects.filter(username=request.user).first()
    condition = {}
    for k,v in kwargs.items():
        if v == 0:
            pass
        else:
            condition[k] = v
    data_count = models.Article.objects.filter(user=user).filter(**condition).count()
    page = Pagination(request.GET.get('p', 1), data_count)
    result = models.Article.objects.filter(user=user).filter(**condition).order_by('-nid').only('nid', 'title', 'user').select_related('user')[page.start:page.end]
    page_str = page.page_str(reverse('backend:article', kwargs=kwargs))
    category_list = models.Category.objects.filter(blog=user.blog).values('nid', 'title')
    tags_list = models.Tag.objects.filter(blog=user.blog).values('nid', 'title')
    kwargs['p'] = page.current_page
    return render(request,
                  'backend_article.html',
                  {'user': user,
                   'result': result,
                   'page_str': page_str,
                   'category_list': category_list,
                   'tags_list': tags_list,
                   'arg_dict': kwargs,
                   'data_count': data_count
                   }
                  )

@login_required
@check_have_blog
def edit_article(request, nid):
    """
    编辑文章
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    if request.method == 'GET':
        obj = models.Article.objects.filter(nid=nid, user=request.user).first()
        if not obj:
            return render(request, 'backend_no_article.html')
        tags = obj.tags.values_list('nid')
        if tags:
            tags = list(zip(*tags))[0]
        init_dict = {
            'nid': obj.nid,
            'title': obj.title,
            'category_id': obj.category_id,
            'content': obj.articledetail.content,
            'tags': tags
        }
        form = ArticleForm(request=request, data=init_dict)
        return render(request, 'backend_edit_article.html', {'form': form, 'nid': nid})
    elif request.method == 'POST':
        form = ArticleForm(request=request, data=request.POST)
        if form.is_valid():
            obj = models.Article.objects.filter(nid=nid, user=request.user).first()
            if not obj:
                return render(request, 'backend_no_article.html')
            with transaction.atomic():
                content = form.cleaned_data.pop('content')
                content = XSSFilter().process(content)
                soup = BeautifulSoup(content, 'html.parser')
                desc = soup.text[0:220] + "..."
                tags = form.cleaned_data.pop('tags')
                models.Article.objects.filter(nid=obj.nid).update(**form.cleaned_data, desc=desc)
                models.ArticleDetail.objects.filter(article=obj).update(content=content)
                models.Article2Tag.objects.filter(article=obj).delete()
                tag_list = []
                for tag_id in tags:
                    tag_id = int(tag_id)
                    tag_list.append(models.Article2Tag(article_id=obj.nid, tag_id=tag_id))
                models.Article2Tag.objects.bulk_create(tag_list)
            return redirect('/backend/article-0-0.html')
        else:
            return render(request, 'backend_edit_article.html', {'form': form})

@login_required
@check_have_blog
def del_article(request):
    """
    del article
    :param request:
    :return:
    """
    if request.method == 'GET':
        nid = request.GET.get('nid')
        article_obj = models.Article.objects.filter(nid=nid, user=request.user).first()
        if article_obj:
            models.Article2Tag.objects.filter(article=article_obj)
            article_obj.delete()
    return redirect('/backend/article-0-0.html')

@login_required
@check_have_blog
def add_article(request, *args, **kwargs):
    """
    添加文章
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    if request.method == "GET":
        form = ArticleForm(request=request)
        return render(request, 'backend_add_article.html', {'form': form})
    elif request.method == 'POST':
        form = ArticleForm(request=request, data=request.POST)
        user = request.user
        if form.is_valid():
            with transaction.atomic():
                tags = form.cleaned_data.pop('tags')
                content = form.cleaned_data.pop('content')
                content = XSSFilter().process2(content)
                soup = BeautifulSoup(content, 'html.parser')
                desc = soup.text[0:220] + "..."
                obj = models.Article.objects.create(**form.cleaned_data, user=user, desc=desc)
                models.ArticleDetail.objects.create(content=content, article=obj)
                tag_list = []
                for tag_id in tags:
                    tag_id = int (tag_id)
                    tag_list.append(models.Article2Tag(article_id=obj.nid, tag_id=tag_id))
                models.Article2Tag.objects.bulk_create(tag_list)
            return redirect('/backend/article-0-0.html')
        else:
            return render(request, 'backend_add_article.html', {'form': form})
    else:
        return redirect('/')

from mybbs import settings
import os, json
@login_required
@check_have_blog
def upload(request):
    obj = request.FILES.get("upload_img")
    file_name = str(uuid.uuid4())
    path = os.path.join(settings.MEDIA_ROOT, "add_article_img", file_name)
    with open(path, "wb") as f:
        for line in obj:
            f.write(line)

        res={
            "error": 0,
            "url": "/media/add_article_img/"+file_name
        }
    return HttpResponse(json.dumps(res))

from django.db.models import Count
@login_required
@check_have_blog
def category(request):
    if request.method == 'GET':
        blog = request.user.blog
        category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article")).values("title","c",'nid')
        page = Pagination(request.GET.get('p', 1), category_list.count())
        category_list = category_list[page.start:page.end]
        page_str = page.page_str(reverse('backend:category'))
        return render(request, 'backend_category.html', {'category_list': category_list,
                                                         'page_str': page_str})
    else:
        '''修改category'''
        title = request.POST.get('title', None)
        nid = request.POST.get('nid', 0)
        blog = request.user.blog
        ret = {"status": 0, "msg": ""}
        if title and nid:
            new_title_exist = models.Category.objects.filter(blog=blog, title=title)
            if new_title_exist:
                ret['status'] = 1
                ret['msg'] = '修改失败，"'+title+'"已存在！'
            else:
                models.Category.objects.filter(blog=blog, nid=nid).update(title=title)
        else:
            ret['status'] = 1
            ret['msg'] = '分类名不能为空'

        return JsonResponse(ret)

@login_required
@check_have_blog
def add_category(request):
    title = request.POST.get('cat_title')
    blog = request.user.blog
    try:
        models.Category.objects.create(blog=blog, title=title)
    except Exception as e:
        # return HttpResponse('添加失败，分类已存在！')
        pass
    return redirect(reverse('backend:category'))

@login_required
@check_have_blog
def del_category(request):
    """
    del article
    :param request:
    :return:
    """
    if request.method == 'GET':
        title = request.GET.get('title')
        ret = {"status": 0, "msg": ""}
        blog = request.user.blog
        article_cnt = models.Article.objects.filter(user=request.user, category__title=title).count()
        if article_cnt:
            ret['status'] = 1
            ret['msg'] = "该类别文章不为零，删除失败!"
        else:
            models.Category.objects.filter(title=title, blog=request.user.blog).delete()
        return JsonResponse(ret)


@login_required
@check_have_blog
def tag(request):
    if request.method == 'GET':
        blog = request.user.blog
        tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count("article")).values("title","c",'nid')
        page = Pagination(request.GET.get('p', 1), tag_list.count())
        tag_list = tag_list[page.start:page.end]
        page_str = page.page_str(reverse('backend:tag'))
        return render(request, 'backend_tag.html', {'tag_list': tag_list,
                                                    'page_str': page_str})
    else:
        '''修改tag'''
        title = request.POST.get('title', None)
        nid = request.POST.get('nid', 0)
        blog = request.user.blog
        ret = {"status": 0, "msg": ""}
        if title and nid:
            new_title_exist = models.Tag.objects.filter(blog=blog, title=title)
            if new_title_exist:
                ret['status'] = 1
                ret['msg'] = '修改失败，"'+title+'"已存在！'
            else:
                models.Tag.objects.filter(blog=blog, nid=nid).update(title=title)
        else:
            ret['status'] = 1
            ret['msg'] = '标签名不能为空'

        return JsonResponse(ret)

@login_required
@check_have_blog
def add_tag(request):
    title = request.POST.get('tag_title')
    blog = request.user.blog
    try:
        models.Tag.objects.create(blog=blog, title=title)
    except Exception as e:
        # return HttpResponse('添加失败，分类已存在！')
        pass
    return redirect(reverse('backend:tag'))

@login_required
@check_have_blog
def del_tag(request):
    """
    del article
    :param request:
    :return:
    """
    if request.method == 'GET':
        title = request.GET.get('title')
        ret = {"status": 0, "msg": ""}
        blog = request.user.blog
        tag = models.Tag.objects.filter(title=title, blog=blog).first()
        article_cnt = models.Article2Tag.objects.filter(tag=tag).count()
        if article_cnt:
            ret['status'] = 1
            ret['msg'] = "该标签文章不为零，删除失败!"
        else:
            tag.delete()
        return JsonResponse(ret)

@login_required
@check_have_blog
def base_info(request):
    """
    博主个人信息
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'backend_base_info.html', {'user': request.user})
    else:
        ret = {"status": 0, "msg": ""}
        blogUrl = request.POST.get('blogUrl')
        avatarUrl = request.POST.get('avatarUrl')
        avatarUrl = avatarUrl[7:]
        if not blogUrl or not avatarUrl:
            ret["status"] = 1
            ret["msg"] = "至少一个参数为空"
            return JsonResponse(ret)
        models.UserInfo.objects.filter(username=request.user).update(avatar=avatarUrl)
        if not blogUrl == request.user.blog.site:
            tmp = models.Blog.objects.filter(site=blogUrl).first()
            print(tmp)
            if tmp:
                ret["status"] = 1
                ret["msg"] = '站点 "'+blogUrl+'" 已存在！'
            else:
                blog = models.Blog.objects.filter(userinfo=request.user).update(site=blogUrl)
        return JsonResponse(ret)

@login_required
@check_have_blog
def upload_avatar(request):
    ret = {'status': False, 'data': None, 'message': None}
    if request.method == 'POST':
        file_obj = request.FILES.get('avatar_img')
        if not file_obj:
            pass
        else:
            file_name = str(uuid.uuid4())
            file_path = os.path.join('media/avatars', file_name)
            f = open(file_path, 'wb')
            for chunk in file_obj.chunks():
                f.write(chunk)
            f.close()
            ret['status'] = True
            ret['data'] = file_path

    return HttpResponse(json.dumps(ret))