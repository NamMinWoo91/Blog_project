from django.http.response import HttpResponse
from django.shortcuts import render, redirect
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

    # 조회수 증가 로직 추가
    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        post.views_count += 1  # 조회수 1 증가
        post.save(update_fields=["views_count"])  # 조회수 필드만 업데이트
        return post

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)
        context["categories"] = Category.objects.all().order_by("-name")
        context["no_category_post_count"] = Post.objects.filter(category=None).count()
        context["comment_form"] = CommentForm
        context["current_user"] = self.request.user
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
    fields = ["title", "content", "head_image", "file_upload", "category"]
    template_name = "blog_page/write_page.html"

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get("tags_str")
            if tags_str:
                tags_str = tags_str.strip().replace(",", ";")
                tags_list = tags_str.split(";")
                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)
            return response
        else:
            return redirect("/blog/")


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ["title", "content", "head_image", "file_upload", "category", "tags"]
    template_name = "blog_page/post_edit.html"  # 템플릿 경로 설정

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.author = current_user
            return super(PostUpdate, self).form_valid(form)
        else:
            return redirect("/blog/")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            post = self.get_object()
            if post.author == request.user:
                return super().dispatch(request, *args, **kwargs)
            else:
                return HttpResponse("You are not allowed to update this post")
        return super().dispatch(request, *args, **kwargs)


def new_comment(request, pk):
    if request.user.is_authenticated:
        post = Post.objects.get(pk=pk)
        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
        else:
            form = CommentForm()
        return render(request, "blog_page/comment_form.html", {"form": form})


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
                    Q(title__icontains=search_keyword) |
                    Q(content__icontains=search_keyword) |
                    Q(tags__name__icontains=search_keyword)
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
    template_name = "blog_page/comment_form.html"  # 템플릿 경로 설정

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.author = current_user
            return super(CommentUpdate, self).form_valid(form)
        else:
            return redirect("/blog/")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            comment = self.get_object()
            if comment.author == request.user:
                return super().dispatch(request, *args, **kwargs)
            else:
                return HttpResponse("You are not allowed to update this comment")
        return super().dispatch(request, *args, **kwargs)


def delete_comment(request, pk):
    if request.user.is_authenticated:
        comment = Comment.objects.get(pk=pk)
        if comment.author == request.user:
            comment.delete()
            return redirect(comment.post.get_absolute_url())
        else:
            return HttpResponse("You are not allowed to delete this comment")
    return redirect("/blog/")


delete = DeleteView.as_view()
