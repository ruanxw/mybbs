from django.shortcuts import redirect


def check_have_blog(func):
    def inner(request, *args, **kwargs):
        user = request.user
        if user.blog:
            return func(request, *args, **kwargs)
        else:
            return redirect('/backend/index.html')
    return inner