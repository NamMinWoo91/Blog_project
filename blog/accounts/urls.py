from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    CustomPasswordChangeView,
    ProfileUpdateView,
    ProfileView,  # 추가: 프로필 보기 뷰
)

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "password_change/", CustomPasswordChangeView.as_view(), name="password_change"
    ),
    path("profile_edit/", ProfileUpdateView.as_view(), name="profile_edit"),
    path("profile/", ProfileView.as_view(), name="profile"),  # 추가: 프로필 보기 URL
]
