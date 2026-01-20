# Assemble Video Sequence

## Goal
Combine disjoint video clips into a single continuous video sequence: **Hook -> Body -> Packshot**.
Generates **all possible combinations** of clips found in the respective folders.

- **Sequence**:
  1.  **Hook**: Standard cut.
  2.  **Body**: Standard cut from Hook.
  3.  **Packshot**: **Overlaps** the end of the Body clip by 0.5 seconds (Crossfade transition).

## Inputs
- **Hook Folder**: Directory of "Hook" clips.
- **Body Folder**: Directory of "Body" clips.
- **Packshot Folder**: Directory of "Packshot" clips.
- **Output Folder**: Destination for assembled videos.

## Processing Logical Steps
1.  **Combinatorial Generation**: Iterates Hook x Body x Packshot.
2.  **Concatenation**: Hook + Body are concatenated normally.
3.  **Transition**: Packshot starts playing 0.5 seconds *before* the Body clip ends, creating a smooth overlap/crossfade.
4.  **Save**: Files saved in `Output Folder / YYYY-MM-DD_HH-MM-SS /` to prevent overwriting.

## Execution Tool
- **Script**: `execution/assemble_video.py`
- **Usage**:
  ```bash
  python3 execution/assemble_video.py --hook_dir <hook_path> --body_dir <body_path> --packshot_dir <packshot_path> --output <output_path>
  ```

## Outputs
- Assembled video files (e.g., `hook1_body2_pack1.mp4`).
