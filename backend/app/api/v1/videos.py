from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from app.config.database import get_db
from app.services.video_service import VideoService
from app.services.storage_service import StorageService
from app.models.video import ProcessedVideo
from app.schemas.video import VideoResponse, VideoList, TrimRequest, TrimRequestByPath, QualityRequest, QualityRequestByPath, ProcessedVideoResponse
from app.schemas.job import JobResponse
from app.tasks.video_tasks import process_video_upload, process_video_trim, process_quality_generation

router = APIRouter()


@router.post("/upload", response_model=JobResponse)
async def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a video file (Level 1)"""
    try:
        # Validate file
        storage = StorageService()
        if not storage.validate_file(file.filename, file.size):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type or size too large"
            )
        
        # Save file
        file_content = await file.read()
        file_path = storage.save_uploaded_file(file_content, file.filename)
        
        # Create video record
        video_service = VideoService(db)
        video = video_service.create_video(file_path, file.filename)
        
        # Create upload job
        from app.models.job import Job
        job = Job(
            video_id=video.id,
            job_type="upload",
            parameters={"filename": file.filename}
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Start background task
        process_video_upload.delay(str(video.id))
        
        return JobResponse.from_orm(job)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=VideoList)
async def list_videos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List uploaded videos (Level 1)"""
    try:
        video_service = VideoService(db)
        videos = video_service.list_videos(skip=skip, limit=limit)
        from app.models.video import Video
        total = db.query(Video).count()
        
        return VideoList(
            videos=[VideoResponse.from_orm(video) for video in videos],
            total=total,
            page=skip // limit + 1,
            size=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get video details"""
    try:
        video_service = VideoService(db)
        video = video_service.get_video(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return VideoResponse.from_orm(video)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{video_id}")
async def delete_video(
    video_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Delete a video"""
    try:
        video_service = VideoService(db)
        success = video_service.delete_video(video_id)
        if not success:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return {"message": "Video deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trim", response_model=JobResponse)
async def trim_video(
    request: TrimRequest,
    db: Session = Depends(get_db)
):
    """Trim a video (Level 2) - Exact endpoint from requirements"""
    try:
        video_service = VideoService(db)
        job = video_service.trim_video(
            request.video_id, 
            request.start_time, 
            request.end_time
        )
        
        # Start background task
        process_video_trim.delay(str(job.id))
        
        return JobResponse.from_orm(job)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{video_id}/trim", response_model=JobResponse)
async def trim_video_by_id(
    video_id: uuid.UUID,
    request: TrimRequestByPath,
    db: Session = Depends(get_db)
):
    """Alternative trim endpoint"""
    # Create a TrimRequest with the video_id from the URL path
    trim_request = TrimRequest(
        video_id=video_id,
        start_time=request.start_time,
        end_time=request.end_time
    )
    return await trim_video(trim_request, db)


@router.post("/{video_id}/qualities", response_model=JobResponse)
async def generate_qualities(
    video_id: uuid.UUID,
    request: QualityRequestByPath,
    db: Session = Depends(get_db)
):
    """Generate multiple quality versions (Level 5)"""
    try:
        video_service = VideoService(db)
        job = video_service.generate_qualities(video_id, request.qualities)
        
        # Start background task
        process_quality_generation.delay(str(job.id))
        
        return JobResponse.from_orm(job)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}/download")
async def download_video(
    video_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Download original video"""
    try:
        video_service = VideoService(db)
        video = video_service.get_video(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            video.file_path,
            filename=video.original_filename,
            media_type="video/mp4"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}/download/{quality}")
async def download_quality(
    video_id: uuid.UUID,
    quality: str,
    db: Session = Depends(get_db)
):
    """Download specific quality version"""
    try:
        video_service = VideoService(db)
        video_quality = video_service.get_video_quality(video_id, quality)
        if not video_quality:
            raise HTTPException(status_code=404, detail="Quality version not found")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            video_quality.file_path,
            filename=f"{video_id}_{quality}.mp4",
            media_type="video/mp4"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}/thumbnail")
async def get_thumbnail(
    video_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get video thumbnail"""
    try:
        video_service = VideoService(db)
        video = video_service.get_video(video_id)
        if not video or not video.thumbnail_path:
            raise HTTPException(status_code=404, detail="Thumbnail not found")
        
        from fastapi.responses import FileResponse
        return FileResponse(video.thumbnail_path, media_type="image/jpeg")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}/processed", response_model=List[ProcessedVideoResponse])
async def list_processed_videos(
    video_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """List all processed versions of a video"""
    try:
        processed_videos = db.query(ProcessedVideo).filter(
            ProcessedVideo.original_video_id == video_id
        ).all()
        
        return processed_videos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processed/{processed_video_id}/download")
async def download_processed_video(
    processed_video_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Download a processed video by its unique ID"""
    try:
        processed_video = db.query(ProcessedVideo).filter(
            ProcessedVideo.id == processed_video_id
        ).first()
        
        if not processed_video:
            raise HTTPException(status_code=404, detail="Processed video not found")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            processed_video.file_path,
            filename=processed_video.filename,
            media_type="video/mp4"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processed/{processed_video_id}", response_model=ProcessedVideoResponse)
async def get_processed_video(
    processed_video_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get processed video details by its unique ID"""
    try:
        processed_video = db.query(ProcessedVideo).filter(
            ProcessedVideo.id == processed_video_id
        ).first()
        
        if not processed_video:
            raise HTTPException(status_code=404, detail="Processed video not found")
        
        return processed_video
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
