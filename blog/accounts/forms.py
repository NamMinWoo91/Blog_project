from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    UserChangeForm,
)
from .models import CustomUser
from django.contrib.auth.forms import UserChangeForm


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, help_text="필수 항목입니다. 유효한 이메일 주소를 입력해주세요."
    )
    nickname = forms.CharField(
        max_length=30,
        required=False,
        help_text="선택 항목입니다. 30자 이내로 입력해주세요.",
    )
    profile_image = forms.ImageField(
        required=False, help_text="선택 항목입니다. 프로필 이미지를 업로드해주세요."
    )

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
        if email and CustomUser.objects.filter(email=email).exists():
            raise ValidationError("이미 사용 중인 이메일 주소입니다.")
        return email

    def clean_nickname(self):
        nickname = self.cleaned_data.get("nickname")
        if nickname and CustomUser.objects.filter(nickname=nickname).exists():
            raise ValidationError("이미 사용 중인 닉네임입니다.")
        return nickname

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.nickname = self.cleaned_data.get("nickname")
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    pass


class CustomUserChangeForm(UserChangeForm):
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
