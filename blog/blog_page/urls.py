from django.urls import path
from .views import (
    PostList,
    PostDetail,
    PostCreate,
    PostUpdate,
    PostDelete,
    delete_comment,
    new_comment,
    CommentUpdate,
    category_page,
    tag_page,
)

app_name = "blog_page"

urlpatterns = [
    # Home page showing the list of posts
    path("", PostList.as_view(), name="post_list"),
    # Detailed view of a single post
    path("<int:pk>/", PostDetail.as_view(), name="post_detail"),
    # Page for creating a new post
    path("write/", PostCreate.as_view(), name="post_create"),
    # Page for updating an existing post
    path("<int:pk>/edit/", PostUpdate.as_view(), name="post_edit"),
    # Page for creating a new comment on a post
    path("<int:pk>/delete/", PostDelete.as_view(), name="post_delete"),
    path("<int:pk>/comment/", new_comment, name="new_comment"),
    # Page for updating an existing comment
    path("comment/<int:pk>/edit/", CommentUpdate.as_view(), name="comment_update"),
    # Page for deleting a comment
    path("comment/<int:pk>/delete/", delete_comment, name="delete_comment"),
    # Page to filter posts by category
    path("category/<slug:slug>/", category_page, name="category_page"),
    # Page to filter posts by tag
    path("tag/<slug:slug>/", tag_page, name="tag_page"),
]
