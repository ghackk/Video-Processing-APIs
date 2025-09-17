from sqlalchemy import Column, String, Integer, BigInteger, DateTime, Text, ForeignKey, DECIMAL, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.config.database import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    duration = Column(DECIMAL(10, 3), nullable=False)
    format = Column(String(50), nullable=False)
    resolution = Column(String(20), nullable=False)
    fps = Column(DECIMAL(5, 2))
    bitrate = Column(Integer)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(UUID(as_uuid=True), nullable=True)  # For future user system
    status = Column(String(20), default="uploaded")
    thumbnail_path = Column(String(500))
    
    # Relationships
    jobs = relationship("Job", back_populates="video", cascade="all, delete-orphan")
    overlays = relationship("Overlay", back_populates="video", cascade="all, delete-orphan")
    qualities = relationship("VideoQuality", back_populates="video", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Video(id={self.id}, filename={self.filename})>"


class ProcessedVideo(Base):
    __tablename__ = "processed_videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    duration = Column(DECIMAL(10, 3), nullable=False)
    format = Column(String(50), nullable=False)
    resolution = Column(String(20), nullable=False)
    fps = Column(DECIMAL(5, 2))
    bitrate = Column(Integer)
    processing_type = Column(String(50), nullable=False)  # 'trim', 'overlay', 'watermark', 'quality'
    parameters = Column(JSON)  # Store processing parameters
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    original_video = relationship("Video", foreign_keys=[original_video_id])
    job = relationship("Job", foreign_keys=[job_id])

    def __repr__(self):
        return f"<ProcessedVideo(id={self.id}, type={self.processing_type})>"


class VideoQuality(Base):
    __tablename__ = "video_qualities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    quality = Column(String(10), nullable=False)  # '1080p', '720p', '480p', '360p'
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    bitrate = Column(Integer)
    resolution = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    video = relationship("Video", back_populates="qualities")

    def __repr__(self):
        return f"<VideoQuality(id={self.id}, quality={self.quality})>"
