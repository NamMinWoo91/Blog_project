from django.contrib import admin
from .models import Post, Category, Tag, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "created_at", "status"]
    list_filter = ["status", "category"]
    search_fields = ["title", "content"]
    filter_horizontal = ("related_posts",)


admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Comment)
