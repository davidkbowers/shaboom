# Video Upload and Processing Flow

## 1. Upload Initiation
- **Endpoint**: `/videos/upload/` (handled by `upload_video` view)
- **Authentication**: User must be logged in
- **Process**:
  1. User submits a video file through a form
  2. System renames the file with a timestamp
  3. Video metadata is saved to a JSON file in `settings.PROCESS_DIR`
  4. A new `Video` record is created with `processing_status='pending'`
  5. The `process_video` Celery task is triggered asynchronously with the video ID

## 2. Video Processing (Celery Task: `process_video`)
- **Triggered**: Automatically after video upload
- **Steps**:
  1. Updates video status to `'processing'`
  2. Creates necessary directories for processed files
  3. **Format Conversion**:
     - Checks video format using `ffprobe`
     - If not MP4 with H.264, converts it using `ffmpeg`
  4. **Compression**:
     - Analyzes video resolution
     - Applies appropriate bitrate based on resolution
     - Creates a compressed version of the video
  5. **Multi-quality Streams**:
     - Generates 5 different quality versions (240p to 1080p)
     - Each version is stored with appropriate bitrate
     - Creates `VideoStream` records for each quality
  6. **Thumbnail Extraction**:
     - Triggers `extract_thumbnails` task asynchronously
  7. **Completion**:
     - Updates video status to `'completed'`
     - Saves path to compressed file

## 3. Thumbnail Extraction (Celery Task: `extract_thumbnails`)
- **Triggered**: After successful video processing
- **Process**:
  1. If no timestamps provided, extracts 4 thumbnails at:
     - 0% (start)
     - 25% (first quarter)
     - 50% (middle)
     - 75% (three-quarters)
  2. Saves thumbnails in `MEDIA_ROOT/videos/thumbnails/`
  3. Selects the middle thumbnail as default
  4. Updates video record with all thumbnail paths

## 4. Video Streaming
- **Endpoint**: `/videos/stream/<int:video_id>/<quality>/`
- **Handled by**: `get_video_stream` view
- **Features**:
  - Supports byte-range requests for seeking
  - Serves appropriate quality based on request
  - Uses efficient file streaming

## 5. Components Involved
- **Models**:
  - `Video`: Main video model
  - `VideoStream`: Different quality versions
  - `Category`: Video categorization
  - `Playlist`: Video collections
  - `Comment`: User comments

## 6. Dependencies
- **FFmpeg**: For video processing
- **Celery**: For background task processing
- **Redis**: As Celery's message broker and result backend

## 7. Storage Structure
```
MEDIA_ROOT/
  videos/
    original/       # Original uploaded videos
    processed/      # Converted MP4 versions
    compressed/     # Compressed versions
    streams/        # Different quality streams
    thumbnails/     # Extracted thumbnails
```

## 8. Error Handling
- Failed processing updates video status to `'failed'`
- Exceptions are caught and logged
- Original files are preserved in case of failure
