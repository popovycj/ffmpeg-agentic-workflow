import argparse
import subprocess
import os
import sys
from pathlib import Path

def process_videos(input_dir, output_dir, size=1080):
    """
    Resizes videos from input_dir to 1:1 format with blurred background
    and saves them to output_dir.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.exists():
        print(f"Error: Input directory '{input_dir}' does not exist.")
        sys.exit(1)

    output_path.mkdir(parents=True, exist_ok=True)

    # Supported extensions
    extensions = {'.mp4', '.mov', '.avi', '.mkv'}

    files = [f for f in input_path.iterdir() if f.suffix.lower() in extensions]

    if not files:
        print(f"No video files found in '{input_dir}'.")
        return

    print(f"Found {len(files)} videos to process.")

    for file_path in files:
        output_filename = f"{file_path.stem}_1x1{file_path.suffix}"
        output_file_path = output_path / output_filename

        print(f"Processing: {file_path.name} -> {output_filename}")

        # FFmpeg filter complex
        # 1. Background: Scale to cover 1:1, crop to 1:1, blur
        # 2. Foreground: Scale to fit 1:1
        # 3. Overlay Foreground on Background

        filter_complex = (
            f"[0:v]scale={size}:{size}:force_original_aspect_ratio=increase,crop={size}:{size},boxblur=40[bg];"
            f"[0:v]scale={size}:{size}:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2"
        )

        cmd = [
            'ffmpeg',
            '-y', # Overwrite output
            '-i', str(file_path),
            '-filter_complex', filter_complex,
            '-c:a', 'copy', # Copy audio
            str(output_file_path)
        ]

        try:
            # Run ffmpeg, suppress verbose output
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("  Done.")
        except subprocess.CalledProcessError as e:
            print(f"  Error processing {file_path.name}: {e}")
            # print(e.stderr.decode()) # Uncomment for debug

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resize videos to 1:1 with blurred background.")
    parser.add_argument("--input", required=True, help="Input folder containing videos")
    parser.add_argument("--output", required=True, help="Output folder for processed videos")
    parser.add_argument("--size", type=int, default=1080, help="Output dimension (square size). Default 1080.")

    args = parser.parse_args()

    process_videos(args.input, args.output, args.size)
