from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

# Create your models here.

class Video(models.Model):
    PROCESSING_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to='videos/original/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov'])]
    )
    compressed_file = models.FileField(upload_to='videos/compressed/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    size = models.BigIntegerField(null=True, blank=True)  # in bytes
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_videos'
    )

    def __str__(self):
        return self.title

class VideoStream(models.Model):
    QUALITY_CHOICES = (
        ('240p', '240p'),
        ('360p', '360p'),
        ('480p', '480p'),
        ('720p', '720p'),
        ('1080p', '1080p'),
    )

    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='streams')
    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES)
    file = models.FileField(upload_to='videos/streams/')
    bitrate = models.IntegerField()  # in kbps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('video', 'quality')
