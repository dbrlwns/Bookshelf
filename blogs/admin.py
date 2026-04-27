from django.contrib import admin

from blogs.models import Blog, Comment, Tag


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    filter_horizontal = ("tags",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass
