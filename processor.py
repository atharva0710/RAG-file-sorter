"""
processor.py — Text extraction from PDF and TXT files.
Supports PyPDF2 for PDFs and plain read for .txt files.
Returns up to the first 3 000 words of content.
"""

import os
from PyPDF2 import PdfReader

MAX_WORDS = 3000

class UnsupportedFileTypeError(Exception):
    """Raised when the file extension is not supported."""
    pass


def extract_text(filepath: str) -> str:
    """
    Dispatch to the correct extractor based on file extension.
    Returns the first MAX_WORDS words of extracted text.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        UnsupportedFileTypeError: If the extension is not .pdf or .txt.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        raw = _extract_pdf(filepath)
    elif ext == ".txt":
        raw = _extract_txt(filepath)
    else:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{ext}'. Only .pdf and .txt are supported."
        )

    # Truncate to the first MAX_WORDS words
    words = raw.split()
    return " ".join(words[:MAX_WORDS])


def _extract_pdf(filepath: str) -> str:
    """
    Read all pages of a PDF using PyPDF2 and return concatenated text.
    Handles corrupt / empty PDFs gracefully.
    """
    try:
        reader = PdfReader(filepath)
    except Exception as e:
        print(f"[processor] WARNING: Could not read PDF '{filepath}': {e}")
        return ""

    pages_text = []
    for page in reader.pages:
        try:
            text = page.extract_text()
            if text:
                pages_text.append(text)
        except Exception as e:
            print(f"[processor] WARNING: Skipping a page in '{filepath}': {e}")

    return "\n".join(pages_text)


def _extract_txt(filepath: str) -> str:
    """Read a plain-text file with UTF-8 encoding."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        # Fallback to latin-1 which never fails
        with open(filepath, "r", encoding="latin-1") as f:
            return f.read()


# ── Quick CLI test ──────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python processor.py <filepath>")
        sys.exit(1)

    text = extract_text(sys.argv[1])
    word_count = len(text.split())
    print(f"Extracted {word_count} words from '{sys.argv[1]}'")
    print("-" * 60)
    print(text[:500], "..." if len(text) > 500 else "")
