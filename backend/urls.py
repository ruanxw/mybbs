"""mybbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, re_path
from . import views

app_name = 'backend'
urlpatterns = [
    path('index.html', views.index, name='index'),
    path('article-<int:tags__nid>-<int:category_id>.html', views.article, name='article'),
    path('edit-article-<int:nid>.html', views.edit_article, name='edit_article'),
    path('add-article.html', views.add_article, name='add_article'),
    path('del-article.html', views.del_article, name='del_article'),
    path('category.html', views.category, name='category'),
    path('del-category.html', views.del_category, name='del_category'),
    path('add-category.html', views.add_category, name='add_category'),
    path('tag.html', views.tag, name='tag'),
    path('del-tag.html', views.del_tag, name='del_tag'),
    path('add-tag.html', views.add_tag, name='add_tag'),
    path('base-info.html', views.base_info, name='base_info'),
    path('upload', views.upload),
    path('upload-avatar.html', views.upload_avatar),
]
