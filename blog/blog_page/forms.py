from django import forms
from .models import Post, Category, Tag, Comment
import json


class PostForm(forms.ModelForm):
    """
    게시물 생성 및 수정을 위한 폼 클래스입니다.

    Attributes:
        tags (CharField): 태그 입력을 위한 필드. 쉼표로 구분된 문자열로 입력받습니다.
    """

    tags = forms.CharField(
        required=False,
        help_text="쉼표로 구분하여 태그를 입력하세요.",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Post
        fields = [
            "title",
            "content",
            "head_image",
            "file_upload",
            "category",
            "tags",
            "status",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"id": "post-title", "class": "form-control"}
            ),
            "content": forms.Textarea(
                attrs={"id": "post-content", "class": "form-control"}
            ),
        }

    def __init__(self, *args, **kwargs):
        """
        폼 초기화 메서드입니다. 카테고리를 선택적으로 만들고,
        수정 시 기존 태그를 불러옵니다.
        """
        super().__init__(*args, **kwargs)
        self.fields["category"].required = False
        if self.instance.pk:
            self.fields["tags"].initial = ", ".join(
                [tag.name for tag in self.instance.tags.all()]
            )

    def clean_tags(self):
        """
        태그 필드를 정제합니다. 쉼표로 구분된 태그를 리스트로 변환합니다.

        Returns:
            list: 정제된 태그 이름 리스트
        """
        tag_string = self.cleaned_data.get("tags", "")
        tag_names = [name.strip() for name in tag_string.split(",") if name.strip()]
        return tag_names

    def save(self, commit=True):
        """
        폼을 저장하고 태그를 처리합니다.

        Args:
            commit (bool): 데이터베이스에 즉시 저장할지 여부

        Returns:
            Post: 저장된 Post 인스턴스
        """
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_tags(instance)
        return instance

    def save_tags(self, instance):
        """
        게시물에 태그를 저장합니다.

        Args:
            instance (Post): 태그를 저장할 Post 인스턴스
        """
        instance.tags.clear()
        tag_names = self.cleaned_data.get("tags", [])
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            instance.tags.add(tag)


class CategoryForm(forms.ModelForm):
    """카테고리 생성 및 수정을 위한 폼 클래스입니다."""

    class Meta:
        model = Category
        fields = ["name", "slug", "is_public"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "카테고리 이름"}),
            "slug": forms.TextInput(attrs={"placeholder": "슬러그 입력"}),
        }

    def clean_slug(self):
        """
        슬러그의 유일성을 검증합니다.

        Returns:
            str: 검증된 슬러그

        Raises:
            forms.ValidationError: 슬러그가 이미 존재하는 경우
        """
        slug = self.cleaned_data.get("slug")
        if Category.objects.filter(slug=slug).exists():
            raise forms.ValidationError("이 슬러그는 이미 사용 중입니다.")
        return slug


class TagForm(forms.ModelForm):
    """태그 생성 및 수정을 위한 폼 클래스입니다."""

    class Meta:
        model = Tag
        fields = ["name", "slug", "is_public"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "태그 이름"}),
            "slug": forms.TextInput(attrs={"placeholder": "슬러그 입력"}),
        }

    def clean_slug(self):
        """
        슬러그의 유일성을 검증합니다.

        Returns:
            str: 검증된 슬러그

        Raises:
            forms.ValidationError: 슬러그가 이미 존재하는 경우
        """
        slug = self.cleaned_data.get("slug")
        if Tag.objects.filter(slug=slug).exists():
            raise forms.ValidationError("이 슬러그는 이미 사용 중입니다.")
        return slug


class CommentForm(forms.ModelForm):
    """댓글 생성 및 수정을 위한 폼 클래스입니다."""

    parent = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment
        fields = ["content", "parent"]
        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean_parent(self):
        """
        부모 댓글의 존재 여부를 검증합니다.

        Returns:
            Comment or None: 검증된 부모 댓글 객체 또는 None

        Raises:
            forms.ValidationError: 부모 댓글이 존재하지 않는 경우
        """
        parent = self.cleaned_data.get("parent")
        if parent:
            try:
                return Comment.objects.get(id=parent)
            except Comment.DoesNotExist:
                raise forms.ValidationError(
                    json.dumps({"parent": ["부모 댓글이 존재하지 않습니다."]})
                )
        return None

    def clean(self):
        """
        폼 전체의 유효성을 검사합니다.

        Returns:
            dict: 정제된 데이터

        Raises:
            forms.ValidationError: 폼에 오류가 있는 경우
        """
        cleaned_data = super().clean()
        if self.errors:
            raise forms.ValidationError(json.dumps(self.errors))
        return cleaned_data
