from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    CategoryPostListView,
    CategoryListView,
    TagPostListView,
    add_comment,
)

urlpatterns = [
    path("", PostListView.as_view(), name="post_list"),  # 블로그 포스트 목록 페이지
    path(
        "post/<int:pk>/", PostDetailView.as_view(), name="post_detail"
    ),  # 블로그 포스트 상세 페이지
    path(
        "category/<slug:slug>/",
        CategoryPostListView.as_view(),
        name="category_post_list",
    ),  # 카테고리별 포스트 목록
    path(
        "tag/<slug:slug>/", TagPostListView.as_view(), name="tag_post_list"
    ),  # 태그별 포스트 목록
    path("post/<int:post_id>/comment/", add_comment, name="add_comment"),  # 댓글 추가
    path(
        "categories/", CategoryListView.as_view(), name="category_list"
    ),  # 카테고리 목록 페이지 추가
]
