"""
test_pipeline.py — Quick end-to-end test.
Runs processor.extract_text → classifier.classify_file on a sample file
and prints the JSON result.

Usage:
    python test_pipeline.py
"""

import json
import os
from processor import extract_text
from classifier import classify_file

TEST_FILE = os.path.join(
    os.path.dirname(__file__), "tests", "sample_files", "test_paper.txt"
)

if __name__ == "__main__":
    print(f"📄 Test file: {TEST_FILE}\n")

    # Step 1 — Extract text
    text = extract_text(TEST_FILE)
    print(f"Extracted {len(text.split())} words.\n")

    # Step 2 — Classify via LLM
    result = classify_file(text, os.path.basename(TEST_FILE))

    # Step 3 — Print the JSON result
    print("─" * 50)
    print("CLASSIFICATION RESULT:")
    print("─" * 50)
    print(json.dumps(result, indent=2))
