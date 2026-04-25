from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from blogs.models import Blog


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ["title", "content"]
        widgets = {
            "content": CKEditorUploadingWidget(),
        }
