from django.db import models

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100, blank=True)
    publisher = models.CharField(max_length=100, blank=True)

    isbn = models.CharField(max_length=20, blank=True, db_index=True) # 색인 추가

    thumbnail_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    publish_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} - {self.isbn}'