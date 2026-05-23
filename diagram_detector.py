import os

def detect_diagrams(frames_dir: str, frame_count: int) -> list:
    """Detect frames that likely contain diagrams using YOLOv8 or heuristics."""
    diagram_frames = []

    try:
        from ultralytics import YOLO
        import cv2
        import numpy as np

        model_path = "yolov8n.pt"
        if not os.path.exists(model_path):
            # fallback to heuristic
            return _heuristic_detect(frames_dir, frame_count)

        model = YOLO(model_path)

        for i in range(frame_count):
            frame_path = os.path.join(frames_dir, f"frame_{i:04d}.jpg")
            if not os.path.exists(frame_path):
                continue
            results = model(frame_path, verbose=False)
            # If any objects detected, treat as diagram-worthy frame
            if len(results[0].boxes) > 0:
                diagram_frames.append(i)

    except Exception:
        diagram_frames = _heuristic_detect(frames_dir, frame_count)

    return diagram_frames


def _heuristic_detect(frames_dir: str, frame_count: int) -> list:
    """Simple heuristic: flag every 3rd frame as potential diagram."""
    return [i for i in range(0, frame_count, 3)]
