from celery import shared_task
import subprocess
import os
import json
from django.conf import settings
from .models import Video, VideoStream

def get_video_format(file_path):
    """Get the container format of the video file."""
    result = subprocess.check_output([
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=codec_name',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        file_path
    ]).decode().strip()
    return result

@shared_task
def process_video(video_id):
    video = Video.objects.get(id=video_id)
    video.processing_status = 'processing'
    video.save()
    
    try:
        input_path = video.file.path
        base_path = os.path.join(settings.MEDIA_ROOT, f'videos/processed/{video_id}')
        os.makedirs(os.path.dirname(base_path), exist_ok=True)
        
        # First, convert to MP4 if needed
        input_format = get_video_format(input_path)
        mp4_path = f'{base_path}_converted.mp4'
        
        # Convert to MP4 with H.264 codec if not already in correct format
        if input_format != 'h264' or not input_path.lower().endswith('.mp4'):
            subprocess.run([
                'ffmpeg', '-i', input_path,
                '-c:v', 'libx264',     # Video codec
                '-c:a', 'aac',         # Audio codec
                '-movflags', '+faststart',  # Enable fast start for web playback
                '-preset', 'medium',    # Encoding preset (balance between speed and quality)
                '-crf', '23',          # Quality setting (lower = better quality, 23 is default)
                mp4_path
            ], check=True)
        else:
            # If already MP4 with H.264, just copy
            mp4_path = input_path

        # Create compressed version
        compressed_path = os.path.join(settings.MEDIA_ROOT, f'videos/compressed/{video_id}.mp4')
        os.makedirs(os.path.dirname(compressed_path), exist_ok=True)
        
        # Compress video using FFmpeg with adaptive bitrate based on resolution
        probe = subprocess.check_output([
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'json',
            mp4_path
        ]).decode()
        
        video_info = json.loads(probe)
        width = int(video_info['streams'][0]['width'])
        height = int(video_info['streams'][0]['height'])
        
        # Calculate target bitrate based on resolution
        # This is a simple heuristic - you might want to adjust these values
        pixels = width * height
        if pixels > 2073600:  # 1080p
            target_bitrate = '4M'
        elif pixels > 921600:  # 720p
            target_bitrate = '2.5M'
        elif pixels > 409920:  # 480p
            target_bitrate = '1.5M'
        else:
            target_bitrate = '1M'
        
        subprocess.run([
            'ffmpeg', '-i', mp4_path,
            '-c:v', 'libx264',
            '-b:v', target_bitrate,
            '-c:a', 'aac',
            '-b:a', '128k',
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
        
        # Extract thumbnails as a separate task
        extract_thumbnails.delay(video_id, compressed_path)
        
        # Update video object
        video.compressed_file = f'videos/compressed/{video_id}.mp4'
        video.processing_status = 'completed'
        video.save()
        
    except Exception as e:
        video.processing_status = 'failed'
        video.save()
        raise e

@shared_task
def extract_thumbnails(video_id, video_path, timestamps=None):
    """
    Extract multiple thumbnails from a video at specified timestamps.
    If no timestamps are provided, extracts thumbnails at 0%, 25%, 50%, and 75% of the video duration.
    """
    video = Video.objects.get(id=video_id)
    try:
        # Get video duration if timestamps not provided
        if not timestamps:
            duration_output = subprocess.check_output([
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', video_path
            ]).decode().strip()
            duration = float(duration_output)
            timestamps = [
                max(0, duration * 0.0),  # Start
                max(0, duration * 0.25),  # Quarter
                max(0, duration * 0.5),   # Middle
                max(0, duration * 0.75),  # Three-quarters
            ]

        thumbnails = []
        for i, timestamp in enumerate(timestamps):
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, f'videos/thumbnails/{video_id}_{i}.jpg')
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            
            subprocess.run([
                'ffmpeg', '-i', video_path,
                '-ss', str(timestamp),
                '-vframes', '1',
                '-vf', 'scale=320:-1',  # Scale width to 320px, maintain aspect ratio
                thumbnail_path
            ], check=True)
            thumbnails.append(f'videos/thumbnails/{video_id}_{i}.jpg')

        # Select the middle thumbnail as default for now
        # TODO: Implement thumbnail selection based on image quality metrics
        default_thumbnail = thumbnails[len(thumbnails)//2]
        
        # Update video object with all thumbnails
        video.thumbnail = default_thumbnail
        video.all_thumbnails = thumbnails
        video.save()
        
        return thumbnails
        
    except Exception as e:
        video.processing_status = 'failed'
        video.save()
        raise e
