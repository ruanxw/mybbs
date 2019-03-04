from django.core.exceptions import ValidationError
from django import forms as django_forms
from django.forms import fields as django_fields
from django.forms import widgets as django_widgets

from blog import models

class ArticleForm(django_forms.Form):
    title = django_fields.CharField(
        widget=django_widgets.TextInput(attrs={'class': 'form-control',
                                               'placeholder': '文章标题',
                                              'required': 'required'})
    )
    content = django_fields.CharField(
        widget=django_widgets.Textarea(attrs={'class': 'kind-content',
                                              'id': 'kind-content',
                                              'style': 'overflow:auto;',
                                              'required': 'required'})
    )
    category_id = django_fields.ChoiceField(
        choices=[],
        widget=django_widgets.RadioSelect,
        required=1
    )
    tags = django_fields.MultipleChoiceField(
        choices=[],
        widget=django_widgets.CheckboxSelectMultiple,
        required=1
    )
    def __init__(self, request, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        user = models.UserInfo.objects.filter(username=request.user).first()
        self.fields['category_id'].choices = models.Category.objects.filter(blog=user.blog).values_list('nid', 'title')
        self.fields['tags'].choices = models.Tag.objects.filter(blog=user.blog).values_list('nid', 'title')
