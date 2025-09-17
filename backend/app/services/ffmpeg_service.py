import subprocess
import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from app.config.settings import settings


class FFmpegService:
    """Service for handling FFmpeg operations"""
    
    def __init__(self):
        self.ffmpeg_path = settings.ffmpeg_path
        self.ffprobe_path = settings.ffprobe_path
    
    def get_video_metadata(self, video_path: str) -> Dict[str, Any]:
        """Extract video metadata using ffprobe"""
        try:
            cmd = [
                self.ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            metadata = json.loads(result.stdout)
            
            # Extract relevant information
            video_stream = next(
                (stream for stream in metadata["streams"] if stream["codec_type"] == "video"),
                None
            )
            
            if not video_stream:
                raise ValueError("No video stream found")
            
            format_info = metadata["format"]
            
            return {
                "duration": float(format_info.get("duration", 0)),
                "size": int(format_info.get("size", 0)),
                "format": format_info.get("format_name", ""),
                "resolution": f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}",
                "fps": eval(video_stream.get("r_frame_rate", "0/1")),
                "bitrate": int(format_info.get("bit_rate", 0))
            }
        except subprocess.CalledProcessError as e:
            raise Exception(f"FFprobe error: {e.stderr}")
        except Exception as e:
            raise Exception(f"Error extracting metadata: {str(e)}")
    
    def generate_thumbnail(self, video_path: str, output_path: str, timestamp: float = 1.0) -> str:
        """Generate thumbnail from video"""
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-ss", str(timestamp),
                "-vframes", "1",
                "-q:v", "2",
                "-y",  # Overwrite output file
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            raise Exception(f"Thumbnail generation failed: {e.stderr}")
    
    def trim_video(self, input_path: str, output_path: str, start_time: float, end_time: float) -> str:
        """Trim video to specified time range"""
        try:
            duration = end_time - start_time
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-ss", str(start_time),
                "-t", str(duration),
                "-c", "copy",  # Copy without re-encoding for speed
                "-avoid_negative_ts", "make_zero",
                "-y",
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            raise Exception(f"Video trimming failed: {e.stderr}")
    
    def add_text_overlay(self, input_path: str, output_path: str, text: str, 
                        position: tuple, font_size: int = 24, 
                        font_color: str = "white", language: str = "en") -> str:
        """Add text overlay to video"""
        try:
            # Get font path based on language
            font_path = self._get_font_path(language)
            
            x, y = position
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-vf", f"drawtext=text='{text}':fontfile={font_path}:fontsize={font_size}:x={x}:y={y}:fontcolor={font_color}",
                "-c:a", "copy",
                "-y",
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            raise Exception(f"Text overlay failed: {e.stderr}")
    
    def add_image_overlay(self, input_path: str, output_path: str, overlay_path: str,
                         position: tuple, size: Optional[tuple] = None) -> str:
        """Add image overlay to video"""
        try:
            x, y = position
            if size:
                width, height = size
                filter_complex = f"[1:v]scale={width}:{height}[scaled];[0:v][scaled]overlay={x}:{y}"
            else:
                filter_complex = f"[0:v][1:v]overlay={x}:{y}"
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-i", overlay_path,
                "-filter_complex", filter_complex,
                "-c:a", "copy",
                "-y",
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            raise Exception(f"Image overlay failed: {e.stderr}")
    
    def add_watermark(self, input_path: str, output_path: str, watermark_path: str,
                     position: str = "bottom-right", opacity: float = 0.5) -> str:
        """Add watermark to video"""
        try:
            # Calculate position based on string
            position_map = {
                "top-left": "10:10",
                "top-right": "W-w-10:10",
                "bottom-left": "10:H-h-10",
                "bottom-right": "W-w-10:H-h-10",
                "center": "(W-w)/2:(H-h)/2"
            }
            
            pos = position_map.get(position, "W-w-10:H-h-10")
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-i", watermark_path,
                "-filter_complex", f"[1:v]format=rgba,colorchannelmixer=aa={opacity}[watermark];[0:v][watermark]overlay={pos}",
                "-c:a", "copy",
                "-y",
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            raise Exception(f"Watermark addition failed: {e.stderr}")
    
    def generate_quality_versions(self, input_path: str, output_dir: str, 
                                 qualities: List[str]) -> Dict[str, str]:
        """Generate multiple quality versions of video"""
        results = {}
        
        quality_settings = {
            "1080p": {"scale": "1920:1080", "bitrate": "5000k", "audio_bitrate": "128k"},
            "720p": {"scale": "1280:720", "bitrate": "2500k", "audio_bitrate": "128k"},
            "480p": {"scale": "854:480", "bitrate": "1000k", "audio_bitrate": "96k"},
            "360p": {"scale": "640:360", "bitrate": "500k", "audio_bitrate": "64k"}
        }
        
        for quality in qualities:
            if quality not in quality_settings:
                continue
                
            settings = quality_settings[quality]
            output_path = os.path.join(output_dir, f"{quality}.mp4")
            
            try:
                cmd = [
                    self.ffmpeg_path,
                    "-i", input_path,
                    "-vf", f"scale={settings['scale']}",
                    "-c:v", "libx264",
                    "-b:v", settings["bitrate"],
                    "-c:a", "aac",
                    "-b:a", settings["audio_bitrate"],
                    "-y",
                    output_path
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                results[quality] = output_path
            except subprocess.CalledProcessError as e:
                raise Exception(f"Quality {quality} generation failed: {e.stderr}")
        
        return results
    
    def _get_font_path(self, language: str) -> str:
        """Get font path for specific language"""
        font_map = {
            "hindi": "assets/fonts/hindi/NotoSansDevanagari-Regular.ttf",
            "tamil": "assets/fonts/tamil/NotoSansTamil-Regular.ttf",
            "telugu": "assets/fonts/telugu/NotoSansTelugu-Regular.ttf",
            "bengali": "assets/fonts/bengali/NotoSansBengali-Regular.ttf",
            "gujarati": "assets/fonts/gujarati/NotoSansGujarati-Regular.ttf",
            "marathi": "assets/fonts/marathi/NotoSansDevanagari-Regular.ttf",
            "kannada": "assets/fonts/kannada/NotoSansKannada-Regular.ttf",
            "malayalam": "assets/fonts/malayalam/NotoSansMalayalam-Regular.ttf",
            "punjabi": "assets/fonts/punjabi/NotoSansGurmukhi-Regular.ttf",
            "odia": "assets/fonts/odia/NotoSansOriya-Regular.ttf"
        }
        
        return font_map.get(language, "assets/fonts/default/NotoSans-Regular.ttf")
