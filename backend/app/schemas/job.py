from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class JobCreate(BaseModel):
    """Schema for job creation"""
    video_id: Optional[uuid.UUID] = None
    job_type: str
    parameters: Optional[Dict[str, Any]] = None


class JobResponse(BaseModel):
    """Schema for job response"""
    id: uuid.UUID
    video_id: Optional[uuid.UUID] = None
    job_type: str
    status: str
    progress: int
    parameters: Optional[Dict[str, Any]] = None
    result_path: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class JobStatus(BaseModel):
    """Schema for job status response"""
    id: uuid.UUID
    status: str
    progress: int
    error_message: Optional[str] = None
    result_path: Optional[str] = None
