from django.shortcuts import render

from .models import Book


def book_home(request):
    query = (request.GET.get("q") or "").strip()
    recent_books = Book.objects.order_by("-created_at")[:8]

    context = {
        "query": query,
        "recent_books": recent_books,
    }
    return render(request, "library/library.html", context)
