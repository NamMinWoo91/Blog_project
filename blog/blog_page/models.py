from django.db import models
from accounts.models import CustomUser
from django.utils.text import slugify
from django.conf import settings
from django.contrib.auth import get_user_model

# from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    head_image = models.ImageField(upload_to="blog/images/%Y/%m/%d/", blank=True)
    file_upload = models.FileField(upload_to="blog/files/%Y/%m/%d/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    related_posts = models.ManyToManyField("self", blank=True, symmetrical=False)
    STATUS_CHOICES = [
        ("draft", "초안"),
        ("published", "발행됨"),
        ("pending", "보류 중"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")

    # author = models.ForeignKey(User, on_delete=models.CASCADE)
    author = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE)

    category = models.ForeignKey(
        "Category", null=True, blank=True, on_delete=models.SET_NULL
    )

    tags = models.ManyToManyField("Tag", blank=True)
    views_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"[{self.pk}]{self.title} :: {self.author}"

    def get_absolute_url(self):
        return f"/blog/{self.pk}/"

    def get_file_name(self):
        return self.file_upload.name.split("/")[-1]

    def get_file_ext(self):
        return self.get_file_name().split(".")[-1]

    def total_likes(self):
        return self.like_set.count()

    def is_liked_by(self, user):
        return self.like_set.filter(user=user).exists()


class Category(models.Model):
    name = models.CharField(max_length=25, unique=True)
    slug = models.SlugField(
        max_length=200, db_index=True, unique=True, allow_unicode=True
    )
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/blog/category/{self.slug}/"

    class Meta:
        verbose_name_plural = "Categories"


class Tag(models.Model):
    name = models.CharField(max_length=25, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True, blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/blog/tag/{self.slug}/"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="replies", on_delete=models.CASCADE
    )  # 대댓글을 위한 부모 댓글 참조

    def __str__(self):
        return f"[{self.post}] {self.content} :: {self.author}"

    def get_absolute_url(self):
        return f"/blog/{self.post.pk}/#comment-{self.pk}"

    class Meta:
        ordering = ["-id"]


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")


class Bookmark(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} bookmarked {self.post.title}"
