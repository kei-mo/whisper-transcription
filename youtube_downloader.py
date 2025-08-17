import yt_dlp
import os
from pathlib import Path
from typing import Optional, Dict, Any
import re
from project_structure import ProjectStructure


class YouTubeDownloader:
    def __init__(self, use_project_structure: bool = True):
        """
        Initialize YouTube downloader.
        
        Args:
            use_project_structure: Whether to use the new project structure
        """
        self.use_project_structure = use_project_structure
        if use_project_structure:
            self.project_manager = ProjectStructure()
        else:
            self.output_dir = Path("audio_files")
            self.output_dir.mkdir(exist_ok=True)
    
    def download_audio(self, url: str, audio_format: str = "mp3",
                      quality: str = "best") -> Dict[str, Any]:
        """
        Download audio from a YouTube video.
        
        Args:
            url: YouTube video URL
            audio_format: Output audio format (mp3, wav, m4a, etc.)
            quality: Audio quality (best, worst, or specific bitrate)
        
        Returns:
            Dictionary containing download information
        """
        video_id = self._extract_video_id(url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {url}")
        
        if self.use_project_structure:
            temp_output_dir = Path("temp_downloads")
            temp_output_dir.mkdir(exist_ok=True)
            output_template = str(temp_output_dir / f"{video_id}.%(ext)s")
        else:
            output_template = str(self.output_dir / f"{video_id}.%(ext)s")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
                'preferredquality': '192' if quality == 'best' else '128',
            }],
            'outtmpl': output_template,
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
        }
        
        print(f"Downloading audio from: {url}")
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if self.use_project_structure:
                    temp_dir = Path("temp_downloads")
                    audio_file = temp_dir / f"{video_id}.{audio_format}"
                    
                    if not audio_file.exists():
                        for file in temp_dir.glob(f"{video_id}.*"):
                            if file.suffix.lower() in ['.mp3', '.m4a', '.wav', '.opus', '.webm']:
                                audio_file = file
                                break
                    
                    # Create project structure
                    metadata = {
                        "title": info.get("title", "Unknown"),
                        "duration": info.get("duration", 0),
                        "uploader": info.get("uploader", "Unknown"),
                        "video_id": video_id,
                        "url": url,
                        "upload_date": info.get("upload_date", "Unknown"),
                        "view_count": info.get("view_count", 0),
                        "description": info.get("description", "")
                    }
                    
                    project_dirs = self.project_manager.create_project(
                        project_name=video_id,
                        project_type="youtube",
                        metadata=metadata
                    )
                    
                    # Move audio file to project structure
                    final_audio_file = self.project_manager.move_audio_to_project(
                        str(audio_file), project_dirs, keep_original=False
                    )
                    
                    # Clean up temp directory
                    if temp_dir.exists():
                        import shutil
                        shutil.rmtree(temp_dir, ignore_errors=True)
                    
                    return {
                        "title": info.get("title", "Unknown"),
                        "duration": info.get("duration", 0),
                        "uploader": info.get("uploader", "Unknown"),
                        "video_id": video_id,
                        "audio_file": str(final_audio_file),
                        "format": audio_format,
                        "url": url,
                        "project_dirs": project_dirs
                    }
                else:
                    audio_file = self.output_dir / f"{video_id}.{audio_format}"
                    
                    if not audio_file.exists():
                        for file in self.output_dir.glob(f"{video_id}.*"):
                            if file.suffix.lower() in ['.mp3', '.m4a', '.wav', '.opus', '.webm']:
                                audio_file = file
                                break
                    
                    return {
                        "title": info.get("title", "Unknown"),
                        "duration": info.get("duration", 0),
                        "uploader": info.get("uploader", "Unknown"),
                        "video_id": video_id,
                        "audio_file": str(audio_file),
                        "format": audio_format,
                        "url": url
                    }
        
        except Exception as e:
            raise Exception(f"Failed to download audio: {str(e)}")
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
            r'(?:live\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Get information about a YouTube video without downloading.
        
        Args:
            url: YouTube video URL
        
        Returns:
            Dictionary containing video information
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    "title": info.get("title", "Unknown"),
                    "duration": info.get("duration", 0),
                    "uploader": info.get("uploader", "Unknown"),
                    "upload_date": info.get("upload_date", "Unknown"),
                    "view_count": info.get("view_count", 0),
                    "description": info.get("description", ""),
                    "video_id": info.get("id", ""),
                    "url": url
                }
        
        except Exception as e:
            raise Exception(f"Failed to get video info: {str(e)}")