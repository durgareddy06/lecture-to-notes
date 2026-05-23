import json
from groq import Groq

def generate_flashcards(notes_markdown: str, groq_api_key: str) -> list:
    """Generate flashcards from notes using Groq."""

    client = Groq(api_key=groq_api_key)

    prompt = f"""From the following lecture notes, generate 8 flashcards for revision.

NOTES:
{notes_markdown[:4000]}

Return ONLY a JSON array like this (no extra text):
[
  {{"question": "What is X?", "answer": "X is...", "topic": "Topic Name"}},
  ...
]
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        content = content.replace("```json", "").replace("```", "").strip()
        flashcards = json.loads(content)
        return flashcards
    except Exception:
        return []
