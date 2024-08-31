from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views import View
from django.db.models import Q
from .models import Post, Category, Tag, Comment, Like, Bookmark
from .forms import CommentForm, PostForm
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.contrib import messages
from django.views.generic.edit import FormMixin


class PostListView(ListView):
    model = Post
    template_name = "blog_page/post_list.html"
    context_object_name = "posts"
    ordering = "-pk"

    def get_queryset(self):
        queryset = super().get_queryset().filter(status="published")
        search_keyword = self.request.GET.get("q")
        if search_keyword:
            queryset = queryset.filter(
                Q(title__icontains=search_keyword)
                | Q(content__icontains=search_keyword)
                | Q(tags__name__icontains=search_keyword)
            ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category_list"] = Category.objects.all().order_by("-name")
        context["no_category_post_count"] = Post.objects.filter(category=None).count()
        context["search_keyword"] = self.request.GET.get("q", "")
        return context


class PostDetailView(DetailView, FormMixin):
    model = Post
    template_name = "blog_page/post_detail.html"
    form_class = CommentForm

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=["views_count"])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all().order_by("-name")
        context["no_category_post_count"] = Post.objects.filter(category=None).count()
        context["comment_form"] = CommentForm()  # 코멘트 폼 추가
        context["current_user"] = self.request.user
        comments = self.object.comment_set.filter(parent=None).order_by("created_at")
        context["comment_tree"] = [
            {
                "comment": comment,
                "replies": comment.replies.all().order_by("created_at"),
            }
            for comment in comments
        ]
        context["related_posts"] = self.object.related_posts.all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.post = self.object
        form.instance.author = self.request.user
        parent_id = self.request.POST.get("parent_id")
        if parent_id:
            form.instance.parent = get_object_or_404(Comment, id=parent_id)
        form.save()
        messages.success(self.request, "댓글이 성공적으로 작성되었습니다.")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse("blog_page:post_detail", kwargs={"pk": self.object.pk})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog_page/write_page.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog_page/post_edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.tags.clear()
        for tag_name in form.cleaned_data["tags"]:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            self.object.tags.add(tag)
        return response


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "blog_page/post_delete.html"
    success_url = reverse_lazy("blog_page:post_list")

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        form.instance.post = post
        form.instance.author = self.request.user
        parent_id = self.request.POST.get("parent_id")
        if parent_id:
            form.instance.parent = get_object_or_404(Comment, id=parent_id)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog_page:post_detail", kwargs={"pk": self.object.post.pk})


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog_page/comment_update.html"

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def handle_no_permission(self):
        messages.error(self.request, "자신의 댓글만 수정할 수 있습니다.")
        return redirect("blog_page:post_detail", pk=self.get_object().post.pk)

    def get_success_url(self):
        messages.success(self.request, "댓글이 성공적으로 수정되었습니다.")
        return reverse("blog_page:post_detail", kwargs={"pk": self.object.post.pk})


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = "blog_page/comment_confirm_delete.html"

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def handle_no_permission(self):
        messages.error(self.request, "자신의 댓글만 삭제할 수 있습니다.")
        return redirect("blog_page:post_detail", pk=self.get_object().post.pk)

    def get_success_url(self):
        messages.success(self.request, "댓글이 성공적으로 삭제되었습니다.")
        return reverse("blog_page:post_detail", kwargs={"pk": self.object.post.pk})


class LikePostView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        return JsonResponse({"liked": liked, "total_likes": post.total_likes()})


class BookmarkPostView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
        if not created:
            bookmark.delete()
            is_bookmarked = False
        else:
            is_bookmarked = True
        return JsonResponse(
            {
                "is_bookmarked": is_bookmarked,
                "bookmark_count": post.bookmark_set.count(),
            }
        )


class BookmarkedPostsView(LoginRequiredMixin, ListView):
    model = Bookmark
    template_name = "blog_page/bookmarked_posts.html"
    context_object_name = "bookmarked_posts"

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related("post")


class CategoryPageView(ListView):
    model = Post
    template_name = "blog_page/post_list.html"
    context_object_name = "post_list"

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return Post.objects.filter(category=self.category).order_by("-pk")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all().order_by("-name")
        context["no_category_post_count"] = Post.objects.filter(category=None).count()
        context["category"] = self.category
        context["category_list"] = Category.objects.all().order_by("-name")
        return context


class TagPageView(ListView):
    model = Post
    template_name = "blog_page/post_list.html"
    context_object_name = "post_list"

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])
        return self.tag.post_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all().order_by("-name")
        context["no_category_post_count"] = Post.objects.filter(category=None).count()
        context["tag"] = self.tag
        context["category_list"] = Category.objects.all().order_by("-name")
        return context


class PostSearchView(ListView):
    model = Post
    template_name = "blog_page/post_list.html"
    context_object_name = "post_list"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        tag_slug = self.kwargs.get("tag", "")
        search_keyword = self.request.GET.get("q", "")
        search_by = self.request.GET.get("search_by", "title")

        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        if search_keyword:
            if search_by == "title":
                queryset = queryset.filter(title__icontains=search_keyword)
            elif search_by == "category":
                queryset = queryset.filter(category__name__icontains=search_keyword)
            else:
                queryset = queryset.filter(
                    Q(title__icontains=search_keyword)
                    | Q(content__icontains=search_keyword)
                    | Q(tags__name__icontains=search_keyword)
                ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category_list"] = Category.objects.all().order_by("-name")
        context["no_category_post_count"] = Post.objects.filter(category=None).count()
        context["search_keyword"] = self.request.GET.get("q", "")
        context["search_by"] = self.request.GET.get("search_by", "title")
        context["tag"] = self.kwargs.get("tag", "")
        return context
