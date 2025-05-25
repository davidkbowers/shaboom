from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, StreamingHttpResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import Video, VideoStream, Comment, Category, Playlist, PlaylistVideo
from .forms import VideoUploadForm, CommentForm, CategoryForm, PlaylistForm, PlaylistVideoForm
from studio.models import StudioProfile, StudioMembership
from datetime import datetime
import os
import json
import subprocess
from moviepy import *
import mimetypes
import re
import shutil

range_re = re.compile(r'bytes=(\d+)-(\d+)?')

@login_required
def upload_video(request):
    studio_profile = get_object_or_404(StudioProfile, owner=request.user)
    
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES, studio=studio_profile)
        if form.is_valid():
            try:
                #rename video file
                timestamp_str = datetime.now().isoformat()
                original_name, extension = os.path.splitext(request.FILES['file'].name)
                new_video_file = f"{timestamp_str}{extension}"

                #create json processing data
                processing_data = {
                    "uploaded_by": request.user.id,
                    "title": form.cleaned_data['title'],
                    "description": form.cleaned_data['description'],
                    "file": new_video_file,
                    "category_id": form.cleaned_data['category'].id if form.cleaned_data['category'] else None,
                }

                # Save processing data to json file
                json_filename = f"{timestamp_str}.json"
                json_filepath = os.path.join(settings.PROCESS_DIR, json_filename)
                print("settings.PROCESS_DIR: ", settings.PROCESS_DIR)
                print("json_filepath: ", json_filepath)

                with open(json_filepath, 'w') as f:
                    json.dump(processing_data, f)

                #copy video file to processing directory
                uploaded_file = request.FILES['file']
                process_filepath = os.path.join(settings.PROCESS_DIR, new_video_file)
                print(process_filepath)

                # Ensure the processing directory exists
                os.makedirs(settings.PROCESS_DIR, exist_ok=True)
                
                # Save the uploaded file to processing directory
                with open(process_filepath, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                # Create and save the video object
                video = form.save(commit=False)
                video.uploaded_by = request.user
                video.processing_status = 'pending'
                video.save()  # Save the video to get an ID

                # Now we can render with a valid video ID
                messages.success(request, 'Video uploaded successfully! Please wait for processing.')
                form = VideoUploadForm(studio=studio_profile)
                return render(request, 'videos/upload.html', {'form': form, 'show_success': True})
            except Exception as e:
                messages.error(request, f"Error uploading video: {str(e)}")
                return render(request, 'videos/upload.html', {'form': form, 'show_error': True})
        else:
            form.add_error(None, f"Error uploading video: {str(form.errors)}")
    else:
        form = VideoUploadForm(studio=studio_profile)
    return render(request, 'videos/upload.html', {'form': form})

#@login_required
#def video_list(request):
#    videos = Video.objects.filter(processing_status='completed').order_by('-created_at')
#    template_name = 'videos/test_list.html' if 'test' in request.GET else 'videos/list.html'
#    return render(request, template_name, {'videos': videos})

@login_required
def video_list(request):
    videos = Video.objects.filter(uploaded_by=request.user).order_by('-created_at')
    return render(request, 'videos/video_list.html', {'videos': videos})

@login_required
def student_video_list(request):
    # Get the studio profile from the user's membership
    studio_membership = get_object_or_404(StudioMembership, member=request.user, is_active=True)
    studio_profile = studio_membership.studio
    
    # Get all public videos from the studio
    videos = Video.objects.filter(
        category__studio=studio_profile,
        category__is_public=True
    ).order_by('-created_at')
    
    # Group videos by category
    categories = Category.objects.filter(
        studio=studio_profile,
        is_public=True
    ).prefetch_related('videos')
    
    return render(request, 'videos/student_video_list.html', {
        'categories': categories,
        'videos': videos,
        'studio': studio_profile
    })

@login_required
def studio_video_list(request, studio_id):
    studio = get_object_or_404(StudioProfile, id=studio_id)
    
    # Check if the user is a student of this studio
    is_student = StudioMembership.objects.filter(
        user=request.user,
        studio=studio,
        role='student'
    ).exists()
    
    if not is_student:
        return redirect('home')  # Or to a custom permission denied page
    
    # Get all categories and their videos for this studio
    categories = Category.objects.filter(
        studio=studio,
        is_public=True
    ).prefetch_related('videos')
    
    context = {
        'studio': studio,
        'categories': categories,
    }
    
    return render(request, 'videos/studio_video_list.html', context)

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
    
    # Get all available streams for the video
    streams = video.streams.all()
    
    # Get the 720p stream if available, otherwise use the original file
    source = None
    if streams.exists():
        # Prefer 720p if available, otherwise take the first available stream
        stream = streams.filter(quality='720p').first() or streams.first()
        if stream:
            source = stream.file.url
    
    if not source and video.file:
        source = video.file.url
    
    comments = video.comments.select_related('user').all()
    comment_form = CommentForm()
    
    return render(request, 'videos/detail.html', {
        'video': video,
        'source': source,
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
