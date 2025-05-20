from django.core.management.base import BaseCommand
from videos.models import Video
from videos.tasks import process_video

class Command(BaseCommand):
    help = 'Process all videos with pending status'

    def handle(self, *args, **options):
        pending_videos = Video.objects.filter(processing_status='pending')
        self.stdout.write(f'Found {pending_videos.count()} pending videos')
        
        for video in pending_videos:
            self.stdout.write(f'Processing video ID {video.id}: {video.title}')
            try:
                # Call the task directly (synchronously) for debugging
                process_video.delay(video.id)
                self.stdout.write(self.style.SUCCESS(f'Successfully queued video ID {video.id}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing video ID {video.id}: {str(e)}'))
