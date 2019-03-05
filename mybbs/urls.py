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
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls import url
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.views import serve
# from django.conf import settings
from mybbs import settings
from django.conf.urls.static import static
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls', namespace='users')),
    # path('favicon.ico', RedirectView.as_view(url='static/img/favicon.ico')),
    path('backend/', include('backend.urls', namespace='backend')),
    path('favicon.ico', serve, {'path': 'img/favicon.ico'}),
    # path('media/<path:par>',  serve, {'document_root': MEDIA_ROOT}),
    # re_path(r'^media/(?P<path>.*)$', serve, {'path': MEDIA_ROOT}),
    path('', include('blog.urls', namespace='blog')),
]
if os.getcwd() != '/app':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG is False:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
