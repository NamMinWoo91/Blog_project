from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("nickname", "profile_image")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("nickname", "profile_image")}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
