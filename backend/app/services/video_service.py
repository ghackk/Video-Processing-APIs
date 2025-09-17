from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import os
from pathlib import Path
from app.models.video import Video, VideoQuality
from app.models.job import Job
from app.schemas.video import VideoCreate, TrimRequest, QualityRequest
from app.services.ffmpeg_service import FFmpegService
from app.services.storage_service import StorageService
from app.config.settings import settings


class VideoService:
    """Service for video operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ffmpeg = FFmpegService()
        self.storage = StorageService()
    
    def create_video(self, file_path: str, original_filename: str) -> Video:
        """Create video record and extract metadata"""
        try:
            # Extract metadata using FFmpeg
            metadata = self.ffmpeg.get_video_metadata(file_path)
            
            # Generate thumbnail
            thumbnail_path = os.path.join(settings.processed_dir, f"thumb_{uuid.uuid4()}.jpg")
            self.ffmpeg.generate_thumbnail(file_path, thumbnail_path)
            
            # Create video record
            video = Video(
                filename=os.path.basename(file_path),
                original_filename=original_filename,
                file_path=file_path,
                file_size=metadata["size"],
                duration=metadata["duration"],
                format=metadata["format"],
                resolution=metadata["resolution"],
                fps=metadata["fps"],
                bitrate=metadata["bitrate"],
                thumbnail_path=thumbnail_path
            )
            
            self.db.add(video)
            self.db.commit()
            self.db.refresh(video)
            
            return video
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to create video: {str(e)}")
    
    def get_video(self, video_id: uuid.UUID) -> Optional[Video]:
        """Get video by ID"""
        return self.db.query(Video).filter(Video.id == video_id).first()
    
    def list_videos(self, skip: int = 0, limit: int = 100) -> List[Video]:
        """List videos with pagination"""
        return self.db.query(Video).offset(skip).limit(limit).all()
    
    def delete_video(self, video_id: uuid.UUID) -> bool:
        """Delete video and all associated files"""
        video = self.get_video(video_id)
        if not video:
            return False
        
        try:
            # Delete files
            if os.path.exists(video.file_path):
                os.remove(video.file_path)
            if video.thumbnail_path and os.path.exists(video.thumbnail_path):
                os.remove(video.thumbnail_path)
            
            # Delete quality versions
            for quality in video.qualities:
                if os.path.exists(quality.file_path):
                    os.remove(quality.file_path)
            
            # Delete from database
            self.db.delete(video)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to delete video: {str(e)}")
    
    def trim_video(self, video_id: uuid.UUID, start_time: float, end_time: float) -> Job:
        """Create trim job for video"""
        video = self.get_video(video_id)
        if not video:
            raise ValueError("Video not found")
        
        if start_time >= end_time:
            raise ValueError("Start time must be less than end time")
        
        if end_time > float(video.duration):
            raise ValueError("End time exceeds video duration")
        
        # Create job
        job = Job(
            video_id=video_id,
            job_type="trim",
            parameters={
                "start_time": start_time,
                "end_time": end_time
            }
        )
        
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        return job
    
    def generate_qualities(self, video_id: uuid.UUID, qualities: List[str]) -> Job:
        """Create quality generation job"""
        video = self.get_video(video_id)
        if not video:
            raise ValueError("Video not found")
        
        # Create job
        job = Job(
            video_id=video_id,
            job_type="quality",
            parameters={
                "qualities": qualities
            }
        )
        
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        return job
    
    def get_video_qualities(self, video_id: uuid.UUID) -> List[VideoQuality]:
        """Get all quality versions for a video"""
        return self.db.query(VideoQuality).filter(VideoQuality.video_id == video_id).all()
    
    def get_video_quality(self, video_id: uuid.UUID, quality: str) -> Optional[VideoQuality]:
        """Get specific quality version"""
        return self.db.query(VideoQuality).filter(
            VideoQuality.video_id == video_id,
            VideoQuality.quality == quality
        ).first()
