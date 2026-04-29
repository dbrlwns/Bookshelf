from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from blogs.models import Blog


class BlogForm(forms.ModelForm):

    # 태그 입력 추가
    tag_names = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "tag1, tag2, ...",}))

    class Meta:
        model = Blog
        fields = ["title", "content"]
        widgets = {
            "content": CKEditorUploadingWidget(),
        }

    # 태그 파싱(문자열 to list)
    def clean_tag_names(self):
        value = self.cleaned_data["tag_names"]
        names = []
        for name in value.split(","):
            name = name.strip().lower()
            if name:
                names.append(name)
        return names
