import argparse
import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime

def add_music(input_dir, music_dir, output_dir):
    """
    Adds music to videos, generating ALL combinations (Cartesian product).
    Saves to a timestamped subfolder in output_dir.
    """
    input_path = Path(input_dir)
    music_path = Path(music_dir)
    base_output_path = Path(output_dir)

    if not input_path.exists():
        print(f"Error: Input directory '{input_dir}' does not exist.")
        sys.exit(1)

    if not music_path.exists():
        print(f"Error: Music directory '{music_dir}' does not exist.")
        sys.exit(1)

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    final_output_path = base_output_path / timestamp
    final_output_path.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {final_output_path}")

    # Supported extensions
    video_exts = {'.mp4', '.mov', '.avi', '.mkv'}
    audio_exts = {'.mp3', '.wav', '.aac', '.m4a'}

    video_files = sorted([f for f in input_path.iterdir() if f.suffix.lower() in video_exts])
    music_files = sorted([f for f in music_path.iterdir() if f.suffix.lower() in audio_exts])

    if not video_files:
        print(f"No video files found in '{input_dir}'.")
        return

    if not music_files:
        print(f"No music files found in '{music_dir}'.")
        return

    print(f"Found {len(video_files)} videos and {len(music_files)} music tracks.")
    print(f"Generating {len(video_files) * len(music_files)} total videos.")

    for video_path in video_files:
        for music_path in music_files:
            # Construct filename: video_stem + music_stem
            output_filename = f"{video_path.stem}_{music_path.stem}.mp4"
            output_file_path = final_output_path / output_filename

            print(f"Processing: {video_path.name} + {music_path.name} -> {output_filename}")

            # Mix video audio with music at reduced volume (20%) to preserve voiceover
            filter_complex = "[0:a][1:a]amix=inputs=2:duration=first:weights=1 0.2[aout]"

            cmd = [
                'ffmpeg',
                '-y',
                '-i', str(video_path),
                '-i', str(music_path),
                '-filter_complex', filter_complex,
                '-map', '0:v',
                '-map', '[aout]',
                '-c:v', 'copy',
                '-c:a', 'aac',    # Force AAC encoding for compatibility
                '-b:a', '192k',   # High quality audio
                str(output_file_path)
            ]

            try:
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print("  Done.")
            except subprocess.CalledProcessError as e:
                print(f"  Error processing {video_path.name}: {e}")
                print(f"  FFmpeg Error Log:\n{e.stderr.decode()}") # Print explicit error

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add music to videos (Combinatorial).")
    parser.add_argument("--input", required=True, help="Input folder containing videos")
    parser.add_argument("--music_dir", required=True, help="Folder containing music files")
    parser.add_argument("--output", required=True, help="Base output folder")

    args = parser.parse_args()

    add_music(args.input, args.music_dir, args.output)
