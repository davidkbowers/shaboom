from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, StreamingHttpResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.views.decorators.http import require_http_methods
from .models import Video, VideoStream, Comment, Category, Playlist, PlaylistVideo
from .forms import VideoUploadForm, CommentForm, CategoryForm, PlaylistForm, PlaylistVideoForm
from accounts.models import StudioProfile
import os
import subprocess
from moviepy import *
import mimetypes
import re

range_re = re.compile(r'bytes=(\d+)-(\d+)?')

@login_required
def upload_video(request):
    studio_profile = get_object_or_404(StudioProfile, owner=request.user)
    
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES, studio=studio_profile)
        if form.is_valid():
            try:
                video = form.save(commit=False)
                video.uploaded_by = request.user
                video.save()
                
                # Skip video processing in test mode
                if 'test' not in request.GET:
                    try:
                        # Get video duration and size
                        with VideoFileClip(video.file.path) as clip:
                            video.duration = clip.duration
                            video.size = os.path.getsize(video.file.path)
                            video.save()
                        
                        # Trigger async video processing (compression and streaming)
                        process_video.delay(video.id)
                    except Exception as e:
                        # If video processing fails, log the error but don't delete the video
                        print(f"Error processing video: {str(e)}")
                        video.processing_status = 'failed'
                        video.save()
                
                return redirect('videos:video_detail', video_id=video.id)
            except Exception as e:
                form.add_error(None, f"Error uploading video: {str(e)}")
    else:
        form = VideoUploadForm(studio=studio_profile)
    
    return render(request, 'videos/upload.html', {'form': form})

@login_required
def video_list(request):
    videos = Video.objects.filter(processing_status='completed').order_by('-created_at')
    template_name = 'videos/test_list.html' if 'test' in request.GET else 'videos/list.html'
    return render(request, template_name, {'videos': videos})

@login_required
def video_list(request):
    videos = Video.objects.filter(uploaded_by=request.user).order_by('-created_at')
    return render(request, 'videos/video_list.html', {'videos': videos})

@login_required
def category_list(request):
    studio_profile = get_object_or_404(StudioProfile, owner=request.user)
    categories = Category.objects.filter(studio=studio_profile)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.studio = studio_profile
            category.save()
            return redirect('videos:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'videos/category_list.html', {
        'categories': categories,
        'form': form
    })

@login_required
def category_detail(request, category_id):
    studio_profile = get_object_or_404(StudioProfile, owner=request.user)
    category = get_object_or_404(Category, id=category_id, studio=studio_profile)
    videos = Video.objects.filter(category=category).order_by('-created_at')
    
    return render(request, 'videos/category_detail.html', {
        'category': category,
        'videos': videos
    })

@login_required
def playlist_list(request):
    studio_profile = get_object_or_404(StudioProfile, owner=request.user)
    playlists = Playlist.objects.filter(studio=studio_profile)
    
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.studio = studio_profile
            playlist.save()
            return redirect('videos:playlist_list')
    else:
        form = PlaylistForm()
    
    return render(request, 'videos/playlist_list.html', {
        'playlists': playlists,
        'form': form
    })

@login_required
def playlist_detail(request, playlist_id):
    studio_profile = get_object_or_404(StudioProfile, owner=request.user)
    playlist = get_object_or_404(Playlist, id=playlist_id, studio=studio_profile)
    playlist_videos = playlist.playlistvideo_set.select_related('video').order_by('order')
    available_videos = Video.objects.filter(uploaded_by=request.user).exclude(playlists=playlist)
    
    if request.method == 'POST':
        form = PlaylistVideoForm(request.POST)
        if form.is_valid():
            playlist_video = form.save(commit=False)
            playlist_video.playlist = playlist
            playlist_video.save()
            return redirect('videos:playlist_detail', playlist_id=playlist.id)
    else:
        form = PlaylistVideoForm()
        form.fields['video'].queryset = available_videos
    
    return render(request, 'videos/playlist_detail.html', {
        'playlist': playlist,
        'playlist_videos': playlist_videos,
        'form': form
    })

@login_required
@require_http_methods(['POST'])
def playlist_video_reorder(request, playlist_id):
    studio_profile = get_object_or_404(StudioProfile, owner=request.user)
    playlist = get_object_or_404(Playlist, id=playlist_id, studio=studio_profile)
    
    video_orders = request.POST.getlist('video_order[]')
    for index, video_id in enumerate(video_orders):
        PlaylistVideo.objects.filter(
            playlist=playlist,
            video_id=video_id
        ).update(order=index)
    
    return JsonResponse({'status': 'success'})

@login_required
@require_http_methods(['POST'])
def playlist_video_remove(request, playlist_id, video_id):
    studio_profile = get_object_or_404(StudioProfile, owner=request.user)
    playlist = get_object_or_404(Playlist, id=playlist_id, studio=studio_profile)
    
    PlaylistVideo.objects.filter(
        playlist=playlist,
        video_id=video_id
    ).delete()
    
    return JsonResponse({'status': 'success'})

def video_detail(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    streams = video.streams.all()
    comments = video.comments.select_related('user').all()
    comment_form = CommentForm()
    return render(request, 'videos/detail.html', {
        'video': video,
        'streams': streams,
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
@require_http_methods(["POST"])
def add_comment(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.video = video
        comment.user = request.user
        comment.save()
        return redirect('videos:video_detail', video_id=video_id)
    
    # If form is invalid, return to video detail with error
    streams = video.streams.all()
    comments = video.comments.select_related('user').all()
    return render(request, 'videos/detail.html', {
        'video': video,
        'streams': streams,
        'comments': comments,
        'comment_form': form
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
