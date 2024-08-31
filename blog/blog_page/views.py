import logging, json
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from .models import Post, Category, Tag, Comment, Like, Bookmark
from .forms import CommentForm, PostForm
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views import View


class PostList(ListView):
    model = Post
    ordering = "-pk"
    template_name = "blog_page/post_list.html"
    context_object_name = "posts"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category_list"] = Category.objects.all().order_by("-name")
        context["no_category_post_count"] = Post.objects.filter(category=None).count()
        context["search_keyword"] = self.request.GET.get("q", "")
        return context

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


class PostDetail(DetailView):
    model = Post
    template_name = "blog_page/post_detail.html"

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        post.views_count += 1
        post.save(update_fields=["views_count"])
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all().order_by("-name")
        context["no_category_post_count"] = Post.objects.filter(category=None).count()
        context["comment_form"] = CommentForm
        context["current_user"] = self.request.user

        comments = self.object.comment_set.filter(parent=None).order_by("created_at")
        comment_tree = self.build_comment_tree(comments)
        context["comment_tree"] = comment_tree

        context["related_posts"] = self.object.related_posts.all()
        return context

    def build_comment_tree(self, comments):
        comment_tree = []
        for comment in comments:
            comment_dict = {
                "comment": comment,
                "replies": self.build_comment_tree(
                    comment.replies.all().order_by("created_at")
                ),
            }
            comment_tree.append(comment_dict)
        return comment_tree


def category_page(request, slug):
    category = get_object_or_404(Category, slug=slug)
    context = {
        "post_list": Post.objects.filter(category=category).order_by("-pk"),
        "categories": Category.objects.all().order_by("-name"),
        "no_category_post_count": Post.objects.filter(category=None).count(),
        "category": category,
        "category_list": Category.objects.all().order_by("-name"),
    }
    return render(request, "blog_page/post_list.html", context)


def tag_page(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    context = {
        "post_list": tag.post_set.all(),
        "categories": Category.objects.all().order_by("-name"),
        "no_category_post_count": Post.objects.filter(category=None).count(),
        "tag": tag,
        "category_list": Category.objects.all().order_by("-name"),
    }
    return render(request, "blog_page/post_list.html", context)


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog_page/write_page.html"

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
            return super().form_valid(form)
        else:
            return redirect("/blog/")

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context["errors"] = form.errors
        return self.render_to_response(context)


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog_page/post_edit.html"

    def get_object(self, queryset=None):
        # 기존의 get_object 메서드를 사용하여 객체를 가져옵니다.
        obj = super().get_object(queryset)
        # 현재 로그인한 사용자가 객체의 작성자인지 확인합니다.
        if obj.author != self.request.user:
            # 작성자가 아닌 경우 PermissionDenied 예외를 발생시킵니다.
            raise PermissionDenied
        return obj

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.tags.clear()
        for tag_name in form.cleaned_data["tags"]:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            self.object.tags.add(tag)
        return response

    def get_initial(self):
        initial = super().get_initial()
        initial["tags"] = ", ".join(tag.name for tag in self.object.tags.all())
        return initial


class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    # template_name = "blog_page/post_delete.html"
    success_url = reverse_lazy("blog_page:post_list")

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            messages.error(request, "You do not have permission to delete this post.")
            return HttpResponseRedirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            messages.error(request, "You do not have permission to delete this post.")
            return HttpResponseRedirect(self.success_url)

        self.object = post
        self.object.delete()
        messages.success(request, "Post has been successfully deleted.")
        return redirect(self.success_url)


class PostSearchView(ListView):
    model = Post
    template_name = "blog_page/post_search.html"
    context_object_name = "post_list"

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return Post.objects.filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(tags__name__icontains=query)
            ).distinct()
        return Post.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_keyword"] = self.request.GET.get("q", "")
        return context


logger = logging.getLogger(__name__)


@method_decorator(require_POST, name="dispatch")
class CommentCreate(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            post = get_object_or_404(Post, pk=pk)
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()

                context = {"comment": comment}
                html = render_to_string(
                    "blog_page/comment.html", context, request=request
                )
                return JsonResponse({"success": True, "html": html})
            else:
                # 폼 오류를 JSON으로 변환
                errors = json.loads(form.errors.as_json())
                return JsonResponse({"success": False, "errors": errors}, status=400)
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "errors": "잘못된 요청 형식입니다."}, status=400
            )
        except Exception as e:
            return JsonResponse({"success": False, "errors": str(e)}, status=500)


@method_decorator(require_POST, name="dispatch")
class CommentUpdate(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk, author=request.user)
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save()
            return JsonResponse(
                {
                    "success": True,
                    "content": comment.content,
                }
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)


@method_decorator(require_POST, name="dispatch")
class CommentDelete(LoginRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk, author=request.user)
        comment.delete()
        return JsonResponse({"success": True})


@require_POST
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def toggle_bookmark(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)

    if not created:
        bookmark.delete()
        is_bookmarked = False
    else:
        is_bookmarked = True

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def bookmarked_posts(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related("post")
    context = {"bookmarked_posts": [bookmark.post for bookmark in bookmarks]}
    return render(request, "blog_page/bookmarked_posts.html", context)
