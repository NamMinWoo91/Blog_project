from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]  # 댓글 작성에 필요한 필드만 포함

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].widget = forms.Textarea(
            attrs={"rows": 4, "placeholder": "댓글을 작성하세요..."}
        )
        self.fields["content"].label = "댓글 내용"
