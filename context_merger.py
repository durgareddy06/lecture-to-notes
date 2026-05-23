def merge_context(segments: list, frame_texts: dict, diagram_descriptions: dict, frame_interval: int) -> str:
    """
    Merge transcript segments with OCR text and diagram descriptions
    using timestamp alignment.
    """
    merged_parts = []

    for seg in segments:
        start = seg.get("start", 0)
        text = seg.get("text", "").strip()
        if text:
            merged_parts.append(f"[{start:.1f}s] {text}")

        # Match frame index to this timestamp
        frame_idx = int(start // frame_interval)

        if frame_idx in frame_texts:
            merged_parts.append(f"  [Slide/Board Text @ {start:.1f}s]: {frame_texts[frame_idx]}")

        if frame_idx in diagram_descriptions:
            merged_parts.append(f"  [Visual @ {start:.1f}s]: {diagram_descriptions[frame_idx]}")

    # If no segments (e.g. tiny model), just dump all frame texts
    if not merged_parts:
        for idx, text in frame_texts.items():
            merged_parts.append(f"[Frame {idx}] {text}")

    return "\n".join(merged_parts)
