import os
from PIL import Image

def extract_text_from_frames(frames_dir: str, frame_count: int) -> dict:
    """Extract text from frames using pytesseract."""
    try:
        import pytesseract
        use_tesseract = True
    except ImportError:
        use_tesseract = False

    frame_texts = {}

    for i in range(frame_count):
        frame_path = os.path.join(frames_dir, f"frame_{i:04d}.jpg")
        if not os.path.exists(frame_path):
            continue
        try:
            if use_tesseract:
                img = Image.open(frame_path)
                text = pytesseract.image_to_string(img).strip()
                if text:
                    frame_texts[i] = text
        except Exception:
            continue

    return frame_texts
