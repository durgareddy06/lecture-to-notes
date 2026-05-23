import whisper

def transcribe_audio(audio_path: str, model_size: str = "base"):
    """Transcribe audio using OpenAI Whisper."""
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, verbose=False)

    transcript = result["text"].strip()
    segments = result.get("segments", [])

    word_count = len(transcript.split())
    metadata = {"word_count": word_count}

    return transcript, segments
