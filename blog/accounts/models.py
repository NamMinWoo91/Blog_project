from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=30, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to="profile_images/", blank=True, null=True
    )
    bio = models.TextField(blank=True, verbose_name="자기소개")
    location = models.CharField(max_length=100, blank=True, verbose_name="위치")
    birth_date = models.DateField(null=True, blank=True, verbose_name="생년월일")
    website = models.URLField(blank=True, verbose_name="웹사이트")

    def __str__(self):
        return self.username
