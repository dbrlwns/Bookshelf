from django.contrib import admin

from blogs.models import Blog


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    pass
