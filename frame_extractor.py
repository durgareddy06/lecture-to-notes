import cv2
import os

def extract_frames(video_path: str, frames_dir: str, interval: int = 5) -> int:
    """Extract frames from video every `interval` seconds."""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 25

    frame_interval = int(fps * interval)
    frame_count = 0
    saved = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            frame_path = os.path.join(frames_dir, f"frame_{saved:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            saved += 1
        frame_count += 1

    cap.release()
    return saved
