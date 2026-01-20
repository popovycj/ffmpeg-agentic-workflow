# Add Music to Video

## Goal
Add a background music track to a batch of videos. The tool generates **ALL combinations** of videos and music tracks (Video A + Music 1, Video A + Music 2, Video B + Music 1, etc.).

- **Music Selection**: Combinatorial (Cartesian Product). Every audio file is applied to every video file.
- **Duration**: The music is automatically cropped to match the length of the video.
- **Organization**: Results are saved in a **timestamped subfolder** within the Output Folder to separate different runs.

## Inputs
- **Input Folder**: Directory containing source video files.
- **Music Folder**: Directory containing music files (`.mp3`, `.wav`, etc.).
- **Output Folder**: Base directory where processed subfolders will be created.

## Processing Logical Steps
1.  **Playlist Generation**: List all music files in the music folder.
2.  **Combinatorial Loop**: Iterate through every video and every music track.
3.  **Unique Filename**: Output file is named `{video_name}_{music_name}.mp4`.
4.  **Audio Replacement**: Replace video audio with assigned music track.
5.  **Duration Match**: Crop music to video length (`-shortest`).
6.  **Save**: Write to `Output Folder / YYYY-MM-DD_HH-MM-SS /`.

## Execution Tool
- **Script**: `execution/add_music.py`
- **Usage**:
  ```bash
  python3 execution/add_music.py --input <video_folder> --music_dir <music_folder> --output <output_base>
  ```

## Outputs
- Processed video files saved in a **timestamped subfolder** (e.g., `Output Folder/2026-01-20_19-30-00/`).
- This separation ensures multiple runs do not overwrite each other.
