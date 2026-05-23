import streamlit as st
import os
import tempfile
import time
from pipeline.audio_extractor import extract_audio
from pipeline.transcriber import transcribe_audio
from pipeline.frame_extractor import extract_frames
from pipeline.ocr_engine import extract_text_from_frames
from pipeline.diagram_detector import detect_diagrams
from pipeline.image_captioner import describe_diagrams
from pipeline.context_merger import merge_context
from pipeline.notes_generator import generate_notes
from utils.pdf_exporter import export_to_pdf
from utils.flashcard_generator import generate_flashcards

# ─────────────────────────────────────────────
#  Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Lecture to Smart Notes AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        text-align: center;
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .step-box {
        background: #f8fafc;
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background: #f0fdf4;
        border: 1px solid #86efac;
        border-radius: 10px;
        padding: 1.5rem;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/graduation-cap.png", width=80)
    st.title("⚙️ Settings")

    gemini_key = "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"

    st.subheader("📹 Video Settings")
    frame_interval = st.slider("Frame Capture Interval (seconds)", 3, 15, 5,
                               help="How often to capture frames from video")
    whisper_model = st.selectbox("Whisper Model Size",
                                 ["tiny", "base", "small", "medium"],
                                 index=1,
                                 help="Larger = more accurate but slower")

    st.subheader("📝 Notes Settings")
    note_language = st.selectbox("Output Language",
                                 ["English", "Hindi", "Tamil", "Telugu"])
    include_flashcards = st.checkbox("Generate Flashcards", value=True)
    include_exam_questions = st.checkbox("Generate Exam Questions", value=True)
    include_summary = st.checkbox("Include Summary", value=True)

    st.divider()
    st.caption("Built with ❤️ using Whisper, Tesseract, YOLOv8 & Groq")

# ─────────────────────────────────────────────
#  Main UI
# ─────────────────────────────────────────────
st.markdown('<h1 class="main-header">🎓 Lecture to Smart Notes AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Upload any college lecture video → Get structured, intelligent notes instantly</p>',
            unsafe_allow_html=True)

# Pipeline steps display
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="step-box">🎥 <b>Step 1</b><br>Upload Video</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="step-box">🎤 <b>Step 2</b><br>Transcribe Audio</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="step-box">👁️ <b>Step 3</b><br>Analyze Frames</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="step-box">📝 <b>Step 4</b><br>Generate Notes</div>', unsafe_allow_html=True)

st.divider()

# Upload Section
uploaded_file = st.file_uploader(
    "📁 Upload Lecture Video",
    type=["mp4", "mkv", "avi", "mov", "webm"],
    help="Supports MP4, MKV, AVI, MOV, WEBM formats"
)

if uploaded_file:
    st.video(uploaded_file)

    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("📄 File Name", uploaded_file.name[:20] + "...")
    with col_info2:
        size_mb = uploaded_file.size / (1024 * 1024)
        st.metric("📦 File Size", f"{size_mb:.1f} MB")
    with col_info3:
        st.metric("🎞️ Format", uploaded_file.type.split("/")[-1].upper())

    st.divider()

    if st.button("🚀 Generate Smart Notes", type="primary", use_container_width=True):

            # Save uploaded file to temp directory
            with tempfile.TemporaryDirectory() as tmpdir:
                video_path = os.path.join(tmpdir, uploaded_file.name)
                with open(video_path, "wb") as f:
                    f.write(uploaded_file.read())

                # ── Progress tracking ──
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    # Step 1: Extract Audio
                    status_text.markdown("🎵 **Extracting audio from video...**")
                    audio_path = extract_audio(video_path, tmpdir)
                    progress_bar.progress(15)
                    time.sleep(0.3)

                    # Step 2: Transcribe
                    status_text.markdown("🎤 **Transcribing lecture audio with Whisper...**")
                    transcript, segments = transcribe_audio(audio_path, model_size=whisper_model)
                    progress_bar.progress(35)
                    time.sleep(0.3)

                    # Step 3: Extract Frames
                    status_text.markdown("🖼️ **Extracting key frames from video...**")
                    frames_dir = os.path.join(tmpdir, "frames")
                    os.makedirs(frames_dir, exist_ok=True)
                    frame_count = extract_frames(video_path, frames_dir, interval=frame_interval)
                    progress_bar.progress(50)
                    time.sleep(0.3)

                    # Step 4: OCR on Frames
                    status_text.markdown("🔍 **Reading board/slide text with OCR...**")
                    frame_texts = extract_text_from_frames(frames_dir, frame_count)
                    progress_bar.progress(65)
                    time.sleep(0.3)

                    # Step 5: Diagram Detection + Description
                    status_text.markdown("📊 **Detecting and describing diagrams...**")
                    diagram_frames = detect_diagrams(frames_dir, frame_count)
                    diagram_descriptions = describe_diagrams(diagram_frames, frames_dir)
                    progress_bar.progress(80)
                    time.sleep(0.3)

                    # Step 6: Merge Context
                    status_text.markdown("🔗 **Merging all content streams...**")
                    merged = merge_context(segments, frame_texts, diagram_descriptions, frame_interval)
                    progress_bar.progress(88)
                    time.sleep(0.3)

                    # Step 7: Generate Notes
                    status_text.markdown("🤖 **Generating smart notes with Groq AI...**")
                    notes_markdown, metadata = generate_notes(
                        merged, gemini_key,
                        language=note_language,
                        include_exam_q=include_exam_questions,
                        include_summary=include_summary
                    )
                    progress_bar.progress(95)
                    time.sleep(0.3)

                    # Step 8: Flashcards
                    flashcards = []
                    if include_flashcards:
                        status_text.markdown("🃏 **Generating flashcards...**")
                        flashcards = generate_flashcards(notes_markdown, gemini_key)

                    progress_bar.progress(100)
                    status_text.markdown("✅ **All done! Notes generated successfully!**")
                    time.sleep(0.5)
                    status_text.empty()
                    progress_bar.empty()

                    # ── Display Results ──
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.success("🎉 Smart Notes Generated Successfully!")

                    # Stats
                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        st.metric("🎤 Words Transcribed", metadata.get("word_count", "N/A"))
                    with m2:
                        st.metric("🖼️ Frames Analyzed", frame_count)
                    with m3:
                        st.metric("📊 Diagrams Found", len(diagram_frames))
                    with m4:
                        st.metric("📝 Notes Length", f"{len(notes_markdown.split())} words")
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.divider()

                    # Tabs for different outputs
                    tab1, tab2, tab3, tab4 = st.tabs(["📝 Smart Notes", "🃏 Flashcards", "🎤 Transcript", "📊 Diagrams"])

                    with tab1:
                        st.markdown(notes_markdown)
                        pdf_bytes = export_to_pdf(notes_markdown, uploaded_file.name)
                        st.download_button(
                            label="📥 Download Notes as PDF",
                            data=pdf_bytes,
                            file_name=f"notes_{uploaded_file.name.split('.')[0]}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )

                    with tab2:
                        if flashcards:
                            for i, card in enumerate(flashcards, 1):
                                with st.expander(f"🃏 Card {i}: {card.get('question', 'Question')}"):
                                    st.markdown(f"**Answer:** {card.get('answer', 'N/A')}")
                                    st.markdown(f"*Topic: {card.get('topic', 'General')}*")
                        else:
                            st.info("Enable flashcards in sidebar settings")

                    with tab3:
                        st.subheader("📜 Full Transcript")
                        st.text_area("Transcript", transcript, height=400)
                        st.download_button(
                            "📥 Download Transcript",
                            data=transcript,
                            file_name="transcript.txt"
                        )

                    with tab4:
                        st.subheader("📊 Detected Diagrams")
                        if diagram_frames:
                            for frame_idx, desc in diagram_descriptions.items():
                                st.markdown(f"**Frame {frame_idx} (~{frame_idx * frame_interval}s):** {desc}")
                        else:
                            st.info("No diagrams detected in this video")

                except Exception as e:
                    st.error(f"❌ Error during processing: {str(e)}")
                    st.exception(e)

else:
    # Demo / Instructions
    st.markdown("""
    ### 📖 How to Use
    1. **Add your Groq API Key** in the sidebar (free at makersuite.google.com)
    2. **Upload a lecture video** (MP4, MKV, AVI supported)
    3. **Click Generate Smart Notes**
    4. **Download your PDF notes** with one click!

    ### 🌟 What You Get
    - ✅ Full structured notes with headings & concepts
    - ✅ All board/slide text captured via OCR
    - ✅ Diagrams detected and described in text
    - ✅ Auto-generated flashcards for revision
    - ✅ Possible exam questions
    - ✅ Downloadable PDF
    - ✅ Full transcript with timestamps

    ### 🎯 Best For
    - College lecture recordings
    - NPTEL / MIT OpenCourseWare videos
    - Zoom/Teams recorded classes
    - YouTube educational videos (download with yt-dlp)
    """)
