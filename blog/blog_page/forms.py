from django import forms
from .models import Post, Category, Tag, Comment


class PostForm(forms.ModelForm):
    tags = forms.CharField(required=False, help_text="쉼표로 구분하여 입력하세요")

    class Meta:
        model = Post
        fields = ["title", "content", "head_image", "file_upload", "category"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 5, "cols": 20}),
            "title": forms.TextInput(attrs={"placeholder": "제목을 입력하세요"}),
            "head_image": forms.ClearableFileInput(attrs={"multiple": False}),
        }

    def clean_tags(self):
        tag_names = self.cleaned_data.get("tags", "")
        tag_list = [name.strip() for name in tag_names.split(",") if name.strip()]
        return tag_list


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
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 3, "cols": 20, "placeholder": "댓글을 입력하세요"}
            ),
        }

    def clean_content(self):
        content = self.cleaned_data.get("content")
        if not content:
            raise forms.ValidationError("댓글 내용을 입력해야 합니다.")
        return content
