from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import auth

import json
import os
import uuid

# Create your views here.
from . import forms
from blog import models


def get_valid_img(request):
    #自己生成一个图片
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import random

    #获取随机颜色的函数
    def get_random_color():
        return random.randint(0,50), random.randint(0,50), random.randint(0,50)

    #生成一个图片对象
    img_obj = Image.new(
        'RGB',
        (120, 30),
        # get_random_color()
        (255,255,255)
    )
    #在生成的图片上写字符
    #生成一个图片画笔对象
    draw_obj = ImageDraw.Draw(img_obj)
    #加载字体文件，得到一个字体对象
    font_obj = ImageFont.truetype("static/font/kumo.ttf", 28)
    #开始生成随机字符串，并写到图片上
    tmp_list = []
    letter_cases = "abcdefghjkmnpqrstuvwxy"  # 小写字母，去除可能干扰的i，l，o，z
    upper_cases = letter_cases.upper()  # 大写字母
    numbers = ''.join(map(str, range(3, 10)))  # 数字
    init_chars = ''.join((letter_cases, upper_cases, numbers))
    tmp_list = random.sample(init_chars, 4)
    i = 0
    for item in tmp_list:
        draw_obj.text((10+25*i, 0), item, fill=get_random_color(), font=font_obj)
        i = i+1
    request.session["valid_code"] = ('').join(tmp_list)

    #绘制干扰线
    line_num = random.randint(1,2) #干扰线条数
    for i in range(line_num):
        #起始点
        begin = (random.randint(0, 20),random.randint(0, 30))
        #结束点
        end = (random.randint(100, 120),random.randint(0, 30))
        draw_obj.line([begin, end], fill=(0,0,0))

    """绘制干扰点"""
    chance = min(100, max(0, int(5)))  # 大小限制在[0, 100]

    for w in range(120):
        for h in range(30):
            tmp = random.randint(0, 100)
            if tmp > 100 - chance:
                draw_obj.point((w, h), fill=(0, 0, 0))

    # 图形扭曲参数
    params = [1 - float(random.randint(1, 2)) / 100,
              0,
              0,
              0,
              1 - float(random.randint(1, 10)) / 100,
              float(random.randint(1, 2)) / 500,
              0.001,
              float(random.randint(1, 2)) / 500
              ]
    img_obj.transform((120,30), Image.PERSPECTIVE, params) #创建扭曲
    img_obj.filter(ImageFilter.EDGE_ENHANCE_MORE)
    #从内存中直接加载文件
    from io import BytesIO
    io_obj = BytesIO()
    #将生成的图片数据加载到io对象中
    img_obj.save(io_obj, "png")
    #从io对象中取到上一步保存的数据
    data = io_obj.getvalue()
    return HttpResponse(data)


def login(request):
    if request.method == "POST":
        #初始化给ajax返回的参数
        ret = {"status": 0, "msg": ""}
        #获取用户输入的用户密码验证码
        username = request.POST.get("username")
        password = request.POST.get("password")
        valid_code = request.POST.get("valid_code")
        if valid_code and valid_code.upper() == request.session.get("valid_code", "").upper():
            #验证码正确
            #利用auth模块做用户名密码校验
            user = auth.authenticate(request=request, username=username, password=password)
            if user:
                #用户名密码正确
                #给用户做登录
                auth.login(request, user)
                ret["msg"] = reverse('blog:index')
                if json.loads(request.POST.get("valibleTime")):
                    request.session.set_expiry(60*60*24*30)
                else:
                    request.session.set_expiry(60*60*24*7)
            else:
                #用户名密码错误
                ret["status"] = 1
                ret["msg"] = "用户名密码错误"
        else:
            #验证码错误
            ret["status"] = 1
            ret["msg"] = "验证码错误"
        return JsonResponse(ret)
    return render(request, "login.html")


def logout(request):
    auth.logout(request)
    return redirect(reverse("blog:index"))


def register(request):
    if request.method == 'POST':
        ret = {"status": 0, "msg": ""}
        form_obj = forms.RegForm(request.POST)
        # 帮我做校验
        if form_obj.is_valid():
            # 校验通过，去数据库创建一个新用户
            form_obj.cleaned_data.pop("re_password")
            avatar_img = request.FILES.get("avatar")
            if(avatar_img):
                models.UserInfo.objects.create_user(**form_obj.cleaned_data, avatar=avatar_img)
                # 头像文件保存到media/avatars文件夹
                file_name = str(uuid.uuid4())
                file_path = os.path.join('media/avatars', file_name)
                f = open(file_path, 'wb')
                for chunk in avatar_img.chunks():
                    f.write(chunk)
                f.close()
            else:
                models.UserInfo.objects.create_user(**form_obj.cleaned_data)
            username = form_obj.cleaned_data.get("username")
            password = form_obj.cleaned_data.get("password")
            # authenticated_user = auth.authenticate(username=username, password=password)
            ret["msg"] = reverse("blog:index")

            return JsonResponse(ret)
        else:
            print(form_obj.errors)
            ret["status"] = 1
            ret["msg"] = form_obj.errors
            print(ret)
            print("=" * 120)
            return JsonResponse(ret)

    # 生成一个form对象
    form_obj = forms.RegForm()
    # print(form_obj)
    return render(request, "register.html", {"form_obj": form_obj})


def check_username_exist(request):
    ret = {"status": 0, "msg": ""}
    username = request.GET.get("username")
    isExist = models.UserInfo.objects.filter(username = username)
    if isExist:
        ret["status"] = 1
        ret["msg"] = "用户名已被注册"
    return JsonResponse(ret)