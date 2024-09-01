from django.contrib import admin
from .models import Post, Category, Tag, Comment


class PostAdmin(admin.ModelAdmin):
    """
    관리자 페이지에서 Post 모델을 관리하기 위한 설정 클래스입니다.

    Attributes:
        list_display (list): 관리자 목록 페이지에 표시할 필드들.
        list_filter (list): 목록을 필터링할 수 있는 필드들.
        search_fields (list): 검색 기능을 적용할 필드들.
        filter_horizontal (tuple): 다대다 관계를 위한 수평 필터 위젯을 사용할 필드들.
    """

    list_display = ["title", "author", "created_at", "status"]
    list_filter = ["status", "category"]
    search_fields = ["title", "content"]
    filter_horizontal = ("related_posts",)


# 관리자 페이지에 모델들을 등록합니다.
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Comment)
