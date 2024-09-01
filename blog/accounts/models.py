from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    사용자 모델을 확장한 커스텀 사용자 모델입니다.

    이 모델은 Django의 기본 User 모델을 확장하여 추가적인 필드를 포함합니다.

    속성:
        nickname (CharField): 사용자의 별명. 최대 30자, 선택적.
        profile_image (ImageField): 사용자의 프로필 이미지. 선택적.
        bio (TextField): 사용자의 자기소개. 선택적.
        location (CharField): 사용자의 위치. 최대 100자, 선택적.
        birth_date (DateField): 사용자의 생년월일. 선택적.
        website (URLField): 사용자의 웹사이트 URL. 선택적.
    """

    nickname = models.CharField(max_length=30, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to="profile_images/", blank=True, null=True
    )
    bio = models.TextField(blank=True, verbose_name="자기소개")
    location = models.CharField(max_length=100, blank=True, verbose_name="위치")
    birth_date = models.DateField(null=True, blank=True, verbose_name="생년월일")
    website = models.URLField(blank=True, verbose_name="웹사이트")

    def __str__(self):
        """
        사용자 객체의 문자열 표현을 반환합니다.

        Returns:
            str: 사용자의 사용자명.
        """
        return self.username
