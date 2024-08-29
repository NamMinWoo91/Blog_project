from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    PasswordChangeView,
    ProfileUpdateView,
)

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password_change/", PasswordChangeView.as_view(), name="password_change"),
    path("profile_edit/", ProfileUpdateView.as_view(), name="profile_edit"),
]
