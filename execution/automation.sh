#!/bin/bash

# Configuration
PROJECT_DIR="/Users/haydamac/agent_workflows/ffmpeg_agent"
INPUT_DIR="$PROJECT_DIR/input/text"
PROCESS_DIR="$PROJECT_DIR/input/processed"
VENV="$PROJECT_DIR/.venv/bin/activate"

cd "$PROJECT_DIR"
source "$VENV"

# Check for new files
files=$(ls "$INPUT_DIR"/*.txt 2>/dev/null)

if [ -z "$files" ]; then
    echo "$(date): No new scripts found in $INPUT_DIR. Skipping... "
    exit 0
fi

for script in $files; do
    filename=$(basename "$script")
    echo "$(date): Starting pipeline for $filename..."

    # 1. TTS
    python execution/text_to_speech.py --input "$script" --output input/voiceovers

    # 2. Dubbing
    python execution/dub_voiceover.py --input "input/voiceovers/${filename%.*}.mp3" --output input/voiceovers --target_lang es
    python execution/dub_voiceover.py --input "input/voiceovers/${filename%.*}.mp3" --output input/voiceovers --target_lang pl
    python execution/dub_voiceover.py --input "input/voiceovers/${filename%.*}.mp3" --output input/voiceovers --target_lang uk

    # 3. Move SRTs
    cp "input/voiceovers/${filename%.*}_es.srt" input/subtitles/
    cp "input/voiceovers/${filename%.*}_pl.srt" input/subtitles/
    cp "input/voiceovers/${filename%.*}_uk.srt" input/subtitles/

    # 4. English SRT
    python execution/transcribe_audio.py --audio "input/voiceovers/${filename%.*}.mp3" --output "input/subtitles/${filename%.*}.srt"

    # 5. Assembly
    # We use a temp folder for assembly to keep clean
    ASSEM_DIR=".tmp/automated_assembly"
    mkdir -p "$ASSEM_DIR"
    python execution/assemble_video.py --hook_dir input/videos/hook --body_dir input/videos/body --packshot_dir input/videos/packshot --output "$ASSEM_DIR"

    # Find newest assembly subdir
    LATEST_ASSEM=$(ls -td "$ASSEM_DIR"/*/ | head -n 1)

    # 6. Apply Voiceover & Subs
    # For en, es, pl, uk
    for lang in en es pl uk; do
        OUT_VOICE=".tmp/voiced/$lang"
        mkdir -p "$OUT_VOICE"

        # Audio/Sub paths
        if [ "$lang" == "en" ]; then
            AUDIO="input/voiceovers/${filename%.*}.mp3"
            SUBS="input/subtitles/${filename%.*}.srt"
        else
            AUDIO="input/voiceovers/${filename%.*}_$lang.mp3"
            SUBS="input/subtitles/${filename%.*}_$lang.srt"
        fi

        for video in "$LATEST_ASSEM"/*.mp4; do
            vbase=$(basename "$video")
            python execution/apply_voiceover.py --video "$video" --audio "$AUDIO" --subtitles "$SUBS" --output "$OUT_VOICE/$vbase"
        done

        # 7. Add Music
        OUT_MUS=".tmp/musical/$lang"
        mkdir -p "$OUT_MUS"
        python execution/add_music.py --input "$OUT_VOICE" --music_dir input/music --output "$OUT_MUS"

        # 8. Resize
        LATEST_MUS=$(ls -td "$OUT_MUS"/*/ | head -n 1)
        mkdir -p "output/final/$lang"
        python execution/resize_video_1x1.py --input "$LATEST_MUS" --output "output/final/$lang"
    done

    # Archive script
    mv "$script" "$PROCESS_DIR/"
    echo "$(date): Finished pipeline for $filename. Script moved to $PROCESS_DIR."

done

echo "$(date): Automation cycle complete."
