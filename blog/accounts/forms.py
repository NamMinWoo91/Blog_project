from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
)
from .models import CustomUser
from django.contrib.auth.forms import UserChangeForm


class CustomUserCreationForm(UserCreationForm):
    """
    새로운 사용자를 생성하기 위한 폼입니다.
    필수 필드와 함께 이메일, 닉네임, 프로필 이미지를 위한 추가 필드를 포함합니다.

    속성:
        email (EmailField): 사용자의 이메일 주소.
        nickname (CharField): 사용자의 닉네임.
        profile_image (ImageField): 사용자의 프로필 이미지.
    """

    email = forms.EmailField(required=True)
    nickname = forms.CharField(max_length=30, required=False)
    profile_image = forms.ImageField(required=False)

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
        """
        제공된 이메일 주소가 사이트 내에서 고유한지 확인합니다.

        반환값:
            str: 정제된 이메일 주소.

        예외:
            forms.ValidationError: 이메일이 이미 사용 중인 경우 발생합니다.
        """
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("이 이메일은 이미 사용 중입니다.")
        return email


class CustomAuthenticationForm(AuthenticationForm):
    """사용자 정의 인증 폼입니다."""

    pass


class CustomUserChangeForm(forms.ModelForm):
    """
    사용자 정보를 업데이트하기 위한 폼입니다.
    사용자의 모든 필드를 포함하지만, 비밀번호 필드는 관리자의 비밀번호 해시 표시 필드로 대체합니다.

    속성:
        email (EmailField): 사용자의 이메일 주소.
        nickname (CharField): 사용자의 닉네임.
        profile_image (ImageField): 사용자의 프로필 이미지.
        bio (CharField): 사용자의 자기소개.
        location (CharField): 사용자의 위치.
        birth_date (DateField): 사용자의 생년월일.
        website (URLField): 사용자의 웹사이트.
    """

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
        """
        제공된 이메일 주소가 사이트 내에서 고유한지 확인합니다.

        반환값:
            str: 정제된 이메일 주소.

        예외:
            forms.ValidationError: 이메일이 다른 사용자에 의해 이미 사용 중인 경우 발생합니다.
        """
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("이 이메일은 이미 사용 중입니다.")
        return email
