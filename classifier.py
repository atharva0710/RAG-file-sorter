"""
classifier.py — Sends extracted text to Google Gemini Flash and
returns structured classification data (category, filename, summary).

Uses a strict "librarian" system prompt that forces JSON-only output.
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ───────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-flash-latest"

VALID_CATEGORIES = [
    "Systems CS",
    "ML-Bio",
    "Personal",
    "Finance",
]

SYSTEM_PROMPT = f"""\
You are a meticulous research librarian and file-organisation expert.

Your job:
1. Read the document text provided by the user.
2. Decide which category it belongs to.
3. Suggest a clean, descriptive filename.
4. Write a one-sentence summary.

Rules:
- Output ONLY a valid JSON object. No markdown, no explanation, no extra text.
- The JSON must have exactly 3 keys:
  {{
    "summary_sentence": "A concise one-sentence summary of the document.",
    "category": "One of {VALID_CATEGORIES}",
    "suggested_filename": "year_topic_snake_case.pdf"
  }}
- For "category", pick the BEST match from this list: {VALID_CATEGORIES}.
  If nothing fits well, use "Personal".
- For "suggested_filename":
  • Start with the year if you can detect it (e.g. 2026_).
  • Use lowercase snake_case.
  • Keep the same file extension as the original.
- Do NOT wrap your response in ```json``` or any other formatting.
"""


def _configure_client():
    """Initialise the Gemini client with the API key."""
    if not GEMINI_API_KEY:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. "
            "Create a .env file with GEMINI_API_KEY=your-key-here"
        )
    genai.configure(api_key=GEMINI_API_KEY)


def classify_file(text: str, original_filename: str) -> dict:
    """
    Send extracted text + original filename to Gemini Flash.

    Returns a dict with keys:
        - summary_sentence (str)
        - category (str)
        - suggested_filename (str)

    On failure (bad JSON, API error) returns a fallback dict
    that places the file in '_unclassified'.
    """
    _configure_client()

    # Preserve the original extension
    ext = os.path.splitext(original_filename)[1].lower() or ".pdf"

    user_prompt = (
        f"Original filename: {original_filename}\n\n"
        f"--- DOCUMENT TEXT ---\n{text}\n--- END ---"
    )

    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=SYSTEM_PROMPT,
    )

    try:
        response = model.generate_content(user_prompt)
        raw = response.text.strip()

        # Defensive: strip possible markdown fences
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

        result = json.loads(raw)

        # Validate required keys
        for key in ("summary_sentence", "category", "suggested_filename"):
            if key not in result:
                raise ValueError(f"Missing key: {key}")

        # Ensure the extension is preserved
        if not result["suggested_filename"].endswith(ext):
            result["suggested_filename"] += ext

        # Normalise category
        if result["category"] not in VALID_CATEGORIES:
            result["category"] = "Personal"

        return result

    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"[classifier] WARNING: Could not parse LLM response: {e}")
        print(f"[classifier] Raw response was: {raw if 'raw' in dir() else 'N/A'}")
        return {
            "summary_sentence": "Could not classify this document.",
            "category": "_unclassified",
            "suggested_filename": original_filename,
        }

    except Exception as e:
        print(f"[classifier] ERROR: API call failed: {e}")
        return {
            "summary_sentence": "API error during classification.",
            "category": "_unclassified",
            "suggested_filename": original_filename,
        }


# ── Quick CLI test ──────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    from processor import extract_text

    if len(sys.argv) < 2:
        print("Usage: python classifier.py <filepath>")
        sys.exit(1)

    filepath = sys.argv[1]
    filename = os.path.basename(filepath)

    print(f"Extracting text from '{filepath}'...")
    text = extract_text(filepath)

    print(f"Classifying ({len(text.split())} words)...")
    result = classify_file(text, filename)

    print(json.dumps(result, indent=2))
