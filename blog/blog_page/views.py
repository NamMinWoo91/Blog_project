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
        queryset = super().get_queryset()
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
        comment_tree = [
            {
                "comment": comment,
                "replies": comment.replies.all().order_by("created_at"),
            }
            for comment in comments
        ]
        context["comment_tree"] = comment_tree
        context["related_posts"] = self.object.related_posts.all()
        return context


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
    success_url = reverse_lazy("blog_page:post_list")

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
            post = form.save(commit=False)
            post.save()
            for tag_name in form.cleaned_data["tags"]:
                slug = slugify(tag_name, allow_unicode=True)
                tag, _ = Tag.objects.get_or_create(
                    name=tag_name, defaults={"slug": slug}
                )
                post.tags.add(tag)
            return super().form_valid(form)
        return redirect("/blog/")


class PostUpdate(LoginRequiredMixin, UpdateView):
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

    def get_initial(self):
        initial = super().get_initial()
        initial["tags"] = ", ".join(tag.name for tag in self.object.tags.all())
        return initial


@login_required
def new_comment(request, pk, parent_comment_id=None):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            if parent_comment_id:
                comment.parent = get_object_or_404(Comment, pk=parent_comment_id)
            comment.save()
            return redirect(post.get_absolute_url())
    else:
        form = CommentForm()
    return render(request, "blog_page/comment_form.html", {"form": form})


class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "blog_page/post_delete.html"
    success_url = reverse_lazy("blog_page:post_list")

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            messages.error(request, "You do not have permission to delete this post.")
            return HttpResponseRedirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)


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


class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog_page/comment_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return HttpResponseForbidden("You are not allowed to update this comment")
        return super().dispatch(request, *args, **kwargs)


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author == request.user:
        post_url = comment.post.get_absolute_url()
        comment.delete()
        return redirect(post_url)
    return HttpResponseForbidden("You are not allowed to delete this comment")


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
    return JsonResponse({"liked": liked, "total_likes": post.total_likes()})


@login_required
def toggle_bookmark(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)

    if not created:
        bookmark.delete()
        is_bookmarked = False
    else:
        is_bookmarked = True

    return JsonResponse(
        {"is_bookmarked": is_bookmarked, "bookmark_count": post.bookmark_set.count()}
    )


@login_required
def bookmarked_posts(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related("post")
    context = {"bookmarked_posts": [bookmark.post for bookmark in bookmarks]}
    return render(request, "blog_page/bookmarked_posts.html", context)
