from celery import shared_task
import subprocess
import os
from django.conf import settings
from .models import Video, VideoStream

@shared_task
def process_video(video_id):
    video = Video.objects.get(id=video_id)
    video.processing_status = 'processing'
    video.save()
    
    try:
        # Create compressed version
        input_path = video.file.path
        compressed_path = os.path.join(settings.MEDIA_ROOT, f'videos/compressed/{video_id}.mp4')
        os.makedirs(os.path.dirname(compressed_path), exist_ok=True)
        
        # Compress video using FFmpeg
        subprocess.run([
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx264', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            compressed_path
        ], check=True)
        
        # Create different quality streams
        qualities = {
            '240p': {'size': '426x240', 'bitrate': '500k'},
            '360p': {'size': '640x360', 'bitrate': '800k'},
            '480p': {'size': '854x480', 'bitrate': '1500k'},
            '720p': {'size': '1280x720', 'bitrate': '2500k'},
            '1080p': {'size': '1920x1080', 'bitrate': '4000k'},
        }
        
        for quality, specs in qualities.items():
            output_path = os.path.join(settings.MEDIA_ROOT, f'videos/streams/{video_id}_{quality}.mp4')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            subprocess.run([
                'ffmpeg', '-i', compressed_path,
                '-vf', f'scale={specs["size"]}',
                '-c:v', 'libx264', '-b:v', specs['bitrate'],
                '-c:a', 'aac', '-b:a', '128k',
                output_path
            ], check=True)
            
            # Create VideoStream object
            stream = VideoStream.objects.create(
                video=video,
                quality=quality,
                file=f'videos/streams/{video_id}_{quality}.mp4',
                bitrate=int(specs['bitrate'][:-1])  # Remove 'k' and convert to int
            )
        
        # Create thumbnail
        thumbnail_path = os.path.join(settings.MEDIA_ROOT, f'videos/thumbnails/{video_id}.jpg')
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
        
        subprocess.run([
            'ffmpeg', '-i', compressed_path,
            '-ss', '00:00:01',
            '-vframes', '1',
            thumbnail_path
        ], check=True)
        
        # Update video object
        video.compressed_file = f'videos/compressed/{video_id}.mp4'
        video.thumbnail = f'videos/thumbnails/{video_id}.jpg'
        video.processing_status = 'completed'
        video.save()
        
    except Exception as e:
        video.processing_status = 'failed'
        video.save()
        raise e
