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
from blog_page.models import Post


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(
            self.request, f"안녕하세요, {user.username}님! 회원가입을 환영합니다."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, "회원가입 중 오류가 발생했습니다. 아래 내용을 확인해주세요."
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "회원가입"
        return context


class LoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = CustomAuthenticationForm

    def get_success_url(self):
        return reverse_lazy("home")  # 로그인 후 리디렉션할 URL


class LogoutView(LogoutView):
    next_page = reverse_lazy("home")  # 로그아웃 후 리디렉션할 URL


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")


from django.urls import reverse_lazy


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")


class ProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "accounts/profile.html"  # 프로필 페이지 템플릿
    context_object_name = "user"  # 템플릿에서 사용할 컨텍스트 이름

    def get_object(self):
        return self.request.user  # 현재 로그인한 사용자

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_posts"] = Post.objects.filter(author=self.request.user).order_by(
            "-created_at"
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        return self.request.user  # 현재 로그인한 사용자
