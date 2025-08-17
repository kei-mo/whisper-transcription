import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ProjectStructure:
    """音声プロジェクトのディレクトリ構造を管理するクラス"""
    
    def __init__(self, base_dir: str = "audio_projects"):
        """
        Initialize project structure manager.
        
        Args:
            base_dir: Base directory for all audio projects
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def create_project(self, project_name: str, project_type: str = "local", 
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Path]:
        """
        Create a new audio project with the standard directory structure.
        
        Args:
            project_name: Name for the project (will be prefixed based on type)
            project_type: Type of project ("youtube" or "local")
            metadata: Additional metadata to save
        
        Returns:
            Dictionary containing paths to created directories
        """
        # Create project folder with appropriate prefix
        if project_type == "youtube":
            folder_name = f"youtube_{project_name}"
        else:
            folder_name = f"local_{project_name}"
        
        project_dir = self.base_dir / folder_name
        
        # Create directory structure
        project_dir.mkdir(exist_ok=True)
        src_audio_dir = project_dir / "src_audio"
        transcription_dir = project_dir / "transcription"
        
        src_audio_dir.mkdir(exist_ok=True)
        transcription_dir.mkdir(exist_ok=True)
        
        # Save metadata
        if metadata:
            metadata_file = project_dir / "metadata.json"
            metadata["created_at"] = datetime.now().isoformat()
            metadata["project_type"] = project_type
            
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return {
            "project_dir": project_dir,
            "src_audio_dir": src_audio_dir,
            "transcription_dir": transcription_dir
        }
    
    def save_transcription_settings(self, project_dir: Path, settings: Dict[str, Any]):
        """
        Save transcription settings to the project.
        
        Args:
            project_dir: Path to the project directory
            settings: Transcription settings to save
        """
        transcription_dir = project_dir / "transcription"
        settings_file = transcription_dir / "settings.json"
        
        settings_data = {
            **settings,
            "processed_at": datetime.now().isoformat()
        }
        
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(settings_data, f, ensure_ascii=False, indent=2)
    
    def move_audio_to_project(self, audio_file: str, project_dirs: Dict[str, Path], 
                             keep_original: bool = False) -> Path:
        """
        Move or copy audio file to the project's src_audio directory.
        
        Args:
            audio_file: Path to the original audio file
            project_dirs: Dictionary containing project directories
            keep_original: Whether to keep the original file (copy instead of move)
        
        Returns:
            Path to the audio file in the project directory
        """
        audio_path = Path(audio_file)
        dest_path = project_dirs["src_audio_dir"] / audio_path.name
        
        if keep_original:
            shutil.copy2(audio_path, dest_path)
        else:
            shutil.move(str(audio_path), dest_path)
        
        return dest_path
    
    def save_transcription_outputs(self, project_dirs: Dict[str, Path], 
                                  outputs: Dict[str, str], base_name: str = "transcript"):
        """
        Save transcription outputs to the project's transcription directory.
        
        Args:
            project_dirs: Dictionary containing project directories
            outputs: Dictionary of output format -> content
            base_name: Base name for output files
        
        Returns:
            Dictionary of output format -> file path
        """
        transcription_dir = project_dirs["transcription_dir"]
        saved_files = {}
        
        for format_type, content in outputs.items():
            if format_type == "text":
                file_path = transcription_dir / f"{base_name}.txt"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            elif format_type == "json":
                file_path = transcription_dir / f"{base_name}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(json.loads(content) if isinstance(content, str) else content, 
                             f, ensure_ascii=False, indent=2)
            elif format_type == "srt":
                file_path = transcription_dir / f"{base_name}.srt"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            elif format_type == "vtt":
                file_path = transcription_dir / f"{base_name}.vtt"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            
            saved_files[format_type] = str(file_path)
        
        return saved_files
    
    def list_projects(self) -> list:
        """
        List all existing projects.
        
        Returns:
            List of project directory names
        """
        if not self.base_dir.exists():
            return []
        
        projects = []
        for item in self.base_dir.iterdir():
            if item.is_dir() and (item.name.startswith("youtube_") or item.name.startswith("local_")):
                projects.append(item.name)
        
        return sorted(projects)
    
    def get_project_info(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific project.
        
        Args:
            project_name: Name of the project
        
        Returns:
            Project information dictionary or None if not found
        """
        project_dir = self.base_dir / project_name
        
        if not project_dir.exists():
            return None
        
        info = {
            "name": project_name,
            "path": str(project_dir),
            "has_audio": len(list((project_dir / "src_audio").glob("*"))) > 0,
            "has_transcription": len(list((project_dir / "transcription").glob("*"))) > 0,
        }
        
        # Load metadata if exists
        metadata_file = project_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, "r", encoding="utf-8") as f:
                info["metadata"] = json.load(f)
        
        # Load transcription settings if exists
        settings_file = project_dir / "transcription" / "settings.json"
        if settings_file.exists():
            with open(settings_file, "r", encoding="utf-8") as f:
                info["transcription_settings"] = json.load(f)
        
        return info