# Virtual Juggler

A real-time virtual juggling experience using your webcam, MediaPipe hand tracking, and OpenCV.

![Demo](demo.gif)

## How It Works

The app captures your webcam feed and uses **MediaPipe** to track your hands in real time. A virtual ball obeys physics (gravity, bouncing, wall collisions). When your fingertip moves upward into the ball's proximity, it launches the ball as if you hit it. Keep it in the air as long as you can; each successful hit adds to your score.

The frame is mirrored, so it feels like looking in a mirror. Holding a peace sign ✌ for ~2 seconds triggers a graceful exit.

## Setup

**Python 3.8+ recommended.**

1. Clone or download this project.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running

```bash
python main.py
```

A window titled **Virtual Juggler** will open, showing your webcam feed with the virtual ball overlaid.

## Controls

| Action | Effect |
|--------|--------|
| Move hand upward into the ball | Hit the ball upward |
| Ball hits floor/walls | Bounces with damping |
| Hold open palm (all 5 fingers extended) for ~2 seconds | Exit the app |
| Press `q` | Exit immediately |

## Configuration

All tunable constants live in [config.py](config.py):

| Constant | Default | Description |
|----------|---------|-------------|
| `GRAVITY` | `0.5` | Downward acceleration (pixels/frame²) |
| `BALL_RADIUS` | `20` | Ball size in pixels |
| `BALL_COLOR` | `(0, 200, 255)` | Ball color (BGR: orange-ish) |
| `BOUNCE_DAMPING` | `0.75` | Energy retained on bounce |
| `HIT_DISTANCE` | `60` | Pixel radius to trigger a hit |
| `HIT_VELOCITY` | `-18` | Upward velocity applied on hit |
| `EXIT_GESTURE_FRAMES` | `60` | Frames (~2s) open palm must be held |
| `CAMERA_INDEX` | `0` | Webcam device index |

## Project Structure

```
virtual-juggler/
├── main.py             # Entry point — main loop
├── hand_tracker.py     # MediaPipe hand tracking
├── ball_physics.py     # Ball simulation (gravity, bounce, hit detection)
├── gesture_detector.py # Open-palm exit gesture recognition
├── renderer.py         # OpenCV drawing (ball, trail, UI overlay)
├── config.py           # Tunable constants
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Requirements

- Python 3.8+
- Webcam
- `opencv-python`
- `mediapipe`
- `numpy`
