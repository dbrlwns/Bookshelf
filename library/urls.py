from django.urls import path

from .views import book_home


urlpatterns = [
    path("", book_home, name="book_home"),
]
