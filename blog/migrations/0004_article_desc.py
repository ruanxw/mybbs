# Generated by Django 2.0.10 on 2019-02-23 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20190112_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='desc',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
