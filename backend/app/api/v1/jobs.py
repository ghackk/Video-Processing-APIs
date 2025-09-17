from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from app.config.database import get_db
from app.models.job import Job
from app.schemas.job import JobResponse, JobStatus
from app.tasks.video_tasks import process_video_upload, process_video_trim, process_quality_generation

router = APIRouter()


@router.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(
    job_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get job status (Level 4) - Exact endpoint from requirements"""
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JobStatus(
            id=job.id,
            status=job.status,
            progress=job.progress,
            error_message=job.error_message,
            result_path=job.result_path
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result/{job_id}")
async def get_job_result(
    job_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Download processed video result (Level 4) - Exact endpoint from requirements"""
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status != "completed":
            raise HTTPException(
                status_code=400, 
                detail=f"Job not completed. Current status: {job.status}"
            )
        
        if not job.result_path:
            raise HTTPException(status_code=404, detail="Result file not found")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            job.result_path,
            filename=f"processed_{job_id}.mp4",
            media_type="video/mp4"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/status", response_model=JobResponse)
async def get_job_details(
    job_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get detailed job information"""
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JobResponse.from_orm(job)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/progress")
async def get_job_progress(
    job_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get job progress percentage"""
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "job_id": job.id,
            "progress": job.progress,
            "status": job.status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{job_id}")
async def cancel_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Cancel a pending job"""
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status not in ["pending", "processing"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel job with status: {job.status}"
            )
        
        # Update job status
        job.status = "cancelled"
        db.commit()
        
        return {"message": "Job cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all jobs with filtering"""
    try:
        query = db.query(Job)
        
        if status:
            query = query.filter(Job.status == status)
        if job_type:
            query = query.filter(Job.job_type == job_type)
        
        jobs = query.offset(skip).limit(limit).all()
        return [JobResponse.from_orm(job) for job in jobs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
