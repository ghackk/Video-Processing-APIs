import os
import uuid
import shutil
from pathlib import Path
from typing import Optional
from app.config.settings import settings


class StorageService:
    """Service for file storage operations"""
    
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.processed_dir = Path(settings.processed_dir)
        self.max_file_size = settings.max_file_size
        self.allowed_extensions = settings.allowed_extensions
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file to storage"""
        # Generate unique filename
        file_extension = Path(filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = self.upload_dir / unique_filename
        
        # Ensure directory exists
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return str(file_path)
    
    def validate_file(self, filename: str, file_size: int) -> bool:
        """Validate uploaded file"""
        # Check file size
        if file_size > self.max_file_size:
            return False
        
        # Check file extension
        file_extension = Path(filename).suffix.lower().lstrip('.')
        if file_extension not in self.allowed_extensions:
            return False
        
        return True
    
    def get_file_path(self, filename: str) -> Optional[str]:
        """Get full path for a file"""
        file_path = self.upload_dir / filename
        if file_path.exists():
            return str(file_path)
        return None
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    def create_processed_file_path(self, filename: str, suffix: str = "") -> str:
        """Create path for processed file"""
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        if suffix:
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{suffix}{ext}"
        
        return str(self.processed_dir / filename)
    
    def copy_file(self, source_path: str, dest_path: str) -> bool:
        """Copy file from source to destination"""
        try:
            shutil.copy2(source_path, dest_path)
            return True
        except Exception:
            return False
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0
    
    def ensure_directory(self, directory_path: str) -> None:
        """Ensure directory exists"""
        Path(directory_path).mkdir(parents=True, exist_ok=True)
