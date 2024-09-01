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
    """
    게시물 목록을 보여주는 뷰입니다.

    Attributes:
        model: 사용할 모델
        ordering: 정렬 기준
        template_name: 사용할 템플릿 파일 이름
        context_object_name: 템플릿에서 사용할 객체 리스트의 이름
    """

    model = Post
    ordering = "-pk"
    template_name = "blog_page/post_list.html"
    context_object_name = "posts"

    def get_context_data(self, **kwargs):
        """
        템플릿에 전달할 컨텍스트 데이터를 설정합니다.

        Returns:
            dict: 추가된 컨텍스트 데이터
        """
        context = super().get_context_data(**kwargs)
        context["category_list"] = Category.objects.all().order_by("-name")
        context["no_category_post_count"] = Post.objects.filter(category=None).count()
        context["search_keyword"] = self.request.GET.get("q", "")
        return context

    def get_queryset(self):
        """
        표시할 게시물 쿼리셋을 반환합니다.
        검색어가 있는 경우 해당 검색어로 필터링합니다.

        Returns:
            QuerySet: 필터링된 게시물 쿼리셋
        """
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
    """
    개별 게시물의 상세 정보를 보여주는 뷰입니다.

    Attributes:
        model: 사용할 모델
        template_name: 사용할 템플릿 파일 이름
    """

    model = Post
    template_name = "blog_page/post_detail.html"

    def get_object(self, queryset=None):
        """
        조회수를 증가시키고 게시물 객체를 반환합니다.

        Returns:
            Post: 조회된 게시물 객체
        """
        post = super().get_object(queryset)
        post.views_count += 1
        post.save(update_fields=["views_count"])
        return post

    def get_context_data(self, **kwargs):
        """
        템플릿에 전달할 컨텍스트 데이터를 설정합니다.

        Returns:
            dict: 추가된 컨텍스트 데이터
        """
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
        """
        댓글 트리를 구성합니다.

        Args:
            comments (QuerySet): 상위 댓글 쿼리셋

        Returns:
            list: 댓글 트리 구조
        """
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
    """
    특정 카테고리의 게시물 목록을 보여주는 뷰 함수입니다.

    Args:
        request (HttpRequest): HTTP 요청 객체
        slug (str): 카테고리 슬러그

    Returns:
        HttpResponse: 렌더링된 카테고리 페이지
    """
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category).order_by("-pk")
    context = {
        "category": category,
        "posts": posts,
        "categories": Category.objects.all().order_by("-name"),
    }
    return render(request, "blog_page/category_list.html", context)


def tag_list(request):
    """
    모든 태그 목록을 보여주는 뷰 함수입니다.

    Args:
        request (HttpRequest): HTTP 요청 객체

    Returns:
        HttpResponse: 렌더링된 태그 목록 페이지
    """
    tags = Tag.objects.all().order_by("name")
    return render(request, "blog_page/tag_list.html", {"tags": tags})


def tag_page(request, slug):
    """
    특정 태그가 달린 게시물 목록을 보여주는 뷰 함수입니다.

    Args:
        request (HttpRequest): HTTP 요청 객체
        slug (str): 태그 슬러그

    Returns:
        HttpResponse: 렌더링된 태그 페이지
    """
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(tags=tag).order_by("-created_at")
    return render(request, "blog_page/tag_page.html", {"tag": tag, "posts": posts})


class PostCreate(LoginRequiredMixin, CreateView):
    """
    새 게시물을 작성하는 뷰입니다.

    Attributes:
        model: 사용할 모델
        form_class: 사용할 폼 클래스
        template_name: 사용할 템플릿 파일 이름
        success_url: 성공 시 리다이렉트할 URL
    """

    model = Post
    form_class = PostForm
    template_name = "blog_page/write_page.html"
    success_url = reverse_lazy("blog_page:post_list")

    def form_valid(self, form):
        """
        폼이 유효할 때 실행되는 메서드입니다.
        현재 로그인한 사용자를 작성자로 설정합니다.

        Args:
            form (PostForm): 제출된 폼

        Returns:
            HttpResponse: 폼 처리 결과
        """
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
            return super().form_valid(form)
        else:
            return redirect("/blog/")

    def form_invalid(self, form):
        """
        폼이 유효하지 않을 때 실행되는 메서드입니다.

        Args:
            form (PostForm): 유효하지 않은 폼

        Returns:
            HttpResponse: 오류 메시지가 포함된 응답
        """
        context = self.get_context_data(form=form)
        context["errors"] = form.errors
        return self.render_to_response(context)


