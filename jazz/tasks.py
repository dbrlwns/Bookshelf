from celery import shared_task

from jazz.models import AudioTransformJob
from jazz.services import mix_jazz_loop


"""
/jazz/tasks.py

모델 객체를 인자로 받지 않는 것이 좋음. 
    Celery task 메시지는 Redis로 넘어갈 때, 직렬화되어 넘어가기 때문
    => worker에서 DB를 다시 조회
"""

# Celery 작업, 비동기로 실행 시 view에서 .delay()로 호출
@shared_task
def transform_jazz_task(jazz_id):
    jazz = AudioTransformJob.objects.get(id=jazz_id)
    mix_jazz_loop(jazz)