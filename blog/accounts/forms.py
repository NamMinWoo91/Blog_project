from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # 이메일 필드 추가
    nickname = forms.CharField(max_length=30, required=False)  # 닉네임 추가
    profile_image = forms.ImageField(required=False)  # 프로필 이미지 추가

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "password1",
            "password2",
            "nickname",
            "profile_image",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("이 이메일은 이미 사용 중입니다.")
        return email

class CustomAuthenticationForm(AuthenticationForm):
    pass

class CustomUserChangeForm(UserChangeForm):
    email = forms.EmailField(required=True)  # 이메일 필드 추가
    nickname = forms.CharField(max_length=30, required=False)  # 닉네임 추가
    profile_image = forms.ImageField(required=False)  # 프로필 이미지 추가

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "nickname",
            "profile_image",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("이 이메일은 이미 사용 중입니다.")
        return email
