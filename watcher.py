"""
watcher.py — Watches input_drop_zone/ for new files and triggers
the extract → classify → organise → save pipeline.

Usage:
    python watcher.py
    (Ctrl+C to stop)
"""

import os
import time
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from processor import extract_text, UnsupportedFileTypeError
from classifier import classify_file
from organizer import move_file
from db import Logger

DROP_ZONE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input_drop_zone")
SETTLE_DELAY = 1  # seconds to wait for the file write to finish

logger = Logger()


class FileHandler(FileSystemEventHandler):
    """React to new files landing in the drop zone."""

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        filename = os.path.basename(filepath)

        # Ignore hidden / temp files (.DS_Store, .tmp, ~ prefixed, etc.)
        if (filename.startswith(".") or filename.startswith("~")
                or filename.endswith(".tmp")):
            return

        print(f"\n{'='*60}")
        print(f"[watcher] New file detected: {filename}")
        print(f"{'='*60}")

        # Wait for the file to finish writing
        time.sleep(SETTLE_DELAY)

        try:
            self.handle_new_token(filepath, filename)
        except Exception as e:
            print(f"[watcher] ERROR processing '{filename}': {e}")

    def handle_new_token(self, filepath: str, filename: str):
        # Step 1 — Extract text
        try:
            text = extract_text(filepath)
        except UnsupportedFileTypeError:
            print(f"[watcher] Unsupported file type, moving to _unsupported/")
            move_file(filepath, "_unsupported", filename)
            return

        if not text.strip():
            print(f"[watcher] No text extracted, moving to _unclassified/")
            move_file(filepath, "_unclassified", filename)
            return

        # Step 2 — Classify via LLM
        print(f"[watcher] Classifying...")
        result = classify_file(text, filename)

        category = result["category"]
        new_name = result["suggested_filename"]
        summary  = result["summary_sentence"]

        print(f"[watcher] Category : {category}")
        print(f"[watcher] New name : {new_name}")
        print(f"[watcher] Summary  : {summary}")

        # Step 3 — Move & rename
        dest = move_file(filepath, category, new_name)

        # Step 4 — Log to SQLite
        logger.log(filename, new_name, category, summary, dest)

        print(f"[watcher] ✅ Done!\n")


def start_watcher():
    """Start the watchdog observer on input_drop_zone/."""
    os.makedirs(DROP_ZONE, exist_ok=True)

    handler = FileHandler()
    observer = Observer()
    observer.schedule(handler, DROP_ZONE, recursive=False)
    observer.start()

    print(f"👁  Watching '{DROP_ZONE}' for new files...")
    print(f"   Drop a PDF or TXT file in there and watch the magic.")
    print(f"   Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[watcher] Stopped.")
    observer.join()


if __name__ == "__main__":
    start_watcher()
