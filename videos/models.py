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
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'webm', 'm4v', '3gp'])]
    )
    compressed_file = models.FileField(upload_to='videos/compressed/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', null=True, blank=True)
    all_thumbnails = models.JSONField(default=list, blank=True)  # Store list of all thumbnail paths
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
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='videos')

    def __str__(self):
        return self.title

class VideoStream(models.Model):
    QUALITY_CHOICES = (
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

    def __str__(self):
        return f"{self.video.title} - {self.quality}"

class Comment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='video_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.video.title}"

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    studio = models.ForeignKey('studio.StudioProfile', on_delete=models.CASCADE, related_name='categories')
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
        unique_together = ['name', 'studio']

    def __str__(self):
        return self.name

class Playlist(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    studio = models.ForeignKey('studio.StudioProfile', on_delete=models.CASCADE, related_name='playlists')
    videos = models.ManyToManyField(Video, through='PlaylistVideo', related_name='playlists')
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['name', 'studio']

    def __str__(self):
        return self.name

class PlaylistVideo(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'added_at']
        unique_together = ['playlist', 'video']

    def __str__(self):
        return f"{self.playlist.name} - {self.video.title}"
