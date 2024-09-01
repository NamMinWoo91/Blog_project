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
    category_page,
    tag_list,
    tag_page,
    toggle_bookmark,
)
from . import views

app_name = "blog_page"

urlpatterns = [
    # Home page showing the list of posts
    path("", PostList.as_view(), name="post_list"),
    # Detailed view of a single post
    path("<int:pk>/", PostDetail.as_view(), name="post_detail"),
    # Page for creating a new post
    path("write/", PostCreate.as_view(), name="post_create"),
    # Page for updating an existing post
    path("edit/<int:pk>/", PostUpdate.as_view(), name="post_edit"),
    # Page for deleting a post
    path("delete/<int:pk>/", PostDelete.as_view(), name="post_delete"),
    # Search posts
    path("search/", PostSearchView.as_view(), name="search"),
    # Page for creating a new comment on a post
    path("<int:pk>/comment/", CommentCreate.as_view(), name="comment_create"),
    path("comment/<int:pk>/update/", CommentUpdate.as_view(), name="comment_update"),
    path("comment/<int:pk>/delete/", CommentDelete.as_view(), name="comment_delete"),
    # Page for replying to a comment (대댓글)
    # 대댓글 현재 미정
    # Page to filter posts by category
    path("category/<slug:slug>/", category_page, name="category_page"),
    # Page to filter posts by tag
    path("tags/", views.tag_list, name="tag_list"),
    path("tag/<str:slug>/", views.tag_page, name="tag_page"),
    path("like/<int:post_id>/", views.like_post, name="like_post"),
    path("bookmark/<int:post_id>/", toggle_bookmark, name="toggle_bookmark"),
    path("bookmark/<int:post_id>/", views.bookmark_post, name="bookmark_post"),
]
