import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from ckeditor_uploader.fields import RichTextUploadingField


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True) # url에 사용
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"#{self.name}"

    """
    slug 저장 문제
    1. 한글 저장 시 slugify 미반환&중복문제 : 미반환 시 uuid값으로 slug 생성
    2. slugify(allow_unicode=True)로 한글 slug 가능
    3. Django와 django처럼 대소문자로 충돌 발생 : 소문자만 가능하게
    
    slug 중복 처리 개선?
    """
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name.strip().lower(), allow_unicode=True) or f"tag-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


class Blog(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blogs", # 사용자 모델에서 블로그 조회가능
    )
    title = models.CharField(max_length=200)
    tags = models.ManyToManyField(
        Tag,
        related_name="blogs",
        blank=True,
    )
    content = RichTextUploadingField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f'{self.id} - {self.title}'


class Comment(models.Model):
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"({self.blog_id}){self.author} : {self.content}"
