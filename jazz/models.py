from django.db import models

# Create your models here.
class AudioTransformJob(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    original_file = models.FileField(upload_to="audio/originals/")
    result_file = models.FileField(upload_to="audio/results/", blank=True, null=True)
    duration = models.FloatField(default=0, blank=True, null=True)
    bpm = models.FloatField(blank=True, null=True)
    style = models.CharField(max_length=50, default="swing")
    status = models.CharField(max_length=20, choices=Status, default="pending")
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
