from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import uuid


class VideoCreate(BaseModel):
    """Schema for video upload"""
    pass  # File will be handled separately


class VideoResponse(BaseModel):
    """Schema for video response"""
    id: uuid.UUID
    filename: str
    original_filename: str
    file_size: int
    duration: Decimal
    format: str
    resolution: str
    fps: Optional[Decimal] = None
    bitrate: Optional[int] = None
    upload_time: datetime
    status: str
    thumbnail_path: Optional[str] = None

    class Config:
        from_attributes = True


class VideoList(BaseModel):
    """Schema for video list response"""
    videos: List[VideoResponse]
    total: int
    page: int
    size: int


class VideoQualityResponse(BaseModel):
    """Schema for video quality response"""
    id: uuid.UUID
    quality: str
    file_path: str
    file_size: int
    bitrate: Optional[int] = None
    resolution: str
    created_at: datetime

    class Config:
        from_attributes = True


class TrimRequest(BaseModel):
    """Schema for video trim request"""
    video_id: uuid.UUID
    start_time: float = Field(..., ge=0, description="Start time in seconds")
    end_time: float = Field(..., gt=0, description="End time in seconds")


class QualityRequest(BaseModel):
    """Schema for quality generation request"""
    video_id: uuid.UUID
    qualities: List[str] = Field(default=["1080p", "720p", "480p"], description="List of qualities to generate")
