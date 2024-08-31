from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    PostSearchView,
    CommentCreateView,
    CommentUpdateView,
    CommentDeleteView,
    CategoryPageView,
    TagPageView,
    LikePostView,
    BookmarkPostView,
    BookmarkedPostsView,
)

app_name = "blog_page"

urlpatterns = [
    # Home page showing the list of posts
    path("", PostListView.as_view(), name="post_list"),
    # Detailed view of a single post
    path("<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    # Page for creating a new post
    path("write/", PostCreateView.as_view(), name="post_create"),
    # Page for updating an existing post
    path("edit/<int:pk>/", PostUpdateView.as_view(), name="post_edit"),
    # Page for deleting a post
    path("delete/<int:pk>/", PostDeleteView.as_view(), name="post_delete"),
    # Search posts
    path("search/", PostSearchView.as_view(), name="search"),
    # Page for creating a new comment on a post
    path("<int:pk>/comment/", CommentCreateView.as_view(), name="new_comment"),
    path(
        "<int:pk>/comment/<int:parent_comment_id>/",
        CommentCreateView.as_view(),
        name="reply_comment",
    ),
    path(
        "comment/<int:pk>/update/", CommentUpdateView.as_view(), name="comment_update"
    ),
    path(
        "comment/<int:pk>/delete/", CommentDeleteView.as_view(), name="delete_comment"
    ),
    # Page to filter posts by category
    path("category/<slug:slug>/", CategoryPageView.as_view(), name="category_page"),
    # Page to filter posts by tag
    path("tag/<str:slug>/", TagPageView.as_view(), name="tag_page"),
    path("like/<int:post_id>/", LikePostView.as_view(), name="like_post"),
    path("bookmark/<int:post_id>/", BookmarkPostView.as_view(), name="toggle_bookmark"),
    path("bookmarks/", BookmarkedPostsView.as_view(), name="bookmarked_posts"),
]
