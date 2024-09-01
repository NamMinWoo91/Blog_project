from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    UserChangeForm,
)
from .models import CustomUser
from django.contrib.auth.forms import UserChangeForm


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


class CustomUserChangeForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    nickname = forms.CharField(max_length=30, required=False)
    profile_image = forms.ImageField(required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    location = forms.CharField(max_length=100, required=False)
    birth_date = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    website = forms.URLField(required=False)

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "nickname",
            "profile_image",
            "bio",
            "location",
            "birth_date",
            "website",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("이 이메일은 이미 사용 중입니다.")
        return email
