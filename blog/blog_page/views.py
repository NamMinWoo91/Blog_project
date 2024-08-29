from django.http.response import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Category, Tag, Comment
from .forms import CommentForm
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseRedirect
from .forms import PostForm


class PostList(ListView):
    model = Post
    ordering = "-pk"
    template_name = "blog_page/post_list.html"  # 템플릿 경로 설정
    context_object_name = "posts"  # 템플릿에서 사용할 객체 이름 설정

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category_list"] = Category.objects.all().order_by(
            "-name"
        )  # 카테고리 리스트
        context["no_category_post_count"] = Post.objects.filter(
            category=None
        ).count()  # 카테고리가 없는 포스트 수
        context["search_keyword"] = self.request.GET.get("q", "")  # 검색 키워드 추가
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
        context = super(PostDetail, self).get_context_data(**kwargs)
        context["categories"] = Category.objects.all().order_by("-name")
        context["no_category_post_count"] = Post.objects.filter(category=None).count()
        context["comment_form"] = CommentForm
        context["current_user"] = self.request.user

        # 댓글을 구조화된 형태로 추가
        comments = self.object.comment_set.filter(parent=None).order_by("created_at")
        comment_tree = []
        for comment in comments:
            comment_dict = {
                "comment": comment,
                "replies": comment.replies.all().order_by("created_at"),
            }
            comment_tree.append(comment_dict)
        context["comment_tree"] = comment_tree

        return context


def category_page(request, slug):
    category = Category.objects.get(slug=slug)
    categories = Category.objects.all().order_by("-name")
    context = {
        "post_list": Post.objects.filter(category=category).order_by("-pk"),
        "categories": categories,
        "no_category_post_count": Post.objects.filter(category=None).count(),
        "category": category,
        "category_list": Category.objects.all().order_by("-name"),
    }
    return render(request, "blog_page/post_list.html", context)


def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()
    categories = Category.objects.all().order_by("-name")
    context = {
        "post_list": post_list,
        "categories": categories,
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
        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.author = current_user
            post = form.save(commit=False)
            post.save()

            tag_names = form.cleaned_data["tags"]
            for tag_name in tag_names:
                slug = slugify(tag_name, allow_unicode=True)
                tag, created = Tag.objects.get_or_create(
                    name=tag_name, defaults={"slug": slug}
                )
                post.tags.add(tag)

            return super().form_valid(form)
        else:
            return redirect("/blog/")


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog_page/post_edit.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.tags.clear()
        tag_names = form.cleaned_data["tags"]
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            self.object.tags.add(tag)
        return response

    def get_initial(self):
        initial = super().get_initial()
        initial["tags"] = ", ".join(tag.name for tag in self.object.tags.all())
        return initial


def new_comment(request, pk, parent_comment_id=None):
    post = get_object_or_404(Post, pk=pk)
    if request.user.is_authenticated:
        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                if parent_comment_id:
                    parent_comment = get_object_or_404(Comment, pk=parent_comment_id)
                    comment.parent = parent_comment  # 대댓글의 부모 댓글 지정
                comment.save()
                return redirect(post.get_absolute_url())
        else:
            form = CommentForm()
        return render(request, "blog_page/comment_form.html", {"form": form})
    return redirect("login_url")


class PostDelete(DeleteView):
    model = Post
    template_name = "blog_page/post_delete.html"  # 삭제 확인용 템플릿
    success_url = reverse_lazy("blog_page:post_list")  # 삭제 성공 후 리다이렉트할 URL

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            messages.error(request, "You do not have permission to delete this post.")
            return HttpResponseRedirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)


class PostSearchView(ListView):
    model = Post
    template_name = "blog_page/post_list.html"  # 사용할 템플릿 경로
    context_object_name = "post_list"  # 템플릿에서 사용할 객체 이름 설정
    paginate_by = 10  # 페이지네이션을 사용할 경우 페이지당 표시할 포스트 수

    def get_queryset(self):
        queryset = super().get_queryset()
        tag_slug = self.kwargs.get("tag", "")
        search_keyword = self.request.GET.get("q", "")
        search_by = self.request.GET.get("search_by", "title")

        # 기본 필터링: 태그에 따른 필터링
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        # 검색어 필터링
        if search_keyword:
            if search_by == "title":
                queryset = queryset.filter(title__icontains=search_keyword)
            elif search_by == "category":
                queryset = queryset.filter(category__name__icontains=search_keyword)
            else:
                # 모든 필드에 대해 검색 (제목, 내용, 태그)
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
        return super(CommentUpdate, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if request.user.is_authenticated and comment.author == request.user:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        return HttpResponseForbidden("You are not allowed to update this comment")


def delete_comment(request, pk):
    if request.user.is_authenticated:
        comment = get_object_or_404(Comment, pk=pk)
        if comment.author == request.user:
            comment.delete()
            return redirect(comment.post.get_absolute_url())
        return HttpResponseForbidden("You are not allowed to delete this comment")
    return redirect("/blog/")


delete = DeleteView.as_view()
