from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
import os


## 파일명 대신 uuid로 저장
def upload_to(instance, filename):
    ext = filename.split('.')[-1]   # 확장자 추출
    new_filename = str(uuid.uuid4()) + ext
    return os.path.join('profile_images', new_filename)


class User(AbstractUser):
    # profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    profile_image = models.ImageField(upload_to=upload_to, blank=True, null=True) # uuid 저장
