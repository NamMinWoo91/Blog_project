from django.urls import path
from .views import (
    PostList,
    PostDetail,
    PostCreate,
    PostUpdate,
    PostDelete,
    PostSearchView,
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
    path("edit/<int:pk>/", PostUpdate.as_view(), name="post_edit"),
    # Page for deleting a post
    path("delete/<int:pk>/", PostDelete.as_view(), name="post_delete"),
    # Search posts
    path("search/<int:pk>/", PostSearchView.as_view(), name="search"),
    # Page for creating a new comment on a post
    path("<int:pk>/comment/", new_comment, name="new_comment"),
    # Page for updating an existing comment
    path("edit/comment/<int:pk>/", CommentUpdate.as_view(), name="comment_update"),
    # Page for deleting a comment
    path("delete/comment/<int:pk>/", delete_comment, name="delete_comment"),
    # Page for replying to a comment (대댓글)
    path(
        "<int:pk>/comment/<int:parent_comment_id>/", new_comment, name="reply_comment"
    ),
    # Page to filter posts by category
    path("category/<slug:slug>/", category_page, name="category_page"),
    # Page to filter posts by tag
    path("tag/<str:slug>/", tag_page, name="tag_page"),
]
