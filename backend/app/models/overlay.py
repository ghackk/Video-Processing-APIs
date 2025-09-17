from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.config.database import Base


class Overlay(Base):
    __tablename__ = "overlays"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    overlay_type = Column(String(20), nullable=False)  # 'text', 'image', 'video'
    content = Column(Text)  # For text overlays
    file_path = Column(String(500))  # For image/video overlays
    position_x = Column(Integer)
    position_y = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    start_time = Column(DECIMAL(10, 3))
    end_time = Column(DECIMAL(10, 3))
    opacity = Column(DECIMAL(3, 2), default=1.0)
    font_family = Column(String(100))
    font_size = Column(Integer)
    font_color = Column(String(7))  # Hex color
    language = Column(String(10))  # For multi-language support
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    video = relationship("Video", back_populates="overlays")

    def __repr__(self):
        return f"<Overlay(id={self.id}, type={self.overlay_type})>"
