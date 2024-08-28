from django import forms
from .models import Post, Category, Tag, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "head_image", "file_upload", "category", "tags"]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug", "is_public"]


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name", "slug", "is_public"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
