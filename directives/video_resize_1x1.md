# Video Resize Workflow (9:16 to 1:1)

## Goal
Resize vertical (9:16) videos to square (1:1) format suitable for social media feeds. The output video retains the original full vertical content in the center, with a blurred, scaled version of the video filling the background to cover the 1:1 aspect ratio.

## Inputs
- **Input Folder**: Directory containing source video files (`.mp4`, `.mov`, etc.)
- **Output Folder**: Directory where processed videos will be saved.

## Processing Logical Steps
1. **Background Layer**:
   - Scale original video to Cover the target 1:1 square.
   - Crop to exact 1:1.
   - Apply blur effect.
2. **Foreground Layer**:
   - Scale original video to Fit within the target 1:1 square (maintaining aspect ratio).
3. **Compositing**:
   - Overlay Foreground on top of Background, centered.

## Execution Tool
- **Script**: `execution/resize_video_1x1.py`
- **Usage**:
  ```bash
  python3 execution/resize_video_1x1.py --input <input_path> --output <output_path>
  ```
- **Optional Arguments**:
  - `--size <int>`: Set output dimension (default 1080 for 1080x1080).

## Outputs
- Processed video files renamed with `_1x1` suffix in the Output Folder.
- Audio is copied from source.
