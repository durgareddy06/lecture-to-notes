import os

def describe_diagrams(diagram_frames: list, frames_dir: str) -> dict:
    """
    Describe diagram frames.
    BLIP-2 skipped (too heavy). Returns basic frame info.
    Groq vision can be plugged in here later.
    """
    descriptions = {}

    for i in diagram_frames:
        frame_path = os.path.join(frames_dir, f"frame_{i:04d}.jpg")
        if os.path.exists(frame_path):
            descriptions[i] = f"[Visual content detected at frame {i}]"

    return descriptions
