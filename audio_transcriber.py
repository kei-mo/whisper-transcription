import whisper
import os
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime
from project_structure import ProjectStructure


class AudioTranscriber:
    def __init__(self, model_size: str = "base", use_project_structure: bool = True):
        """
        Initialize the Whisper transcriber.
        
        Args:
            model_size: Size of the Whisper model to use.
                       Options: tiny, base, small, medium, large
            use_project_structure: Whether to use the new project structure
        """
        print(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        self.model_size = model_size
        self.use_project_structure = use_project_structure
        
        if not use_project_structure:
            self.output_dir = Path("transcriptions")
            self.output_dir.mkdir(exist_ok=True)
        else:
            self.project_manager = ProjectStructure()
    
    def transcribe_audio(self, audio_path: str, language: Optional[str] = None,
                        output_format: str = "all", project_dirs: Optional[Dict[str, Path]] = None) -> Dict[str, Any]:
        """
        Transcribe an audio file using Whisper.
        
        Args:
            audio_path: Path to the audio file
            language: Language code (e.g., 'ja' for Japanese, 'en' for English)
            output_format: Output format - 'text', 'srt', 'vtt', 'json', or 'all'
            project_dirs: Directory structure for project-based organization
        
        Returns:
            Dictionary containing transcription results
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        print(f"Transcribing: {audio_path}")
        
        options = {
            "language": language,
            "task": "transcribe",
            "verbose": True
        }
        
        if language:
            print(f"Language set to: {language}")
        
        result = self.model.transcribe(audio_path, **options)
        
        # Save transcription settings
        transcription_settings = {
            "model_size": self.model_size,
            "language": language,
            "output_format": output_format,
            "audio_file": audio_path
        }
        
        outputs = {}
        
        if self.use_project_structure and project_dirs:
            # Save settings to project
            self.project_manager.save_transcription_settings(
                project_dirs["project_dir"], transcription_settings
            )
            
            # Prepare outputs for project structure
            output_contents = {}
            if output_format in ["text", "all"]:
                output_contents["text"] = result["text"]
            if output_format in ["json", "all"]:
                output_contents["json"] = result
            if output_format in ["srt", "all"]:
                output_contents["srt"] = self._generate_srt(result["segments"])
            if output_format in ["vtt", "all"]:
                output_contents["vtt"] = self._generate_vtt(result["segments"])
            
            # Save all outputs to project structure
            outputs = self.project_manager.save_transcription_outputs(
                project_dirs, output_contents
            )
            
            for format_type, file_path in outputs.items():
                print(f"{format_type.upper()} saved to: {file_path}")
        
        else:
            # Use old structure
            base_name = Path(audio_path).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_base = self.output_dir / f"{base_name}_{timestamp}"
            
            if output_format in ["text", "all"]:
                text_file = f"{output_base}.txt"
                with open(text_file, "w", encoding="utf-8") as f:
                    f.write(result["text"])
                outputs["text"] = text_file
                print(f"Text saved to: {text_file}")
            
            if output_format in ["json", "all"]:
                json_file = f"{output_base}.json"
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                outputs["json"] = json_file
                print(f"JSON saved to: {json_file}")
            
            if output_format in ["srt", "all"]:
                srt_file = f"{output_base}.srt"
                self._write_srt(result["segments"], srt_file)
                outputs["srt"] = srt_file
                print(f"SRT saved to: {srt_file}")
            
            if output_format in ["vtt", "all"]:
                vtt_file = f"{output_base}.vtt"
                self._write_vtt(result["segments"], vtt_file)
                outputs["vtt"] = vtt_file
                print(f"VTT saved to: {vtt_file}")
        
        return {
            "text": result["text"],
            "language": result.get("language", "unknown"),
            "duration": result.get("duration", 0),
            "output_files": outputs,
            "segments": result.get("segments", [])
        }
    
    def _write_srt(self, segments, output_path):
        """Write segments to SRT format."""
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, 1):
                start = self._format_timestamp(segment["start"], srt=True)
                end = self._format_timestamp(segment["end"], srt=True)
                text = segment["text"].strip()
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
    
    def _write_vtt(self, segments, output_path):
        """Write segments to WebVTT format."""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n")
            for segment in segments:
                start = self._format_timestamp(segment["start"])
                end = self._format_timestamp(segment["end"])
                text = segment["text"].strip()
                f.write(f"{start} --> {end}\n{text}\n\n")
    
    def _generate_srt(self, segments):
        """Generate SRT content as string."""
        content = []
        for i, segment in enumerate(segments, 1):
            start = self._format_timestamp(segment["start"], srt=True)
            end = self._format_timestamp(segment["end"], srt=True)
            text = segment["text"].strip()
            content.append(f"{i}\n{start} --> {end}\n{text}\n")
        return "\n".join(content)
    
    def _generate_vtt(self, segments):
        """Generate WebVTT content as string."""
        content = ["WEBVTT\n"]
        for segment in segments:
            start = self._format_timestamp(segment["start"])
            end = self._format_timestamp(segment["end"])
            text = segment["text"].strip()
            content.append(f"{start} --> {end}\n{text}\n")
        return "\n".join(content)
    
    def _format_timestamp(self, seconds, srt=False):
        """Format timestamp for SRT or VTT."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        
        if srt:
            return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace(".", ",")
        else:
            return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"