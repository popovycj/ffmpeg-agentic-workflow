import argparse
import subprocess
import os
import sys
import json
from pathlib import Path
from datetime import datetime

def get_video_info(file_path):
    """Returns duration, width, height, and has_audio using ffprobe."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'stream=width,height,codec_type',
        '-show_entries', 'format=duration',
        '-of', 'json',
        str(file_path)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        duration = float(data.get('format', {}).get('duration', 0))

        width = 1080
        height = 1080
        has_audio = False

        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video' and 'width' in stream:
                width = int(stream['width'])
                height = int(stream['height'])
            if stream.get('codec_type') == 'audio':
                has_audio = True

        return duration, width, height, has_audio
    except Exception as e:
        print(f"Error getting info for {file_path}: {e}")
        return 0.0, 1080, 1080, False

def assemble_videos(hook_dir, body_dir, packshot_dir, output_dir):
    """
    Assembles videos: Hook -> Body -> Packshot.
    Packshot overlaps Body by 0.5s.
    Generates all combinations.
    """
    hook_path = Path(hook_dir)
    body_path = Path(body_dir)
    packshot_path = Path(packshot_dir)

    # Validate inputs
    for p in [hook_path, body_path, packshot_path]:
        if not p.exists():
            print(f"Error: Directory '{p}' does not exist.")
            sys.exit(1)

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    final_output_path = Path(output_dir) / timestamp
    final_output_path.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {final_output_path}")

    # Supported extensions
    exts = {'.mp4', '.mov', '.avi', '.mkv'}

    hooks = sorted([f for f in hook_path.iterdir() if f.suffix.lower() in exts])
    bodies = sorted([f for f in body_path.iterdir() if f.suffix.lower() in exts])
    packshots = sorted([f for f in packshot_path.iterdir() if f.suffix.lower() in exts])

    if not hooks or not bodies or not packshots:
        print("Error: One or more input directories are empty.")
        return

    print(f"Found {len(hooks)} hooks, {len(bodies)} bodies, {len(packshots)} packshots.")

    # Get reference dimensions
    _, ref_w, ref_h, _ = get_video_info(hooks[0])
    print(f"Standardizing to resolution: {ref_w}x{ref_h}")

    count = 0
    for hook in hooks:
        hook_dur, _, _, hook_has_audio = get_video_info(hook)
        if hook_dur <= 0:
            print(f"Skipping {hook.name}: Invalid duration ({hook_dur})")
            continue

        for body in bodies:
            body_dur, _, _, body_has_audio = get_video_info(body)
            if body_dur <= 0:
                print(f"Skipping {body.name}: Invalid duration ({body_dur})")
                continue

            for packshot in packshots:
                # Packshot check
                # Note: Packshot might not have audio, so we check.
                p_dur, _, _, pack_has_audio = get_video_info(packshot)

                count += 1
                output_filename = f"{hook.stem}_{body.stem}_{packshot.stem}.mp4"
                output_file_path = final_output_path / output_filename

                print(f"[{count}] Assembling: {output_filename}")

                # Offset for xfade = (Hook + Body) - 0.5s overlap
                offset = hook_dur + body_dur - 0.5

                if offset < 0:
                     print(f"  Error: Combined length of Hook+Body ({hook_dur + body_dur}s) < 0.5s overlap. Skipping.")
                     continue

                # Input normalization filters
                # We standardize all video inputs to match the first hook's resolution and pixel format.
                norm_filters = f"scale={ref_w}:{ref_h}:force_original_aspect_ratio=decrease,pad={ref_w}:{ref_h}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p"

                # Audio handling: use stream if exists, else generate silence

                # Hook Audio
                if hook_has_audio:
                    a0 = "[0:a]"
                    filt_a0 = ""
                else:
                    a0 = "[a0]"
                    filt_a0 = f"anullsrc=channel_layout=stereo:sample_rate=44100:d={hook_dur}[a0];"

                # Body Audio
                if body_has_audio:
                    a1 = "[1:a]"
                    filt_a1 = ""
                else:
                    a1 = "[a1]"
                    filt_a1 = f"anullsrc=channel_layout=stereo:sample_rate=44100:d={body_dur}[a1];"

                # Packshot Audio
                if pack_has_audio:
                    a2 = "[2:a]"
                    filt_a2 = ""
                else:
                    a2 = "[a2]"
                    filt_a2 = f"anullsrc=channel_layout=stereo:sample_rate=44100:d={p_dur}[a2];"

                # Filter Complex Construction
                filter_complex = (
                    f"{filt_a0}{filt_a1}{filt_a2}"
                    f"[0:v]{norm_filters}[v0];"
                    f"[1:v]{norm_filters}[v1];"
                    f"[2:v]{norm_filters}[v2];"
                    f"[v0]{a0}[v1]{a1}concat=n=2:v=1:a=1[hb_v][hb_a];"
                    f"[hb_v]settb=AVTB[hb_v_tb];"
                    f"[v2]settb=AVTB[v2_tb];"
                    f"[hb_v_tb][v2_tb]xfade=transition=fade:duration=0.5:offset={offset}[v];"
                    f"[hb_a]{a2}acrossfade=d=0.5[a]"
                )

                cmd = [
                    'ffmpeg',
                    '-y',
                    '-i', str(hook),
                    '-i', str(body),
                    '-i', str(packshot),
                    '-filter_complex', filter_complex,
                    '-map', '[v]',
                    '-map', '[a]',
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    str(output_file_path)
                ]

                try:
                    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except subprocess.CalledProcessError as e:
                    print(f"Error processing {output_filename}: {e}")
                    print(f"FFmpeg Error: {e.stderr.decode()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assemble videos (Hook -> Body -> Packshot) with overlap.")
    parser.add_argument("--hook_dir", required=True, help="Folder containing hooks")
    parser.add_argument("--body_dir", required=True, help="Folder containing bodies")
    parser.add_argument("--packshot_dir", required=True, help="Folder containing packshots")
    parser.add_argument("--output", required=True, help="Output folder")

    args = parser.parse_args()

    assemble_videos(args.hook_dir, args.body_dir, args.packshot_dir, args.output)
