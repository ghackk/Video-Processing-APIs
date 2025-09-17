from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
import uuid


class OverlayCreate(BaseModel):
    """Schema for overlay creation"""
    video_id: uuid.UUID
    overlay_type: str = Field(..., pattern="^(text|image|video)$")
    content: Optional[str] = None  # For text overlays
    file_path: Optional[str] = None  # For image/video overlays
    position_x: Optional[int] = Field(None, ge=0)
    position_y: Optional[int] = Field(None, ge=0)
    width: Optional[int] = Field(None, gt=0)
    height: Optional[int] = Field(None, gt=0)
    start_time: Optional[float] = Field(None, ge=0)
    end_time: Optional[float] = Field(None, gt=0)
    opacity: Optional[float] = Field(1.0, ge=0.0, le=1.0)
    font_family: Optional[str] = None
    font_size: Optional[int] = Field(None, gt=0)
    font_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    language: Optional[str] = Field("en", description="Language for text rendering (en, hindi, tamil, telugu, bengali, gujarati, marathi, kannada, malayalam, punjabi, odia)")


class OverlayResponse(BaseModel):
    """Schema for overlay response"""
    id: uuid.UUID
    video_id: uuid.UUID
    overlay_type: str
    content: Optional[str] = None
    file_path: Optional[str] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    start_time: Optional[Decimal] = None
    end_time: Optional[Decimal] = None
    opacity: Optional[Decimal] = None
    font_family: Optional[str] = None
    font_size: Optional[int] = None
    font_color: Optional[str] = None
    language: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WatermarkRequest(BaseModel):
    """Schema for watermark request"""
    video_id: uuid.UUID
    watermark_type: str = Field(..., pattern="^(image|text)$")
    content: Optional[str] = None  # For text watermarks
    file_path: Optional[str] = None  # For image watermarks
    position: str = Field("bottom-right", pattern="^(top-left|top-right|bottom-left|bottom-right|center)$")
    opacity: Optional[float] = Field(0.5, ge=0.0, le=1.0)
    size: Optional[int] = Field(100, gt=0, le=500)  # Size in pixels
