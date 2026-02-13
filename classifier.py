"""
classifier.py — Sends extracted text to Google Gemini Flash and
returns structured classification data (category, filename, summary).

Uses a strict "librarian" system prompt that forces JSON-only output.
Supports dynamic categories: checks VALID_CATEGORIES first, then
existing folders in organized_storage, and creates new ones if needed.
"""

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env file to keep it secure
load_dotenv()

# ── Configuration ───────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-flash-latest"

# Hard-coded starting categories
VALID_CATEGORIES = [
    "Systems CS",
    "ML-Bio",
    "Personal",
    "Finance",
]

# Path to where files are organized
STORAGE_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "organized_storage")


def _get_existing_folders() -> list[str]:
    """
    Scan organized_storage/ and return a list of existing category folder names.
    This allows the AI to discover categories you manually created.
    Excludes internal folders that start with '_' (like _unclassified, _unsupported).
    """
    if not os.path.isdir(STORAGE_ROOT):
        return []
    return [
        name for name in os.listdir(STORAGE_ROOT)
        if os.path.isdir(os.path.join(STORAGE_ROOT, name))
        and not name.startswith("_")
    ]


def _get_all_categories() -> list[str]:
    """
    Merge VALID_CATEGORIES + existing folders (deduplicated, sorted).
    This ensures the AI knows about EVERY category available right now.
    """
    existing = _get_existing_folders()
    merged = list(set(VALID_CATEGORIES + existing))
    merged.sort()
    return merged


def _build_system_prompt() -> str:
    """
    Build the system prompt dynamically.
    Injects the current list of folders so the AI knows valid destinations.
    Sets the "Librarian" persona and enforces strict JSON output.
    """
    all_cats = _get_all_categories()

    return f"""\
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
    "category": "The best-fit category name",
    "suggested_filename": "year_topic_snake_case.pdf"
  }}

Category selection (FOLLOW THIS PRIORITY ORDER):
  1. FIRST, try to fit the document into one of these EXISTING categories: {all_cats}
  2. If NONE of the existing categories fit well, you MAY create a NEW category.
     - New category names must be short (1-3 words), Title Case, and descriptive.
     - Examples: "History", "Philosophy", "Cooking", "Health", "Legal".
  3. Use "Personal" ONLY for truly personal documents (letters, journals, notes).

- For "suggested_filename":
  • Start with the year if you can detect it (e.g. 2026_).
  • Use lowercase snake_case.
  • Keep the same file extension as the original.
- Do NOT wrap your response in ```json``` or any other formatting.
"""


def _configure_client():
    """Initialise the Google Gemini client with the API key."""
    if not GEMINI_API_KEY:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. "
            "Create a .env file with GEMINI_API_KEY=your-key-here"
        )
    genai.configure(api_key=GEMINI_API_KEY)


def classify_file(text: str, original_filename: str) -> dict:
    """
    The Main Intelligence Function.
    Sends extracted text + original filename to Gemini Flash.

    Steps:
    1. Prepare prompt with filename and text.
    2. Call Gemini API.
    3. Clean and parse JSON response.
    4. Validate and sanitize keys.
    5. Return decision to watcher.py.
    """
    _configure_client()

    # Preserve the original extension (e.g., .pdf) to use in the new filename
    ext = os.path.splitext(original_filename)[1].lower() or ".pdf"

    user_prompt = (
        f"Original filename: {original_filename}\n\n"
        f"--- DOCUMENT TEXT ---\n{text}\n--- END ---"
    )

    # Build prompt dynamically so it sees current folders on disk
    system_prompt = _build_system_prompt()

    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=system_prompt,
    )

    try:
        # Send data to Google and wait for response
        response = model.generate_content(user_prompt)
        raw = response.text.strip()

        # Defensive: strip possible markdown fences (```json ... ```)
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

        # Parse the raw string into a Python dictionary
        result = json.loads(raw)

        # Validate required keys exist
        for key in ("summary_sentence", "category", "suggested_filename"):
            if key not in result:
                raise ValueError(f"Missing key: {key}")

        # Ensure the extension is preserved in the new filename
        if not result["suggested_filename"].endswith(ext):
            result["suggested_filename"] += ext

        # Sanitise the category name (remove headers/slashes to avoid bad paths)
        result["category"] = result["category"].strip().replace("/", "-").replace("\\", "-")

        # Log if the AI created a new category that didn't exist before
        all_known = _get_all_categories()
        if result["category"] not in all_known:
            print(f"[classifier] New category created: '{result['category']}'")

        return result

    except (json.JSONDecodeError, ValueError, KeyError) as e:
        # Fallback: If AI fails or returns bad JSON, move to _unclassified
        print(f"[classifier] WARNING: Could not parse LLM response: {e}")
        print(f"[classifier] Raw response was: {raw if 'raw' in dir() else 'N/A'}")
        return {
            "summary_sentence": "Could not classify this document.",
            "category": "_unclassified",
            "suggested_filename": original_filename,
        }

    except Exception as e:
        # Fallback: API errors (network issues, etc.)
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

    print(f"Known categories: {_get_all_categories()}")
    print(f"Extracting text from '{filepath}'...")
    text = extract_text(filepath)

    print(f"Classifying ({len(text.split())} words)...")
    result = classify_file(text, filename)

    print(json.dumps(result, indent=2))
