from django.shortcuts import render

from .clients import search_books
from .models import Book


def book_home(request):
    query = (request.GET.get("q") or "").strip()
    recent_books = Book.objects.order_by("-created_at")[:8]

    # 최근 검색어1
    recent_keywords = request.session.get("recent_keywords", [])

    # 검색한 도서
    search_results = []
    if query:
        search_results = search_books(query)

        # 최근 검색어2
        if query in recent_keywords: recent_keywords.remove(query)
        recent_keywords.insert(0, query)
        recent_keywords = recent_keywords[:5]
        request.session["recent_keywords"] = recent_keywords


    context = {
        "query": query,
        "recent_books": recent_books,
        "search_results": search_results,
        "recent_keywords": recent_keywords,
    }
    return render(request, "library/library.html", context)
