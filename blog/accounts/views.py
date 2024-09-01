from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, CreateView
from django.contrib import messages
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    CustomUserChangeForm,
)
from .models import CustomUser
from django.views.generic import DetailView
from blog_page.models import Post, Bookmark


class RegisterView(CreateView):
    """
    사용자 등록을 위한 뷰입니다.

    Attributes:
        form_class: 사용자 생성에 사용될 폼 클래스
        template_name: 렌더링할 템플릿 파일 이름
        success_url: 성공 시 리디렉션할 URL
    """

    form_class = CustomUserCreationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        """
        폼이 유효할 경우 사용자를 생성하고 로그인합니다.

        Args:
            form: 유효성이 검증된 폼 인스턴스

        Returns:
            HttpResponse: 부모 클래스의 form_valid 메소드 결과
        """
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        폼이 유효하지 않을 경우 에러를 컨텍스트에 추가합니다.

        Args:
            form: 유효성 검증에 실패한 폼 인스턴스

        Returns:
            HttpResponse: 에러가 포함된 응답
        """
        context = self.get_context_data(form=form)
        context["errors"] = form.errors
        return self.render_to_response(context)


class LoginView(LoginView):
    """
    사용자 로그인을 위한 뷰입니다.

    Attributes:
        template_name: 렌더링할 템플릿 파일 이름
        authentication_form: 인증에 사용될 폼 클래스
    """

    template_name = "accounts/login.html"
    authentication_form = CustomAuthenticationForm

    def get_success_url(self):
        """
        로그인 성공 시 리디렉션할 URL을 반환합니다.

        Returns:
            str: 리디렉션할 URL
        """
        return reverse_lazy("home")


class LogoutView(LogoutView):
    """
    사용자 로그아웃을 위한 뷰입니다.

    Attributes:
        next_page: 로그아웃 후 리디렉션할 URL
    """

    next_page = reverse_lazy("home")


class CustomPasswordChangeView(PasswordChangeView):
    """
    비밀번호 변경을 위한 뷰입니다.

    Attributes:
        template_name: 렌더링할 템플릿 파일 이름
        success_url: 성공 시 리디렉션할 URL
    """

    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")


class ProfileView(LoginRequiredMixin, DetailView):
    """
    사용자 프로필을 표시하는 뷰입니다.

    Attributes:
        model: 사용할 모델 클래스
        template_name: 렌더링할 템플릿 파일 이름
        context_object_name: 컨텍스트에서 사용할 객체 이름
    """

    model = CustomUser
    template_name = "accounts/profile.html"
    context_object_name = "user"

    def get_object(self):
        """
        현재 로그인한 사용자 객체를 반환합니다.

        Returns:
            CustomUser: 현재 로그인한 사용자 객체
        """
        return self.request.user

    def get_context_data(self, **kwargs):
        """
        컨텍스트 데이터를 확장하여 사용자의 게시물과 북마크된 게시물을 추가합니다.

        Returns:
            dict: 확장된 컨텍스트 데이터
        """
        context = super().get_context_data(**kwargs)
        context["user_posts"] = Post.objects.filter(author=self.request.user).order_by(
            "-created_at"
        )
        context["bookmarked_posts"] = Post.objects.filter(
            bookmark__user=self.request.user
        ).order_by("-bookmark__created_at")
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    사용자 프로필 수정을 위한 뷰입니다.

    Attributes:
        model: 사용할 모델 클래스
        form_class: 프로필 수정에 사용될 폼 클래스
        template_name: 렌더링할 템플릿 파일 이름
        success_url: 성공 시 리디렉션할 URL
    """

    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        """
        현재 로그인한 사용자 객체를 반환합니다.

        Returns:
            CustomUser: 현재 로그인한 사용자 객체
        """
        return self.request.user
