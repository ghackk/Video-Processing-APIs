from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
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
    overlay_file: UploadFile = File(...),
    video_id: str = Form(...),
    overlay_type: str = Form(default="image"),
    position_x: int = Form(default=10),
    position_y: int = Form(default=10),
    width: int = Form(default=None),
    height: int = Form(default=None),
    db: Session = Depends(get_db)
):
    """Add image overlay to video (Level 3)"""
    try:
        if overlay_type != "image":
            raise HTTPException(status_code=400, detail="Overlay type must be 'image'")
        
        # Convert video_id to UUID
        try:
            video_uuid = uuid.UUID(video_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid video_id format")
        
        # Save overlay file
        from app.services.storage_service import StorageService
        storage = StorageService()
        
        file_content = await overlay_file.read()
        overlay_path = storage.save_uploaded_file(file_content, overlay_file.filename)
        
        # Create job
        job = Job(
            video_id=video_uuid,
            job_type="overlay",
            parameters={
                "overlay_type": "image",
                "overlay_path": overlay_path,
                "position_x": position_x,
                "position_y": position_y,
                "width": width,
                "height": height
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
    overlay_file: UploadFile = File(...),
    video_id: str = Form(...),
    overlay_type: str = Form(default="video"),
    position_x: int = Form(default=10),
    position_y: int = Form(default=10),
    width: int = Form(default=None),
    height: int = Form(default=None),
    db: Session = Depends(get_db)
):
    """Add video overlay to video (Level 3)"""
    try:
        if overlay_type != "video":
            raise HTTPException(status_code=400, detail="Overlay type must be 'video'")
        
        # Convert video_id to UUID
        try:
            video_uuid = uuid.UUID(video_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid video_id format")
        
        # Save overlay file
        from app.services.storage_service import StorageService
        storage = StorageService()
        
        file_content = await overlay_file.read()
        overlay_path = storage.save_uploaded_file(file_content, overlay_file.filename)
        
        # Create job
        job = Job(
            video_id=video_uuid,
            job_type="overlay",
            parameters={
                "overlay_type": "video",
                "overlay_path": overlay_path,
                "position_x": position_x,
                "position_y": position_y,
                "width": width,
                "height": height
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
    video_id: str = Form(...),
    watermark_type: str = Form(...),
    position: str = Form("bottom-right"),
    opacity: float = Form(0.5),
    size: int = Form(100),
    content: Optional[str] = Form(None),
    watermark_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Add watermark to video (Level 3)"""
    try:
        # Validate video_id
        try:
            video_uuid = uuid.UUID(video_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid video_id format")
        
        # Validate watermark_type
        if watermark_type not in ["image", "text"]:
            raise HTTPException(status_code=400, detail="watermark_type must be 'image' or 'text'")
        
        # Validate position
        valid_positions = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]
        if position not in valid_positions:
            raise HTTPException(status_code=400, detail=f"position must be one of: {', '.join(valid_positions)}")
        
        # Validate opacity
        if not 0.0 <= opacity <= 1.0:
            raise HTTPException(status_code=400, detail="opacity must be between 0.0 and 1.0")
        
        # Validate size
        if not 0 < size <= 500:
            raise HTTPException(status_code=400, detail="size must be between 1 and 500 pixels")
        
        parameters = {
            "watermark_type": watermark_type,
            "position": position,
            "opacity": opacity,
            "size": size
        }
        
        if watermark_type == "image":
            if not watermark_file:
                raise HTTPException(status_code=400, detail="Watermark file is required for image watermark")
            
            # Save watermark file
            from app.services.storage_service import StorageService
            storage = StorageService()
            
            file_content = await watermark_file.read()
            watermark_path = storage.save_uploaded_file(file_content, watermark_file.filename)
            parameters["watermark_path"] = watermark_path
            
        elif watermark_type == "text":
            if not content:
                raise HTTPException(status_code=400, detail="Text content is required for text watermark")
            parameters["text"] = content
        
        # Create job
        job = Job(
            video_id=video_uuid,
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
