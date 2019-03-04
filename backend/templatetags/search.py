from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def category_all(arg_dict):
    tags__nid = arg_dict['tags__nid']
    category_nid = arg_dict['category_id']
    p = arg_dict['p']
    url = reverse('backend:article', kwargs={'tags__nid': tags__nid, 'category_id': 0})
    if category_nid == 0:
        temp =  '<a class="active" href="%s?p=%s">全部</a>' % (url, p,)
    else:
        temp = '<a href="%s?p=%s">全部</a>' % (url, p,)
    return mark_safe(temp)

@register.simple_tag
def category_combine(obj_list, arg_dict):
    li = []
    tags__nid = arg_dict['tags__nid']
    category_nid = arg_dict['category_id']
    p = arg_dict['p']
    for obj in obj_list:
        url = reverse('backend:article', kwargs={'tags__nid': tags__nid, 'category_id': obj['nid']})
        if obj['nid'] == int(category_nid):
            temp = '<a class="active" href="%s?p=%s">%s</a>' % (url,p, obj['title'])
        else:
            temp = '<a href="%s?p=%s">%s</a>' % (url,p, obj['title'])
        li.append(temp)
    return mark_safe(''.join(li))


@register.simple_tag
def article_type_all(arg_dict):
    tags__nid = arg_dict['tags__nid']
    category_nid = arg_dict['category_id']
    p = arg_dict['p']
    url = reverse('backend:article', kwargs={'tags__nid': 0, 'category_id': category_nid})
    if tags__nid == 0:
        temp = '<a class="active" href="%s?p=%s">全部</a>' % (url,p,)
    else:
        temp = '<a href="%s?p=%s">全部</a>' % (url,p,)
    return mark_safe(temp)

@register.simple_tag
def article_type_combine(obj_list, arg_dict):
    li = []
    tags__nid = arg_dict['tags__nid']
    category_nid = arg_dict['category_id']
    p = arg_dict['p']
    for obj in obj_list:
        url = reverse('backend:article', kwargs={'tags__nid': obj['nid'], 'category_id': category_nid})
        if obj['nid'] == int(tags__nid):
            temp = '<a class="active" href="%s?p=%s">%s</a>' % (url,p, obj['title'])
        else:
            temp = '<a href="%s?p=%s">%s</a>' % (url,p, obj['title'])
        li.append(temp)
    return mark_safe(''.join(li))