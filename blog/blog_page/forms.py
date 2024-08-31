from django import forms
from .models import Post, Category, Tag, Comment
import json


class PostForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(), required=False, widget=forms.CheckboxSelectMultiple
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
        title = forms.CharField(widget=forms.TextInput(attrs={"id": "post-title"}))
        content = forms.CharField(widget=forms.Textarea(attrs={"id": "post-content"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].required = False


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
