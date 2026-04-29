"""
/library/clients.py

외부 API(알라딘 openAPI)와 통신하는 파일
-> 알라딘 api 호출 + 받은 응답을 dictionary로 변환

알라딘 API 사용 예제(https://blog.aladin.co.kr/openapi/5353301)
"""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from django.conf import settings
import dotenv
import os
dotenv.load_dotenv()

api_key = os.environ.get("ALADIN_API_KEY", "")
ALADIN_ITEM_SEARCH_URL = f"https://www.aladin.co.kr/ttb/api/ItemSearch.aspx"


class AladinAPIError(Exception):
    pass


def normalize_aladin_item(item):
    return {
        "title": item.get("title", ""),
        "author": item.get("author", ""),
        "publisher": item.get("publisher", ""),
        "isbn": item.get("isbn13") or item.get("isbn", ""),
        "thumbnail_url": item.get("cover", ""),
        "description": item.get("description", ""),
        "publish_date": item.get("pubDate", ""),
        "source": "aladin",
        "source_id": str(item.get("itemId", "")),
        "link": item.get("link", ""),
    }


def search_books(query, *, max_results=10, start=1, query_type="Keyword"):
    query = query.strip()
    if not query:
        return []

    if not api_key:
        raise AladinAPIError("ALADIN_API_KEY is not configured.")

    params = {
        "ttbkey": api_key,
        "Query": query,
        "QueryType": query_type,
        "MaxResults": max_results,
        "start": start,
        "SearchTarget": "Book",
        "output": "js",
        "Version": "20131101",
    }
    url = f"{ALADIN_ITEM_SEARCH_URL}?{urlencode(params)}"
    # print(urlencode(params))
    try:
        with urlopen(url, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise AladinAPIError(f"Aladin API returned HTTP {error.code}.") from error
    except URLError as error:
        raise AladinAPIError("Could not connect to Aladin API.") from error
    except json.JSONDecodeError as error:
        raise AladinAPIError("Aladin API returned invalid JSON.") from error

    items = payload.get("item", [])
    return [normalize_aladin_item(item) for item in items]
