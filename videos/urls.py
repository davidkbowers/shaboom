from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'videos'

urlpatterns = [
    path('upload/', views.upload_video, name='upload_video'),
    path('list/', views.video_list, name='video_list'),
    path('<int:video_id>/', views.video_detail, name='video_detail'),
    path('<int:video_id>/stream/<str:quality>/', views.get_video_stream, name='video_stream'),
    path('<int:video_id>/comment/', views.add_comment, name='add_comment'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:category_id>/', views.category_detail, name='category_detail'),
    
    # Playlist URLs
    path('playlists/', views.playlist_list, name='playlist_list'),
    path('playlists/<int:playlist_id>/', views.playlist_detail, name='playlist_detail'),
    path('playlists/<int:playlist_id>/reorder/', views.playlist_video_reorder, name='playlist_video_reorder'),
    path('playlists/<int:playlist_id>/remove/<int:video_id>/', views.playlist_video_remove, name='playlist_video_remove'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
