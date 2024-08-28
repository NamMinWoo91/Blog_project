from django.contrib import admin
from django.urls import path

# from main.views import main_view  # 메인 페이지 뷰 임포트
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.home, name='home'),  # 여기가 홈 페이지
]
