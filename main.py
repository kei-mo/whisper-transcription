#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from audio_transcriber import AudioTranscriber
from youtube_downloader import YouTubeDownloader
from project_structure import ProjectStructure


def transcribe_local_audio(audio_path: str, model_size: str = "base",
                          language: str = None, output_format: str = "all"):
    """
    Transcribe a local audio file.
    
    Args:
        audio_path: Path to the audio file
        model_size: Whisper model size
        language: Language code for transcription
        output_format: Output format(s) to generate
    """
    print(f"\n=== Transcribing Local Audio ===")
    print(f"File: {audio_path}")
    
    # Create project structure for local audio
    project_manager = ProjectStructure()
    audio_file_path = Path(audio_path)
    
    metadata = {
        "original_filename": audio_file_path.name,
        "file_size": audio_file_path.stat().st_size if audio_file_path.exists() else 0,
        "source_type": "local"
    }
    
    project_dirs = project_manager.create_project(
        project_name=audio_file_path.stem,
        project_type="local",
        metadata=metadata
    )
    
    # Copy audio file to project structure
    final_audio_path = project_manager.move_audio_to_project(
        audio_path, project_dirs, keep_original=True
    )
    
    transcriber = AudioTranscriber(model_size=model_size)
    result = transcriber.transcribe_audio(
        audio_path=str(final_audio_path),
        language=language,
        output_format=output_format,
        project_dirs=project_dirs
    )
    
    print(f"\n=== Transcription Complete ===")
    print(f"Detected Language: {result['language']}")
    print(f"Duration: {result['duration']:.2f} seconds")
    print(f"\nTranscription Preview (first 500 chars):")
    print(result['text'][:500])
    
    if result['output_files']:
        print(f"\nOutput files saved:")
        for format_type, file_path in result['output_files'].items():
            print(f"  - {format_type}: {file_path}")
    
    return result


def transcribe_youtube(url: str, model_size: str = "base",
                      language: str = None, output_format: str = "all",
                      audio_format: str = "mp3", keep_audio: bool = False):
    """
    Download and transcribe audio from a YouTube video.
    
    Args:
        url: YouTube video URL
        model_size: Whisper model size
        language: Language code for transcription
        output_format: Output format(s) to generate
        audio_format: Format for downloaded audio
        keep_audio: Whether to keep the downloaded audio file
    """
    print(f"\n=== Processing YouTube Video ===")
    print(f"URL: {url}")
    
    downloader = YouTubeDownloader()
    
    print("\n1. Getting video information...")
    try:
        video_info = downloader.get_video_info(url)
        print(f"Title: {video_info['title']}")
        print(f"Uploader: {video_info['uploader']}")
        print(f"Duration: {video_info['duration']} seconds")
    except Exception as e:
        print(f"Warning: Could not fetch video info: {e}")
    
    print("\n2. Downloading audio...")
    download_result = downloader.download_audio(
        url=url,
        audio_format=audio_format,
        quality="best"
    )
    
    audio_file = download_result['audio_file']
    print(f"Audio saved to: {audio_file}")
    
    print("\n3. Transcribing audio...")
    transcriber = AudioTranscriber(model_size=model_size)
    
    # Pass project_dirs if available
    transcribe_kwargs = {
        "audio_path": audio_file,
        "language": language,
        "output_format": output_format
    }
    if "project_dirs" in download_result:
        transcribe_kwargs["project_dirs"] = download_result["project_dirs"]
    
    result = transcriber.transcribe_audio(**transcribe_kwargs)
    
    if not keep_audio:
        print(f"\n4. Cleaning up audio file...")
        Path(audio_file).unlink()
        print(f"Deleted: {audio_file}")
    
    print(f"\n=== Transcription Complete ===")
    print(f"Video Title: {download_result['title']}")
    print(f"Detected Language: {result['language']}")
    print(f"Duration: {result['duration']:.2f} seconds")
    print(f"\nTranscription Preview (first 500 chars):")
    print(result['text'][:500])
    
    if result['output_files']:
        print(f"\nOutput files saved:")
        for format_type, file_path in result['output_files'].items():
            print(f"  - {format_type}: {file_path}")
    
    return result


def list_projects():
    """List all audio projects."""
    print(f"\n=== Audio Projects ===")
    
    project_manager = ProjectStructure()
    projects = project_manager.list_projects()
    
    if not projects:
        print("No projects found.")
        return
    
    for project_name in projects:
        project_info = project_manager.get_project_info(project_name)
        if project_info:
            print(f"\n📁 {project_name}")
            if "metadata" in project_info:
                meta = project_info["metadata"]
                if "title" in meta:
                    print(f"   Title: {meta['title']}")
                if "duration" in meta:
                    print(f"   Duration: {meta['duration']} seconds")
                if "source_type" in meta:
                    print(f"   Type: {meta['source_type']}")
            print(f"   Audio: {'✓' if project_info['has_audio'] else '✗'}")
            print(f"   Transcription: {'✓' if project_info['has_transcription'] else '✗'}")


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio files or YouTube videos using OpenAI Whisper"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List projects command
    list_parser = subparsers.add_parser("list", help="List all audio projects")
    
    audio_parser = subparsers.add_parser("audio", help="Transcribe a local audio file")
    audio_parser.add_argument("file", help="Path to the audio file")
    audio_parser.add_argument("-m", "--model", default="base",
                            choices=["tiny", "base", "small", "medium", "large"],
                            help="Whisper model size (default: base)")
    audio_parser.add_argument("-l", "--language", default=None,
                            help="Language code (e.g., 'ja' for Japanese, 'en' for English)")
    audio_parser.add_argument("-f", "--format", default="all",
                            choices=["text", "srt", "vtt", "json", "all"],
                            help="Output format (default: all)")
    
    youtube_parser = subparsers.add_parser("youtube", help="Download and transcribe a YouTube video")
    youtube_parser.add_argument("url", help="YouTube video URL")
    youtube_parser.add_argument("-m", "--model", default="base",
                              choices=["tiny", "base", "small", "medium", "large"],
                              help="Whisper model size (default: base)")
    youtube_parser.add_argument("-l", "--language", default=None,
                              help="Language code (e.g., 'ja' for Japanese, 'en' for English)")
    youtube_parser.add_argument("-f", "--format", default="all",
                              choices=["text", "srt", "vtt", "json", "all"],
                              help="Output format (default: all)")
    youtube_parser.add_argument("-a", "--audio-format", default="mp3",
                              choices=["mp3", "wav", "m4a"],
                              help="Audio format for download (default: mp3)")
    youtube_parser.add_argument("-k", "--keep-audio", action="store_true",
                              help="Keep the downloaded audio file")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "list":
            list_projects()
        
        elif args.command == "audio":
            transcribe_local_audio(
                audio_path=args.file,
                model_size=args.model,
                language=args.language,
                output_format=args.format
            )
        
        elif args.command == "youtube":
            transcribe_youtube(
                url=args.url,
                model_size=args.model,
                language=args.language,
                output_format=args.format,
                audio_format=args.audio_format,
                keep_audio=args.keep_audio
            )
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()