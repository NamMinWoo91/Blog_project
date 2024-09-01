from django import forms
from .models import Post, Category, Tag, Comment
import json


class PostForm(forms.ModelForm):
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
        super().__init__(*args, **kwargs)
        self.fields["category"].required = False
        if self.instance.pk:
            self.fields["tags"].initial = ", ".join(
                [tag.name for tag in self.instance.tags.all()]
            )

    def clean_tags(self):
        tag_string = self.cleaned_data.get("tags", "")
        tag_names = [name.strip() for name in tag_string.split(",") if name.strip()]
        return tag_names

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_tags(instance)
        return instance

    def save_tags(self, instance):
        instance.tags.clear()
        tag_names = self.cleaned_data.get("tags", [])
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            instance.tags.add(tag)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug", "is_public"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "카테고리 이름"}),
            "slug": forms.TextInput(attrs={"placeholder": "슬러그 입력"}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        if Category.objects.filter(slug=slug).exists():
            raise forms.ValidationError("이 슬러그는 이미 사용 중입니다.")
        return slug


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name", "slug", "is_public"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "태그 이름"}),
            "slug": forms.TextInput(attrs={"placeholder": "슬러그 입력"}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        if Tag.objects.filter(slug=slug).exists():
            raise forms.ValidationError("이 슬러그는 이미 사용 중입니다.")
        return slug


class CommentForm(forms.ModelForm):
    parent = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment
        fields = ["content", "parent"]
        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean_parent(self):
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
        cleaned_data = super().clean()
        if self.errors:
            raise forms.ValidationError(json.dumps(self.errors))
        return cleaned_data
