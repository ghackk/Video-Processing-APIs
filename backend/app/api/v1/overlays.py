from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import uuid
from app.config.database import get_db
from app.models.job import Job
from app.schemas.job import JobResponse
from app.schemas.overlay import OverlayCreate, OverlayResponse, WatermarkRequest
from app.tasks.video_tasks import process_overlay, process_watermark

router = APIRouter()


@router.post("/text", response_model=JobResponse)
async def add_text_overlay(
    request: OverlayCreate,
    db: Session = Depends(get_db)
):
    """Add text overlay to video (Level 3)"""
    try:
        if request.overlay_type != "text":
            raise HTTPException(status_code=400, detail="Overlay type must be 'text'")
        
        if not request.content:
            raise HTTPException(status_code=400, detail="Text content is required")
        
        # Create job
        job = Job(
            video_id=request.video_id,
            job_type="overlay",
            parameters={
                "overlay_type": "text",
                "text": request.content,
                "position_x": request.position_x or 10,
                "position_y": request.position_y or 10,
                "font_size": request.font_size or 24,
                "font_color": request.font_color or "white",
                "language": request.language or "en"
            }
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Start background task
        process_overlay.delay(str(job.id))
        
        return JobResponse.from_orm(job)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image", response_model=JobResponse)
async def add_image_overlay(
    request: OverlayCreate,
    overlay_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Add image overlay to video (Level 3)"""
    try:
        if request.overlay_type != "image":
            raise HTTPException(status_code=400, detail="Overlay type must be 'image'")
        
        # Save overlay file
        from app.services.storage_service import StorageService
        storage = StorageService()
        
        file_content = await overlay_file.read()
        overlay_path = storage.save_uploaded_file(file_content, overlay_file.filename)
        
        # Create job
        job = Job(
            video_id=request.video_id,
            job_type="overlay",
            parameters={
                "overlay_type": "image",
                "overlay_path": overlay_path,
                "position_x": request.position_x or 10,
                "position_y": request.position_y or 10,
                "width": request.width,
                "height": request.height
            }
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Start background task
        process_overlay.delay(str(job.id))
        
        return JobResponse.from_orm(job)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video", response_model=JobResponse)
async def add_video_overlay(
    request: OverlayCreate,
    overlay_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Add video overlay to video (Level 3)"""
    try:
        if request.overlay_type != "video":
            raise HTTPException(status_code=400, detail="Overlay type must be 'video'")
        
        # Save overlay file
        from app.services.storage_service import StorageService
        storage = StorageService()
        
        file_content = await overlay_file.read()
        overlay_path = storage.save_uploaded_file(file_content, overlay_file.filename)
        
        # Create job
        job = Job(
            video_id=request.video_id,
            job_type="overlay",
            parameters={
                "overlay_type": "video",
                "overlay_path": overlay_path,
                "position_x": request.position_x or 10,
                "position_y": request.position_y or 10,
                "width": request.width,
                "height": request.height
            }
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Start background task
        process_overlay.delay(str(job.id))
        
        return JobResponse.from_orm(job)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/watermark", response_model=JobResponse)
async def add_watermark(
    request: WatermarkRequest,
    watermark_file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Add watermark to video (Level 3)"""
    try:
        parameters = {
            "watermark_type": request.watermark_type,
            "position": request.position,
            "opacity": request.opacity,
            "size": request.size
        }
        
        if request.watermark_type == "image":
            if not watermark_file:
                raise HTTPException(status_code=400, detail="Watermark file is required for image watermark")
            
            # Save watermark file
            from app.services.storage_service import StorageService
            storage = StorageService()
            
            file_content = await watermark_file.read()
            watermark_path = storage.save_uploaded_file(file_content, watermark_file.filename)
            parameters["watermark_path"] = watermark_path
            
        elif request.watermark_type == "text":
            if not request.content:
                raise HTTPException(status_code=400, detail="Text content is required for text watermark")
            parameters["text"] = request.content
        
        # Create job
        job = Job(
            video_id=request.video_id,
            job_type="watermark",
            parameters=parameters
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Start background task
        process_watermark.delay(str(job.id))
        
        return JobResponse.from_orm(job)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}", response_model=List[OverlayResponse])
async def list_overlays(
    video_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """List all overlays for a video"""
    try:
        from app.models.overlay import Overlay
        overlays = db.query(Overlay).filter(Overlay.video_id == video_id).all()
        return [OverlayResponse.from_orm(overlay) for overlay in overlays]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
