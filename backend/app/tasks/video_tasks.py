from celery import current_task
from sqlalchemy.orm import sessionmaker
from app.config.database import engine
from app.config.celery_config import celery_app
from app.models.video import Video, VideoQuality
from app.models.job import Job
from app.services.ffmpeg_service import FFmpegService
from app.services.storage_service import StorageService
from app.config.settings import settings
import uuid
import os


# Create database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@celery_app.task(bind=True)
def process_video_upload(self, video_id: str):
    """Process video upload - extract metadata and generate thumbnail"""
    db = next(get_db())
    
    try:
        # Update job status
        job = db.query(Job).filter(Job.id == self.request.id).first()
        if job:
            job.status = "processing"
            job.started_at = db.query(Job).filter(Job.id == self.request.id).first().created_at
            db.commit()
        
        # Get video
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError("Video not found")
        
        # Update progress
        current_task.update_state(state="PROGRESS", meta={"progress": 50})
        
        # Process video (metadata already extracted during upload)
        # Generate thumbnail if not exists
        if not video.thumbnail_path:
            ffmpeg = FFmpegService()
            thumbnail_path = os.path.join(settings.processed_dir, f"thumb_{video_id}.jpg")
            ffmpeg.generate_thumbnail(video.file_path, thumbnail_path)
            video.thumbnail_path = thumbnail_path
            db.commit()
        
        # Update job status
        if job:
            job.status = "completed"
            job.progress = 100
            job.completed_at = db.query(Job).filter(Job.id == self.request.id).first().created_at
            db.commit()
        
        return {"status": "completed", "video_id": video_id}
        
    except Exception as e:
        # Update job status
        if job:
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
        
        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True)
def process_video_trim(self, job_id: str):
    """Process video trimming"""
    db = next(get_db())
    
    try:
        # Get job
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError("Job not found")
        
        # Update job status
        job.status = "processing"
        job.started_at = db.query(Job).filter(Job.id == job_id).first().created_at
        db.commit()
        
        # Get video
        video = db.query(Video).filter(Video.id == job.video_id).first()
        if not video:
            raise ValueError("Video not found")
        
        # Get parameters
        start_time = job.parameters["start_time"]
        end_time = job.parameters["end_time"]
        
        # Update progress
        current_task.update_state(state="PROGRESS", meta={"progress": 30})
        
        # Process trimming
        ffmpeg = FFmpegService()
        storage = StorageService()
        
        output_filename = f"trimmed_{video_id}_{start_time}_{end_time}.mp4"
        output_path = storage.create_processed_file_path(output_filename)
        
        ffmpeg.trim_video(video.file_path, output_path, start_time, end_time)
        
        # Update progress
        current_task.update_state(state="PROGRESS", meta={"progress": 80})
        
        # Update job
        job.status = "completed"
        job.progress = 100
        job.result_path = output_path
        job.completed_at = db.query(Job).filter(Job.id == job_id).first().created_at
        db.commit()
        
        return {"status": "completed", "result_path": output_path}
        
    except Exception as e:
        # Update job status
        if job:
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
        
        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True)
def process_quality_generation(self, job_id: str):
    """Process multiple quality generation"""
    db = next(get_db())
    
    try:
        # Get job
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError("Job not found")
        
        # Update job status
        job.status = "processing"
        job.started_at = db.query(Job).filter(Job.id == job_id).first().created_at
        db.commit()
        
        # Get video
        video = db.query(Video).filter(Video.id == job.video_id).first()
        if not video:
            raise ValueError("Video not found")
        
        # Get parameters
        qualities = job.parameters["qualities"]
        
        # Process quality generation
        ffmpeg = FFmpegService()
        storage = StorageService()
        
        results = ffmpeg.generate_quality_versions(
            video.file_path, 
            settings.processed_dir, 
            qualities
        )
        
        # Save quality records
        for quality, file_path in results.items():
            file_size = storage.get_file_size(file_path)
            
            quality_record = VideoQuality(
                video_id=video.id,
                quality=quality,
                file_path=file_path,
                file_size=file_size,
                resolution=quality.replace("p", ""),
                bitrate=1000 if quality == "480p" else 2500 if quality == "720p" else 5000
            )
            db.add(quality_record)
        
        # Update job
        job.status = "completed"
        job.progress = 100
        job.result_path = str(results)
        job.completed_at = db.query(Job).filter(Job.id == job_id).first().created_at
        db.commit()
        
        return {"status": "completed", "qualities": list(results.keys())}
        
    except Exception as e:
        # Update job status
        if job:
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
        
        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True)
