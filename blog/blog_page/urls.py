from django.urls import path
from .views import (
    PostList,
    PostDetail,
    PostCreate,
    PostUpdate,
    PostDelete,
    PostSearchView,
    CommentCreate,
    CommentUpdate,
    CommentDelete,
    toggle_bookmark,
    category_page,
)
from . import views

app_name = "blog_page"

urlpatterns = [
    # 게시물 목록 페이지 (홈페이지)
    path("", PostList.as_view(), name="post_list"),
    # 게시물 상세 보기
    path("<int:pk>/", PostDetail.as_view(), name="post_detail"),
    # 새 게시물 작성 페이지
    path("write/", PostCreate.as_view(), name="post_create"),
    # 기존 게시물 수정 페이지
    path("edit/<int:pk>/", PostUpdate.as_view(), name="post_edit"),
    # 게시물 삭제
    path("delete/<int:pk>/", PostDelete.as_view(), name="post_delete"),
    # 게시물 검색
    path("search/", PostSearchView.as_view(), name="search"),
    # 댓글 생성
    path("<int:pk>/comment/", CommentCreate.as_view(), name="comment_create"),
    # 댓글 수정
    path("comment/<int:pk>/update/", CommentUpdate.as_view(), name="comment_update"),
    # 댓글 삭제
    path("comment/<int:pk>/delete/", CommentDelete.as_view(), name="comment_delete"),
    # 카테고리별 게시물 목록
    path("category/<slug:slug>/", category_page, name="category_page"),
    # 태그 목록
    path("tags/", views.tag_list, name="tag_list"),
    # 태그별 게시물 목록
    path("tag/<str:slug>/", views.tag_page, name="tag_page"),
    # 게시물 좋아요
    path("like/<int:post_id>/", views.like_post, name="like_post"),
    # 북마크 토글
    path("bookmark/<int:post_id>/", toggle_bookmark, name="toggle_bookmark"),
    # 게시물 북마크
    path("bookmark/<int:post_id>/", views.bookmark_post, name="bookmark_post"),
]

"""
블로그 페이지 관련 URL 설정

이 모듈은 블로그 애플리케이션의 URL 패턴을 정의합니다.
각 URL 패턴은 특정 뷰 함수나 클래스와 연결되어 있으며, 
사용자의 요청을 적절한 뷰로 라우팅합니다.

주요 기능:
- 게시물 목록, 상세 보기, 생성, 수정, 삭제
- 댓글 생성, 수정, 삭제
- 카테고리 및 태그별 게시물 필터링
- 게시물 검색
- 좋아요 및 북마크 기능

각 URL 패턴에는 고유한 이름이 지정되어 있어, 
템플릿이나 뷰에서 URL 역참조를 할 때 사용할 수 있습니다.
"""
