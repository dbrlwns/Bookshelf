from django.urls import path

from .views import book_home, book_note_create


urlpatterns = [
    path("", book_home, name="book_home"),
    path("notes/add/", book_note_create, name="book_note_create"),
]
