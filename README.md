# 🎱 Pool Shot Detector

A real-time computer vision system that watches a pool/billiards match on video and automatically detects **shots** and **ball collisions** — no training data or pre-trained models required. Built entirely with classical CV techniques (color segmentation, contour analysis, and centroid tracking).

## How It Works

The pipeline processes a video frame-by-frame through a modular detection stack:

1. **Frame Extraction** — reads the video stream frame by frame using OpenCV.
2. **Ball Detection** — auto-samples the felt color from the center of the frame (works on green, blue, red tables, etc.), isolates non-felt regions via HSV color segmentation, and filters contours by size/roundness to identify balls.
3. **Ball Tracking** — assigns persistent IDs to detected balls and tracks them across frames using nearest-neighbor distance matching, estimating velocity along the way.
4. **Shot Detection** — identifies the cue ball (largest/most consistently tracked ball) and flags a shot as `STARTED`, `ONGOING`, or `ENDED` based on its speed.
5. **Collision Detection** — checks distances between all tracked balls each frame and flags a collision once they get close enough, with a cooldown to avoid double-counting.
6. **Event State Machine** — combines shot state + collision events into a final verdict per shot: `POINT` or `NO POINT`.
7. **Overlay** — draws bounding circles and the live verdict directly onto the video feed.

## Project Structure

```
Pool detector/
├── main.py                      # Entry point — runs the full detection pipeline
├── config.py                    # Table mask polygon (crop to your table's felt area)
├── normalize_video.py           # Video pre-processing/normalization helper
├── requirements.txt             # Python dependencies
├── data/
│   ├── input_videos/            # Source match footage
│   ├── output_videos/           # Processed output
│   └── logs/                    # Run logs
└── modules/
    ├── frame_extractor.py       # Video → frame stream
    ├── ball_detector.py         # HSV color segmentation + contour filtering
    ├── ball_tracker.py          # Centroid-based multi-object tracking
    ├── shot_detector.py         # Cue ball speed → shot state
    ├── collision_detector.py    # Pairwise distance → collision events
    ├── event_state_machine.py   # Shot state + collisions → POINT / NO POINT
    └── overlay.py                # Draws tracking circles + verdict on frame
```

## Tech Stack

- **Python 3.12**
- **OpenCV** — video I/O, color space conversion, contour detection
- **NumPy** — array/image processing
- **SciPy** — distance computation for ball tracking
- **imageio-ffmpeg** — video handling

## Getting Started

### 1. Clone & install dependencies
```bash
git clone https://github.com/ahsankhattak/pool-shot-detector.git
cd pool-shot-detector
pip install -r requirements.txt
```

### 2. Normalize your input video
`main.py` expects a standardized video at `data/input_videos/standard_input.mp4`. Convert your raw footage first:
```bash
python normalize_video.py
```
This uses ffmpeg to re-encode your match video (`data/input_videos/match1.mp4` by default) into a consistent codec/pixel format that OpenCV reads reliably. Edit `INPUT_VIDEO` / `OUTPUT_VIDEO` in `normalize_video.py` to point to your own files.

### 3. Configure your table region
Edit `config.py` and set `TABLE_MASK_POLYGON` to trace the inner cushion edge of your table (clockwise from top-left). This crops detection to just the playing surface.

### 4. Run it
```bash
python main.py
```
A window will open showing the live video with tracked balls circled and shot verdicts overlaid in real time. Press `q` to quit.

On completion, the console prints a shot-by-shot results log and the total collision score.

## Key Design Choices

- **No training data needed** — detection relies on classical color segmentation rather than a trained model, so it adapts to different table felt colors automatically.
- **Duplicate suppression** — filters out glare/highlight blobs that would otherwise be mistaken for a second ball on the same physical ball.
- **Age-gated collisions** — a ball must be tracked for a minimum number of frames before it's eligible to register a collision, reducing false positives from noisy/short-lived detections.
- **Cooldown-based collision counting** — only the first collision per shot counts toward the verdict, preventing a single contact event from being counted multiple times across frames.

## Future Improvements

- [ ] Pocket detection to track potted balls
- [ ] Support for multiple camera angles
- [ ] Export shot statistics to CSV/dashboard
- [ ] Replace color-segmentation detector with a lightweight trained model for more robust detection under variable lighting

## Author

**Ahsan Javed** — CS student focused on Machine Learning & Computer Vision
[GitHub](https://github.com/ahsankhattak)
