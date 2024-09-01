from django.db import models
from accounts.models import CustomUser
from django.utils.text import slugify
from django.conf import settings
from django.contrib.auth import get_user_model


class Post(models.Model):
    """
    블로그 게시물을 나타내는 모델 클래스입니다.

    Attributes:
        title (str): 게시물 제목
        content (str): 게시물 내용
        head_image (ImageField): 게시물 대표 이미지
        file_upload (FileField): 첨부 파일
        created_at (datetime): 게시물 생성 시간
        updated_at (date): 게시물 최종 수정 일자
        related_posts (ManyToManyField): 관련 게시물들
        status (str): 게시물 상태 (초안, 발행됨, 보류 중)
        author (ForeignKey): 게시물 작성자
        category (ForeignKey): 게시물 카테고리
        tags (ManyToManyField): 게시물 태그들
        views_count (int): 조회수
    """

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
    author = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE)
    category = models.ForeignKey(
        "Category", null=True, blank=True, on_delete=models.SET_NULL
    )
    tags = models.ManyToManyField("Tag", blank=True)
    views_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        """게시물의 문자열 표현을 반환합니다."""
        return f"[{self.pk}]{self.title} :: {self.author}"

    def get_absolute_url(self):
        """게시물의 절대 URL을 반환합니다."""
        return f"/blog/{self.pk}/"

    def get_file_name(self):
        """첨부 파일의 이름을 반환합니다."""
        return self.file_upload.name.split("/")[-1]

    def get_file_ext(self):
        """첨부 파일의 확장자를 반환합니다."""
        return self.get_file_name().split(".")[-1]

    def total_likes(self):
        """게시물의 총 좋아요 수를 반환합니다."""
        return self.like_set.count()

    def is_liked_by(self, user):
        """
        주어진 사용자가 이 게시물을 좋아하는지 확인합니다.

        Args:
            user (CustomUser): 확인할 사용자 객체

        Returns:
            bool: 사용자가 게시물을 좋아하면 True, 아니면 False
        """
        return self.like_set.filter(user=user).exists()


class Category(models.Model):
    """
    블로그 게시물의 카테고리를 나타내는 모델 클래스입니다.

    Attributes:
        name (str): 카테고리 이름
        slug (str): URL에 사용될 슬러그
        is_public (bool): 공개 여부
        created_at (datetime): 생성 시간
        updated_at (date): 최종 수정 일자
    """

    name = models.CharField(max_length=25, unique=True)
    slug = models.SlugField(
        max_length=200, db_index=True, unique=True, allow_unicode=True
    )
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        """카테고리의 문자열 표현을 반환합니다."""
        return self.name

    def get_absolute_url(self):
        """카테고리의 절대 URL을 반환합니다."""
        return f"/blog/category/{self.slug}/"

    class Meta:
        verbose_name_plural = "Categories"


class Tag(models.Model):
    """
    블로그 게시물의 태그를 나타내는 모델 클래스입니다.

    Attributes:
        name (str): 태그 이름
        slug (str): URL에 사용될 슬러그
        is_public (bool): 공개 여부
        created_at (datetime): 생성 시간
        updated_at (date): 최종 수정 일자
        description (str): 태그 설명
    """

    name = models.CharField(max_length=25, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True, blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        태그를 저장할 때 슬러그를 자동으로 생성합니다.
        """
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        """태그의 문자열 표현을 반환합니다."""
        return self.name

    def get_absolute_url(self):
        """태그의 절대 URL을 반환합니다."""
        return f"/blog/tag/{self.slug}/"


class Comment(models.Model):
    """
    블로그 게시물의 댓글을 나타내는 모델 클래스입니다.

    Attributes:
        post (ForeignKey): 연결된 게시물
        author (ForeignKey): 댓글 작성자
        content (str): 댓글 내용
        created_at (datetime): 생성 시간
        updated_at (datetime): 최종 수정 시간
        parent (ForeignKey): 부모 댓글 (대댓글인 경우)
    """

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="replies", on_delete=models.CASCADE
    )

    def __str__(self):
        """댓글의 문자열 표현을 반환합니다."""
        return f"[{self.post}] {self.content} :: {self.author}"

    def get_absolute_url(self):
        """댓글의 절대 URL을 반환합니다."""
        return f"/blog/{self.post.pk}/#comment-{self.pk}"

    class Meta:
        ordering = ["-id"]


class Like(models.Model):
    """
    블로그 게시물의 좋아요를 나타내는 모델 클래스입니다.

    Attributes:
        user (ForeignKey): 좋아요를 누른 사용자
        post (ForeignKey): 좋아요가 눌린 게시물
        created_at (datetime): 생성 시간
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")


class Bookmark(models.Model):
    """
    블로그 게시물의 북마크를 나타내는 모델 클래스입니다.

    Attributes:
        user (ForeignKey): 북마크를 한 사용자
        post (ForeignKey): 북마크된 게시물
        created_at (datetime): 생성 시간
    """

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        """북마크의 문자열 표현을 반환합니다."""
        return f"{self.user.username} bookmarked {self.post.title}"
