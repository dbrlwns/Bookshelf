from django.conf import settings
from django.db import models

from ckeditor_uploader.fields import RichTextUploadingField


class Blog(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blogs", # 사용자 모델에서 블로그 조회가능
    )
    title = models.CharField(max_length=200)
    content = RichTextUploadingField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f'{self.id} - {self.title}'
