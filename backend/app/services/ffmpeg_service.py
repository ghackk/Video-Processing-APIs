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
            
            # For Hindi and other Unicode languages, use a different approach
            if language in ["hindi", "tamil", "telugu", "bengali", "gujarati", "marathi", "kannada", "malayalam", "punjabi", "odia"]:
                try:
                    # Try subtitle approach first (better Unicode support)
                    subtitle_file = self._create_subtitle_file(text, font_path, font_size, font_color, x, y)
                    
                    cmd = [
                        self.ffmpeg_path,
                        "-i", input_path,
                        "-vf", f"subtitles={subtitle_file}",
                        "-c:a", "copy",
                        "-y",
                        output_path
                    ]
                except Exception as e:
                    # Fallback to drawtext with proper font path escaping
                    print(f"Subtitle approach failed, using drawtext fallback: {e}")
                    escaped_text = text.replace("'", "\\'").replace(":", "\\:")
                    # Escape Windows path separators for FFmpeg
                    escaped_font_path = font_path.replace("\\", "\\\\").replace(":", "\\:")
                    
                    cmd = [
                        self.ffmpeg_path,
                        "-i", input_path,
                        "-vf", f"drawtext=text='{escaped_text}':fontfile='{escaped_font_path}':fontsize={font_size}:x={x}:y={y}:fontcolor={font_color}",
                        "-c:a", "copy",
                        "-y",
                        output_path
                    ]
            else:
                # Standard text overlay for English
                escaped_text = text.replace("'", "\\'").replace(":", "\\:")
                cmd = [
                    self.ffmpeg_path,
                    "-i", input_path,
                    "-vf", f"drawtext=text='{escaped_text}':fontfile={font_path}:fontsize={font_size}:x={x}:y={y}:fontcolor={font_color}",
                    "-c:a", "copy",
                    "-y",
                    output_path
                ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Clean up temporary subtitle file if it was created
            if language in ["hindi", "tamil", "telugu", "bengali", "gujarati", "marathi", "kannada", "malayalam", "punjabi", "odia"]:
                import os
                try:
                    if 'subtitle_file' in locals() and os.path.exists(subtitle_file):
                        os.remove(subtitle_file)
                except:
                    pass  # Ignore cleanup errors
            
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
            "1080p": {"height": "1080", "bitrate": "5000k", "audio_bitrate": "128k"},
            "720p": {"height": "720", "bitrate": "2500k", "audio_bitrate": "128k"},
            "480p": {"height": "480", "bitrate": "1000k", "audio_bitrate": "96k"},
            "360p": {"height": "360", "bitrate": "500k", "audio_bitrate": "64k"}
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
                    "-vf", f"scale=-2:{settings['height']}",  # -2 preserves aspect ratio
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
        # Get the absolute path to the backend directory
        backend_dir = Path(__file__).parent.parent.parent
        
        font_map = {
            "hindi": backend_dir / "assets/fonts/hindi/NotoSansDevanagari-Regular.ttf",
            "tamil": backend_dir / "assets/fonts/tamil/NotoSansTamil-Regular.ttf",
            "telugu": backend_dir / "assets/fonts/telugu/NotoSansTelugu-Regular.ttf",
            "bengali": backend_dir / "assets/fonts/bengali/NotoSansBengali-Regular.ttf",
            "gujarati": backend_dir / "assets/fonts/gujarati/NotoSansGujarati-Regular.ttf",
            "marathi": backend_dir / "assets/fonts/marathi/NotoSansDevanagari-Regular.ttf",
            "kannada": backend_dir / "assets/fonts/kannada/NotoSansKannada-Regular.ttf",
            "malayalam": backend_dir / "assets/fonts/malayalam/NotoSansMalayalam-Regular.ttf",
            "punjabi": backend_dir / "assets/fonts/punjabi/NotoSansGurmukhi-Regular.ttf",
            "odia": backend_dir / "assets/fonts/odia/NotoSansOriya-Regular.ttf"
        }
        
        # Get the font path
        font_path = font_map.get(language, backend_dir / "assets/fonts/default/NotoSans-Regular.ttf")
        
        # Check if font file exists, if not, use system default
        if not font_path.exists():
            # For Hindi and other Indian languages, try to use system fonts
            if language == "hindi":
                # Try common system Hindi fonts
                system_fonts = [
                    "C:/Windows/Fonts/NotoSansDevanagari-Regular.ttf",
                    "C:/Windows/Fonts/Devanagari.ttf",
                    "/System/Library/Fonts/NotoSansDevanagari-Regular.ttf",
                    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"
                ]
                for sys_font in system_fonts:
                    if Path(sys_font).exists():
                        return str(sys_font)
            
            # If no specific font found, use system default
            return "Arial"  # FFmpeg will use system default
        
        return str(font_path)
    
    def _create_subtitle_file(self, text: str, font_path: str, font_size: int, 
                             font_color: str, x: int, y: int) -> str:
        """Create a temporary ASS subtitle file for Unicode text rendering"""
        import tempfile
        import os
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False, encoding='utf-8')
        
        # Convert color to ASS format (white = &HFFFFFF&)
        color_map = {
            "white": "&HFFFFFF&",
            "black": "&H000000&",
            "red": "&H0000FF&",
            "green": "&H00FF00&",
            "blue": "&HFF0000&",
            "yellow": "&H00FFFF&",
            "cyan": "&HFFFF00&",
            "magenta": "&HFF00FF&"
        }
        ass_color = color_map.get(font_color.lower(), "&HFFFFFF&")
        
        # Create ASS subtitle content
        ass_content = f"""[Script Info]
Title: Hindi Text Overlay
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{os.path.basename(font_path).replace('.ttf', '')},{font_size},{ass_color},&H000000&,&H000000&,&H000000&,0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,99:59:59.99,Default,,0,0,0,,{{\\pos({x},{y})}}{text}
"""
        
        temp_file.write(ass_content)
        temp_file.close()
        
        return temp_file.name
