"""
Bookshelf/celery.py
: Celery 앱을 만드는 설정 파일

Celery 앱을 만들고 CELERY_로 시작하는 설정들을 읽어 적용


"""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Bookshelf.settings")

app = Celery("Bookshelf")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks() # django 앱 내에서 tasks.py 탐색


"""
1. brew services start redis로 redis 실행
2. celery -A Bookshelf worker -l info 로 Celery worker 실행
3. python manage.py runserver로 django 실행
"""