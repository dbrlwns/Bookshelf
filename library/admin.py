from django.contrib import admin

from .models import Book, BookNote


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(BookNote)
class BookNoteAdmin(admin.ModelAdmin):
    pass
