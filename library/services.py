from datetime import datetime

from django.db import transaction

from .models import Book

"""
/library/services.py

알라딘 API로 받은 도서 응답을 Book Model에 저장 전 파싱하고,
    저장된 상태면 재사용하도록 동작함.


"""

# isbn의 dash나 공백을 지움.
def normalize_isbn(value):
    if not value:
        return ""
    return str(value).replace("-", "").replace(" ", "").strip()


# 문자열인 날짜를 date 형으로 반환
def parse_publish_date(value):
    if not value:
        return None

    value = str(value).strip()
    for date_format in ("%Y-%m-%d", "%Y%m%d", "%Y-%m", "%Y"):
        try:
            parsed = datetime.strptime(value, date_format)
            return parsed.date()
        except ValueError:
            continue
    return None


# 인자에 맞는 데이터 반환
def pick_first(data, *keys): # 가변 인자
    for key in keys:
        value = data.get(key)
        if value:
            return value
    return ""


# API마다 다른 키 이름을 Book 필드에 맞게 반환
def normalize_book_data(data):
    isbn = normalize_isbn(pick_first(data, "isbn13", "isbn", "isbn10"))
    author = pick_first(data, "author", "authors")
    if isinstance(author, list):
        author = ", ".join(author)

    return {
        "title": pick_first(data, "title", "name").strip(),
        "author": str(author).strip(),
        "publisher": pick_first(data, "publisher").strip(),
        "isbn": isbn,
        "thumbnail_url": pick_first(data, "thumbnail_url", "thumbnail", "image").strip(),
        "description": pick_first(data, "description", "contents", "summary").strip(),
        "publish_date": parse_publish_date(
            pick_first(data, "publish_date", "published_date", "pubdate")
        ),
    }


# 도서 찾기(isbn, title+author 이용)
def find_existing_book(book_data):
    isbn = book_data.get("isbn")
    if isbn:
        return Book.objects.filter(isbn=isbn).first()

    title = book_data.get("title")
    author = book_data.get("author")
    if title and author:
        return Book.objects.filter(title__iexact=title, author__iexact=author).first()

    return None



@transaction.atomic # 트랜잭션 데코레이터 : 이 함수의 DB 작업을 한 묶음으로 처리
def save_book_from_api_data(data):
    book_data = normalize_book_data(data)
    if not book_data["title"]:
        raise ValueError("Book title is required.")

    book = find_existing_book(book_data)
    if book is None:
        return Book.objects.create(**book_data), True

    for field, value in book_data.items():
        if value not in ("", None):
            setattr(book, field, value)
    book.save()
    return book, False


"""
키워드 인자
Book.objects.create(**book_data)는 (book_data는 딕셔너리)
    Book.objects.create(
    title="python",
    author="dbrlwns",
    ...
    )       로 바뀜.
    
그리고 함수에서 def ex(**kwargs):
    처럼 사용하면 ex(title="python", author="dbrlwns)
        호출 시 kwargs 인자에는 {title="python", author="dbrlwns}가 저장됨.
        
        
setattr(book, field, value) 처럼 호출하면
    book.field = value 와 같음.
    즉, 객체의 속성을 문자열 이름으로 설정
    반복문으로 필드 이름이 변수로 들어오므로 사용함.
"""