import argparse
import json
import sys
from pathlib import Path

def generate_srt(audio_file, output_srt):
    """
    Generates SRT file from ElevenLabs alignment JSON sidecar.
    """
    audio_path = Path(audio_file)
    json_path = audio_path.with_suffix(".json")

    if not json_path.exists():
        print(f"Warning: Alignment file '{json_path}' not found. Generating estimated SRT from audio duration (fallback).")
        # Fallback: Create a single subtitle line for the whole duration (or split blindly)
        # We need audio duration. Use ffprobe or just guess/read if possible.
        # Since we don't have python-ffmpeg installed easily, we'll try to run ffprobe.
        import subprocess
        try:
             result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
             duration = float(result.stdout.strip())
        except Exception as e:
             print(f"Error getting duration: {e}. Defaulting to 10s.")
             duration = 10.0

        # Create a simple SRT with one block
        with open(output_srt, 'w', encoding='utf-8') as f:
            s = format_time(0)
            e = format_time(duration)
            f.write(f"1\n{s} --> {e}\n(Voiceover Caption)\n\n")
        print(f"SRT generated (Fallback): {output_srt}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        alignment = json.load(f)

    # ElevenLabs alignment format:
    # {
    #   "characters": ["H", "e", "l", "l", "o", " "],
    #   "character_start_times_seconds": [0.0, 0.05, ...],
    #   "character_end_times_seconds": [0.05, 0.1, ...]
    # }

    chars = alignment.get("characters", [])
    starts = alignment.get("character_start_times_seconds", [])
    ends = alignment.get("character_end_times_seconds", [])

    words = []
    current_word = ""
    word_start = 0.0
    word_end = 0.0

    # Simple word grouping logic
    if chars:
         word_start = starts[0]

    for i, char in enumerate(chars):
        current_word += char

        # Word end detection (space)
        if char == " " or i == len(chars) - 1:
            word_end = ends[i]
            if current_word.strip():
                 words.append({
                    "text": current_word.strip(),
                    "start": word_start,
                    "end": word_end
                 })
            current_word = ""
            if i < len(chars) - 1:
                word_start = starts[i+1]

    # SRT Line Grouping (simplified)
    subtitles = []
    current_line = []
    current_line_char_count = 0
    line_start = 0.0

    for i, word in enumerate(words):
        if not current_line:
            line_start = word['start']

        current_line.append(word)
        current_line_char_count += len(word['text']) + 1

        # "Finite" captions: Shorter segments for punchy feel.
        # Max chars ~15-20 suitable for vertical video / shorts.
        is_end_of_sentence = word['text'].endswith(('.', '!', '?', ','))
        if current_line_char_count > 20 or is_end_of_sentence or i == len(words) - 1:
            line_end = word['end']
            line_text = " ".join([w['text'] for w in current_line])

            subtitles.append({
                "start": line_start,
                "end": line_end,
                "text": line_text
            })
            current_line = []
            current_line_char_count = 0
            if i < len(words) - 1:
                # Next line starts at the next word's start
                # (handled by line_start assignment at loop start)
                pass

    # Write SRT
    with open(output_srt, 'w', encoding='utf-8') as f:
        for i, sub in enumerate(subtitles, 1):
            s = format_time(sub['start'])
            e = format_time(sub['end'])
            f.write(f"{i}\n{s} --> {e}\n{sub['text']}\n\n")

    print(f"SRT generated: {output_srt}")

def format_time(seconds):
    # HH:MM:SS,mmm
    millis = int((seconds % 1) * 1000)
    seconds = int(seconds)
    minutes = (seconds // 60) % 60
    hours = (seconds // 3600)
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate SRT from TTS alignment JSON.")
    parser.add_argument("--audio", required=True, help="Input audio file (expects .json sidecar)")
    parser.add_argument("--output", required=True, help="Output SRT file")

    args = parser.parse_args()
    generate_srt(args.audio, args.output)
