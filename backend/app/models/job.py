from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.config.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=True)
    job_type = Column(String(50), nullable=False)  # 'upload', 'trim', 'overlay', 'watermark', 'quality'
    status = Column(String(20), default="pending")  # 'pending', 'processing', 'completed', 'failed'
    progress = Column(Integer, default=0)  # 0-100
    parameters = Column(JSON)  # Job parameters
    result_path = Column(String(500))  # Path to result file
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    video = relationship("Video", back_populates="jobs")

    def __repr__(self):
        return f"<Job(id={self.id}, type={self.job_type}, status={self.status})>"
