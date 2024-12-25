from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, StreamingHttpResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.views.decorators.http import require_http_methods
from .models import Video, VideoStream
from .forms import VideoUploadForm
import os
import subprocess
from moviepy import *
import mimetypes
import re

range_re = re.compile(r'bytes=(\d+)-(\d+)?')

@login_required
def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.uploaded_by = request.user
            video.save()
            
            # Get video duration and size
            with VideoFileClip(video.file.path) as clip:
                video.duration = clip.duration
                video.size = os.path.getsize(video.file.path)
                video.save()
            
            # Trigger async video processing (compression and streaming)
            process_video.delay(video.id)
            
            return redirect('video_detail', video_id=video.id)
    else:
        form = VideoUploadForm()
    
    return render(request, 'videos/upload.html', {'form': form})

@login_required
def video_list(request):
    videos = Video.objects.filter(processing_status='completed').order_by('-created_at')
    return render(request, 'videos/list.html', {'videos': videos})

def video_detail(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    streams = video.streams.all()
    return render(request, 'videos/detail.html', {
        'video': video,
        'streams': streams
    })

def get_video_stream(request, video_id, quality):
    video = get_object_or_404(Video, id=video_id)
    stream = get_object_or_404(VideoStream, video=video, quality=quality)
    
    path = stream.file.path
    size = os.path.getsize(path)
    
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = range_re.match(range_header)
    
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = int(last_byte) if last_byte else size - 1
        length = last_byte - first_byte + 1
        
        resp = StreamingHttpResponse(
            file_iterator(path, chunk_size=8192, start=first_byte, length=length),
            status=206,
            content_type='video/mp4'
        )
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = f'bytes {first_byte}-{last_byte}/{size}'
    else:
        resp = StreamingHttpResponse(
            file_iterator(path),
            content_type='video/mp4'
        )
        resp['Content-Length'] = str(size)
    
    resp['Accept-Ranges'] = 'bytes'
    return resp

def file_iterator(path, chunk_size=8192, start=0, length=None):
    with open(path, 'rb') as f:
        f.seek(start)
        remaining = length
        while True:
            bytes_length = chunk_size if remaining is None else min(remaining, chunk_size)
            data = f.read(bytes_length)
            if not data:
                break
            if remaining:
                remaining -= len(data)
            yield data
