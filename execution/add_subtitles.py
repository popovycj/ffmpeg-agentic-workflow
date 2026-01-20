import argparse
import subprocess
import os
import sys
from pathlib import Path

def add_subtitles(input_path_str, subtitle_file, output_dir, style_name='clean_white'):
    """
    Burns subtitles into videos.
    Applies the SAME subtitle file to all videos in input_path (file or directory).
    """
    input_item = Path(input_path_str)
    sub_path = Path(subtitle_file)
    output_path = Path(output_dir)

    if not input_item.exists():
        print(f"Error: Input '{input_path_str}' does not exist.")
        sys.exit(1)

    if not sub_path.exists():
        print(f"Error: Subtitle file '{subtitle_file}' does not exist.")
        sys.exit(1)

    output_path.mkdir(parents=True, exist_ok=True)

    # Supported extensions
    extensions = {'.mp4', '.mov', '.avi', '.mkv'}

    if input_item.is_file():
        if input_item.suffix.lower() in extensions:
            files = [input_item]
        else:
            print(f"Error: Input file '{input_item.name}' is not a supported video format.")
            return
    else:
        # It's a directory
        files = [f for f in input_item.iterdir() if f.suffix.lower() in extensions]

    if not files:
        print(f"No video files found in '{input_path_str}'.")
        return

    print(f"Found {len(files)} videos. Applying subtitles from '{sub_path.name}'.")

    for file_path in files:
        output_filename = f"{file_path.stem}_subbed{file_path.suffix}"
        output_file_path = output_path / output_filename

        print(f"Processing: {file_path.name} -> {output_filename}")

        # FFmpeg filter for subtitles
        # Note: escape path for FFmpeg filter if needed, though simple paths usually work.
        # Best practice is to use relative path or escape special chars.
        # For simplicity in this script, we'll try absolute path key-value.
        # However, FFmpeg's subtitles filter handles paths tricky on Windows,
        # but on Mac absolute paths usually work if no special chars.

        # We need to escape colons and backslashes in the path for the filter string
        # But for Mac (Unix), just ensuring it's a string is usually enough unless it has : inside the path (rare in normal paths compared to Windows drive letters)
        escaped_sub_path = str(sub_path).replace(":", "\\:")

        # Style Definitions
        # ASS/SSA formatting tags:
        # Fontname, Fontsize, PrimaryColour (BBGGRR), SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut,
        # ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding

        styles = {
            'clean_white': "Fontsize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1,Shadow=1,MarginV=30",
            'highlight_yellow': "Fontname=Arial,Fontsize=26,PrimaryColour=&H0000FFFF,BackColour=&H80000000,BorderStyle=3,Outline=0,Shadow=0,MarginV=50,Bold=1",
            'bold_red': "Fontname=Impact,Fontsize=15,PrimaryColour=&H000000FF,OutlineColour=&H00FFFFFF,BorderStyle=1,Outline=2,Shadow=0,Alignment=5"
        }

        selected_style = styles.get(style_name)
        if not selected_style:
             print(f"Warning: Style '{style_name}' not found. Using 'clean_white'.")
             selected_style = styles['clean_white']

        filter_complex = f"subtitles='{escaped_sub_path}':force_style='{selected_style}'"

        cmd = [
            'ffmpeg',
            '-y',
            '-i', str(file_path),
            '-vf', filter_complex,
            '-c:a', 'copy',
            str(output_file_path)
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("  Done.")
        except subprocess.CalledProcessError as e:
            print(f"  Error processing {file_path.name}: {e}")
            print(f"  FFmpeg Error: {e.stderr.decode()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Burn subtitles into videos.")
    parser.add_argument("--input", required=True, help="Input folder containing videos OR single video file")
    parser.add_argument("--subtitles", required=True, help="Path to .srt file")
    parser.add_argument("--output", required=True, help="Output folder")

    parser.add_argument("--style", default="clean_white", help="Caption style: clean_white (default), highlight_yellow, bold_red")

    args = parser.parse_args()

    add_subtitles(args.input, args.subtitles, args.output, args.style)
