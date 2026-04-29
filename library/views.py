from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .clients import search_books
from .models import BookNote
from .services import save_book_from_api_data


def book_home(request):
    query = (request.GET.get("q") or "").strip()
    recent_notes = BookNote.objects.select_related("book", "user").order_by("-created_at")[:6]

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
        "recent_notes": recent_notes,
        "search_results": search_results,
        "recent_keywords": recent_keywords,
    }
    return render(request, "library/library.html", context)


@login_required
@require_POST
def book_note_create(request):
    book_data = {
        "title": request.POST.get("book_title", ""),
        "author": request.POST.get("book_author", ""),
        "publisher": request.POST.get("book_publisher", ""),
        "isbn": request.POST.get("book_isbn", ""),
        "thumbnail_url": request.POST.get("book_thumbnail_url", ""),
        "description": request.POST.get("book_description", ""),
        "publish_date": request.POST.get("book_publish_date", ""),
    }
    note_title = (request.POST.get("title") or "").strip()
    note_content = (request.POST.get("content") or "").strip()

    if not note_title or not note_content:
        messages.error(request, "invalid your input")
        return redirect("book_home")

    try:
        book, _ = save_book_from_api_data(book_data)
    except ValueError:
        messages.error(request, "can't save book, too short")
        return redirect("book_home")

    BookNote.objects.create(
        user=request.user,
        book=book,
        title=note_title,
        content=note_content,
    )
    messages.success(request, "Book review successfully saved")
    return redirect("book_home")
