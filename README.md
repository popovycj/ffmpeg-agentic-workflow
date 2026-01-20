# FFmpeg Video Processing Agent

An intelligent video processing pipeline that automates content creation workflows using FFmpeg, ElevenLabs TTS, and AI orchestration.

## Features

- 🎙️ **Text-to-Speech**: Convert scripts to voiceover using ElevenLabs API with word-level timestamps
- 📝 **Auto-Captions**: Generate SRT subtitles from TTS alignment data
- 🎬 **Video Assembly**: Combine hook, body, and packshot clips with crossfade transitions
- 🔊 **Voiceover Overlay**: Apply voiceover audio to assembled videos
- 📺 **Subtitle Burning**: Burn captions directly into video with customizable styles
- 🎵 **Music Mixing**: Add background music at configurable volume levels
- 📐 **Resize/Reformat**: Convert videos to 1:1 (square) format with blurred background

## Quick Start

### Prerequisites

- Python 3.8+
- FFmpeg installed and in PATH
- ElevenLabs API key

### Installation

```bash
# Clone repository
git clone <repo-url>
cd ffmpeg_agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install requests

# Configure environment
cp .env.example .env
# Edit .env and add your ELEVENLABS_API_KEY
```

### Environment Variables

Create a `.env` file with:

```
ELEVENLABS_API_KEY=your_api_key_here
```

## Directory Structure

```
ffmpeg_agent/
├── execution/           # Deterministic Python scripts
│   ├── text_to_speech.py
│   ├── transcribe_audio.py
│   ├── assemble_video.py
│   ├── apply_voiceover.py
│   ├── add_subtitles.py
│   ├── add_music.py
│   └── resize_video_1x1.py
├── directives/          # SOPs for AI orchestration
├── input/               # Source files (gitignored)
│   ├── text/           # Script files for TTS
│   ├── videos/         # Video clips (hook/, body/, packshot/)
│   └── music/          # Background music tracks
├── output/              # Generated files (gitignored)
├── .agent/workflows/    # Automated workflow definitions
└── AGENTS.md           # AI agent instructions
```

## Execution Scripts

### 1. Text to Speech
```bash
python execution/text_to_speech.py \
  --input input/text/script.txt \
  --output output/tts \
  --voice_id <optional_voice_id>
```
Generates MP3 audio and JSON timing data for subtitle generation.

### 2. Transcribe Audio (Generate SRT)
```bash
python execution/transcribe_audio.py \
  --audio output/tts/script.mp3 \
  --output output/tts/script.srt
```
Creates SRT subtitles from ElevenLabs timing data with ~20 char line segments.

### 3. Assemble Video
```bash
python execution/assemble_video.py \
  --hook_dir input/videos/hook \
  --body_dir input/videos/body \
  --packshot_dir input/videos/packshot \
  --output output/assembled
```
Generates all combinations with 0.5s crossfade between body and packshot.

### 4. Apply Voiceover
```bash
python execution/apply_voiceover.py \
  --video input.mp4 \
  --audio voiceover.mp3 \
  --output output.mp4
```
Replaces video audio with voiceover, preserving full video duration.

### 5. Add Subtitles
```bash
python execution/add_subtitles.py \
  --input output/voiceover \
  --subtitles output/tts/script.srt \
  --output output/captioned \
  --style clean_white
```
Available styles: `clean_white`, `highlight_yellow`, `bold_red`

### 6. Add Music
```bash
python execution/add_music.py \
  --input output/captioned \
  --music_dir input/music \
  --output output/with_music
```
Mixes music at 20% volume under voiceover. Generates all video × music combinations.

### 7. Resize to 1:1
```bash
python execution/resize_video_1x1.py \
  --input output/with_music \
  --output output/final \
  --size 1080
```
Converts to square format with blurred background fill.

## Full Pipeline Workflow

The complete pipeline can be run via the AI agent using:

```
/workflows:run
```

This executes all 7 steps in sequence:
1. TTS → 2. Captions → 3. Assemble → 4. Voiceover → 5. Subtitles → 6. Music → 7. Resize

### Example Output
- **Input**: 2 hooks × 2 bodies × 1 packshot × 2 music tracks
- **Output**: 8 final videos (1080×1080, ~20s each)

## Architecture

This project follows a **3-layer architecture**:

| Layer | Purpose | Location |
|-------|---------|----------|
| **Directive** | SOPs defining what to do | `directives/` |
| **Orchestration** | AI decision-making | AI agent |
| **Execution** | Deterministic scripts | `execution/` |

See [AGENTS.md](AGENTS.md) for detailed AI orchestration instructions.

## Supported Formats

- **Video**: MP4, MOV, AVI, MKV
- **Audio**: MP3, WAV, AAC, M4A
- **Subtitles**: SRT

## License

MIT
