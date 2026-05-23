from groq import Groq

def generate_notes(merged_context: str, groq_api_key: str,
                   language: str = "English",
                   include_exam_q: bool = True,
                   include_summary: bool = True) -> tuple:
    """Generate structured notes using Groq LLaMA 3.3 70B."""

    client = Groq(api_key=groq_api_key)

    exam_q_instruction = ""
    if include_exam_q:
        exam_q_instruction = """
## 🎯 Possible Exam Questions
List 5 probable exam questions based on this lecture.
"""

    summary_instruction = ""
    if include_summary:
        summary_instruction = """
## 📌 Summary
A concise 5-line summary of the entire lecture.
"""

    prompt = f"""You are an expert academic note-taker. Convert the following lecture content into clear, structured study notes in {language}.

LECTURE CONTENT:
{merged_context[:8000]}

Generate notes in this exact format:

# 📚 Lecture Notes

## 🗂️ Topics Covered
- List all main topics

## 📖 Detailed Notes
For each topic, provide:
- Key concepts explained clearly
- Important definitions
- Examples mentioned
- Formulas or rules if any

{summary_instruction}

{exam_q_instruction}

Make notes student-friendly, well-structured, and easy to revise from.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000,
        temperature=0.3
    )

    notes = response.choices[0].message.content
    word_count = len(merged_context.split())
    metadata = {"word_count": word_count}

    return notes, metadata
