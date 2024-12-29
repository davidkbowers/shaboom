from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'videos'

urlpatterns = [
    path('upload/', views.upload_video, name='upload_video'),
    path('', views.video_list, name='video_list'),
    path('<int:video_id>/', views.video_detail, name='video_detail'),
    path('<int:video_id>/stream/<str:quality>/', views.get_video_stream, name='video_stream'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
