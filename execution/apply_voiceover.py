import argparse
import subprocess
import os
import sys
from pathlib import Path

def apply_voiceover(video_file, audio_file, subtitle_file, output_file):
    """
    Combines video with voiceover audio and burns in subtitles.
    Replaces original audio with voiceover.
    """
    video_path = Path(video_file)
    audio_path = Path(audio_file)
    sub_path = Path(subtitle_file) if subtitle_file else None
    output_path = Path(output_file)

    if not video_path.exists():
        print(f"Error: Video file '{video_file}' does not exist.")
        sys.exit(1)

    if not audio_path.exists():
        print(f"Error: Audio file '{audio_file}' does not exist.")
        sys.exit(1)

    if sub_path and not sub_path.exists():
        print(f"Error: Subtitle file '{subtitle_file}' does not exist.")
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Applying voiceover and subtitles to '{video_path.name}'...")

    # Build FFmpeg command
    cmd = [
        'ffmpeg',
        '-y',
        '-i', str(video_path),
        '-i', str(audio_path)
    ]

    # Filter complex for subtitles
    filter_complex = ""
    if sub_path:
        escaped_sub_path = str(sub_path).replace(":", "\\:")
        # Default style (can be enhanced to match add_subtitles logic)
        style = "Fontsize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1,Shadow=1,MarginV=30"
        filter_complex = f"subtitles='{escaped_sub_path}':force_style='{style}'"
        cmd.extend(['-vf', filter_complex])

    # Mapping: Use Video from 0, Audio from 1 (Voiceover)
    # Pad audio to match video duration so full video plays
    # Use filter_complex to extend voiceover with silence to match video length
    cmd.extend([
        '-filter_complex', '[1:a]apad[a]',
        '-map', '0:v',
        '-map', '[a]',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-shortest',  # Now -shortest stops at video end (audio is padded infinitely)
        str(output_path)
    ])

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Success! Output saved to: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing video: {e}")
        print(f"FFmpeg Error: {e.stderr.decode()}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add voiceover and subtitles to video.")
    parser.add_argument("--video", required=True, help="Input video file")
    parser.add_argument("--audio", required=True, help="Input voiceover audio file")
    parser.add_argument("--subtitles", help="Input SRT file (optional)")
    parser.add_argument("--output", required=True, help="Output video file")

    args = parser.parse_args()
    apply_voiceover(args.video, args.audio, args.subtitles, args.output)
