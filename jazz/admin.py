from django.contrib import admin

from jazz.models import AudioTransformJob


# Register your models here.
@admin.register(AudioTransformJob)
class JazzAdmin(admin.ModelAdmin):
    pass