from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Post, Category, Tag, Comment
from .forms import CommentForm
from django.contrib.auth.decorators import login_required


# 블로그 포스트 목록 뷰
class PostListView(ListView):
    model = Post
    template_name = "blog_page/post_list.html"
    context_object_name = "posts"
    paginate_by = 10  # 페이지당 10개의 포스트를 표시

    def get_queryset(self):
        return Post.objects.all().order_by("-created_at")


# 블로그 포스트 상세 뷰
class PostDetailView(DetailView):
    model = Post
    template_name = "blog_page/post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = CommentForm()
        return context


# 카테고리별 포스트 목록 뷰
class CategoryPostListView(ListView):
    model = Post
    template_name = "blog_page/category_post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return Post.objects.filter(category=self.category).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class CategoryListView(ListView):
    model = Category
    template_name = "blog_page/category_list.html"
    context_object_name = "categories"


# 태그별 포스트 목록 뷰
class TagPostListView(ListView):
    model = Post
    template_name = "blog_page/tag_post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])
        return Post.objects.filter(tags=self.tag).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        return context


# 댓글 작성 처리 뷰
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect(post.get_absolute_url())
    else:
        form = CommentForm()
    return render(
        request, "blog_page/post_detail.html", {"post": post, "comment_form": form}
    )