class PostUpdate(LoginRequiredMixin, UpdateView):
    """
    기존 게시물을 수정하는 뷰입니다.

    Attributes:
        model: 사용할 모델
        form_class: 사용할 폼 클래스
        template_name: 사용할 템플릿 파일 이름
        success_url: 성공 시 리다이렉트할 URL
    """

    model = Post
    form_class = PostForm
    template_name = "blog_page/post_edit.html"
    success_url = reverse_lazy("blog_page:post_list")

    def get_object(self, queryset=None):
        """
        수정할 게시물 객체를 반환합니다.
        작성자만 수정할 수 있도록 확인합니다.

        Returns:
            Post: 수정할 게시물 객체

        Raises:
            PermissionDenied: 권한이 없는 경우
        """
        obj = super().get_object(queryset)
        if obj.author != self.request.user:
            raise PermissionDenied
        return obj

    def form_valid(self, form):
        """
        폼이 유효할 때 실행되는 메서드입니다.
        태그를 처리합니다.

        Args:
            form (PostForm): 제출된 폼

        Returns:
            HttpResponse: 폼 처리 결과
        """
        response = super().form_valid(form)
        self.object.tags.clear()
        for tag_name in form.cleaned_data["tags"]:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            self.object.tags.add(tag)
        return response

    def get_initial(self):
        """
        폼의 초기 데이터를 설정합니다.

        Returns:
            dict: 초기 데이터
        """
        initial = super().get_initial()
        initial["tags"] = ", ".join(tag.name for tag in self.object.tags.all())
        return initial


class PostDelete(LoginRequiredMixin, DeleteView):
    """
    게시물을 삭제하는 뷰입니다.

    Attributes:
        model: 사용할 모델
        success_url: 성공 시 리다이렉트할 URL
    """

    model = Post
    success_url = reverse_lazy("blog_page:post_list")

    def dispatch(self, request, *args, **kwargs):
        """
        요청을 처리하기 전에 권한을 확인합니다.

        Returns:
            HttpResponse: 처리 결과
        """
        post = self.get_object()
        if post.author != request.user:
            messages.error(request, "You do not have permission to delete this post.")
            return HttpResponseRedirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        POST 요청을 처리합니다.

        Returns:
            HttpResponse: 삭제 처리 결과
        """
        post = self.get_object()
        if post.author != request.user:
            messages.error(request, "You do not have permission to delete this post.")
            return HttpResponseRedirect(self.success_url)

        self.object = post
        self.object.delete()
        messages.success(request, "Post has been successfully deleted.")
        return redirect(self.success_url)


class PostSearchView(ListView):
    """
    게시물 검색 결과를 보여주는 뷰입니다.

    Attributes:
        model: 사용할 모델
        template_name: 사용할 템플릿 파일 이름
        context_object_name: 템플릿에서 사용할 객체 리스트의 이름
    """

    model = Post
    template_name = "blog_page/post_search.html"
    context_object_name = "post_list"

    def get_queryset(self):
        """
        검색 결과 쿼리셋을 반환합니다.

        Returns:
            QuerySet: 검색된 게시물 쿼리셋
        """
        query = self.request.GET.get("q")
        if query:
            return Post.objects.filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(tags__name__icontains=query)
            ).distinct()
        return Post.objects.none()

    def get_context_data(self, **kwargs):
        """
        템플릿에 전달할 컨텍스트 데이터를 설정합니다.

        Returns:
            dict: 추가된 컨텍스트 데이터
        """
        context = super().get_context_data(**kwargs)
        context["search_keyword"] = self.request.GET.get("q", "")
        return context


logger = logging.getLogger(__name__)


@method_decorator(require_POST, name="dispatch")
class CommentCreate(LoginRequiredMixin, View):
    """댓글을 생성하는 뷰입니다."""

    def post(self, request, pk):
        """
        POST 요청을 처리하여 댓글을 생성합니다.

        Args:
            request (HttpRequest): HTTP 요청 객체
            pk (int): 게시물의 기본 키

        Returns:
            JsonResponse: 처리 결과를 JSON 형식으로 반환
        """
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
            return JsonResponse
