# Generated by Django 5.0.7 on 2024-08-30 00:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_page', '0006_bookmark'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='status',
            field=models.CharField(choices=[('draft', '초안'), ('published', '발행됨'), ('pending', '보류 중')], default='draft', max_length=10),
        ),
    ]