def process_overlay(self, job_id: str):
    """Process overlay addition"""
    db = next(get_db())
    
    try:
        # Get job
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError("Job not found")
        
        # Update job status
        job.status = "processing"
        job.started_at = db.query(Job).filter(Job.id == job_id).first().created_at
        db.commit()
        
        # Get video
        video = db.query(Video).filter(Video.id == job.video_id).first()
        if not video:
            raise ValueError("Video not found")
        
        # Get parameters
        overlay_type = job.parameters["overlay_type"]
        
        # Process overlay
        ffmpeg = FFmpegService()
        storage = StorageService()
        
        output_filename = f"overlay_{video_id}_{overlay_type}.mp4"
        output_path = storage.create_processed_file_path(output_filename)
        
        if overlay_type == "text":
            text = job.parameters["text"]
            position = (job.parameters["position_x"], job.parameters["position_y"])
            font_size = job.parameters.get("font_size", 24)
            font_color = job.parameters.get("font_color", "white")
            language = job.parameters.get("language", "en")
            
            ffmpeg.add_text_overlay(
                video.file_path, output_path, text, position, 
                font_size, font_color, language
            )
        elif overlay_type == "image":
            overlay_path = job.parameters["overlay_path"]
            position = (job.parameters["position_x"], job.parameters["position_y"])
            size = (job.parameters.get("width"), job.parameters.get("height"))
            
            ffmpeg.add_image_overlay(
                video.file_path, output_path, overlay_path, position, size
            )
        
        # Update job
        job.status = "completed"
        job.progress = 100
        job.result_path = output_path
        job.completed_at = db.query(Job).filter(Job.id == job_id).first().created_at
        db.commit()
        
        return {"status": "completed", "result_path": output_path}
        
    except Exception as e:
        # Update job status
        if job:
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
        
        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True)
def process_watermark(self, job_id: str):
    """Process watermark addition"""
    db = next(get_db())
    
    try:
        # Get job
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError("Job not found")
        
        # Update job status
        job.status = "processing"
        job.started_at = db.query(Job).filter(Job.id == job_id).first().created_at
        db.commit()
        
        # Get video
        video = db.query(Video).filter(Video.id == job.video_id).first()
        if not video:
            raise ValueError("Video not found")
        
        # Get parameters
        watermark_type = job.parameters["watermark_type"]
        position = job.parameters.get("position", "bottom-right")
        opacity = job.parameters.get("opacity", 0.5)
        
        # Process watermark
        ffmpeg = FFmpegService()
        storage = StorageService()
        
        output_filename = f"watermarked_{video_id}.mp4"
        output_path = storage.create_processed_file_path(output_filename)
        
        if watermark_type == "image":
            watermark_path = job.parameters["watermark_path"]
            ffmpeg.add_watermark(video.file_path, output_path, watermark_path, position, opacity)
        elif watermark_type == "text":
            text = job.parameters["text"]
            # For text watermarks, we'll use the text overlay function
            ffmpeg.add_text_overlay(
                video.file_path, output_path, text, (10, 10), 16, "white@0.5"
            )
        
        # Update job
        job.status = "completed"
        job.progress = 100
        job.result_path = output_path
        job.completed_at = db.query(Job).filter(Job.id == job_id).first().created_at
        db.commit()
        
        return {"status": "completed", "result_path": output_path}
        
    except Exception as e:
        # Update job status
        if job:
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
        
        raise self.retry(exc=e, countdown=60, max_retries=3)
