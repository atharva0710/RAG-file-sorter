"""
watcher.py — Watches input_drop_zone/ for new files and triggers
the extract → classify → organise → save pipeline.

Usage:
    python watcher.py
    (Ctrl+C to stop)
"""

import os # Used for folder paths and finding the current directory.
import time # Used to pause the program for a short time.
import sys # Used to exit the program.
from watchdog.observers import Observer # Used to watch for changes in the file system.
from watchdog.events import FileSystemEventHandler # Used to handle events in the file system.

# Local modules
from classifier import classify_file # Used to classify files.
from organizer import move_file # Used to move files.
from db import Logger # Used to log files.
from processor import extract_text, UnsupportedFileTypeError # Used to extract text from files.

# ── Configuration ───────────────────────────────────────────────────
# Define the folder to watch relative to this script
DROP_ZONE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input_drop_zone")
# If you want to watch a completely different folder (like one on your Desktop), you can just replace that whole line with the direct path:
# DROP_ZONE = "/Users/atharvamandhaniya/Desktop/My_New_Watch_Folder"
# Time to wait (in seconds) for a file copy to finish before processing
SETTLE_DELAY = 1  # seconds to wait for the file write to finish

# Initialize the database logger
logger = Logger()


class FileHandler(FileSystemEventHandler):
    """
    React to new files landing in the drop zone.
    This class defines what happens when a new file is detected.
    """

    def on_created(self, event):
        """
        Triggered automatically when a file is created.
        Serves as the 'Security Guard' filtering valid files.
        """
        # 1. Ignore if it's a folder, not a file
        if event.is_directory:
            return

        filepath = event.src_path
        filename = os.path.basename(filepath)

        # 2. Ignore hidden system files (.DS_Store) and temporary files
        if (filename.startswith(".") or filename.startswith("~")
                or filename.endswith(".tmp")):
            return

        # Visual separator for the terminal
        print(f"\n{'='*60}")
        print(f"[watcher] New file detected: {filename}")
        print(f"{'='*60}")

        # 3. Wait for the file to finish writing (prevents reading empty files)
        time.sleep(SETTLE_DELAY)

        # 4. Hand off to the processing pipeline
        try:
            self.handle_new_token(filepath, filename)
        except Exception as e:
            # Catch-all safety net to keep the watcher running even if a file fails
            print(f"[watcher] ERROR processing '{filename}': {e}")

    def handle_new_token(self, filepath: str, filename: str):
        """
        The Core Pipeline: Extract → Classify → Move → Log
        Processes a newly detected file through the entire workflow.
        """
        # Step 1 — Extract text
        try:
            text = extract_text(filepath)
        except UnsupportedFileTypeError:
            print(f"[watcher] Unsupported file type, moving to _unsupported/")
            move_file(filepath, "_unsupported", filename)
            return

        # If file is empty or unreadable
        if not text.strip(): #text.strip() removes whitespace; if not ...: checks if empty.
            print(f"[watcher] No text extracted, moving to _unclassified/")
            move_file(filepath, "_unclassified", filename)
            return

        # Step 2 — Classify via LLM (The "Brain")
        print(f"[watcher] Classifying...")
        result = classify_file(text, filename)

        category = result["category"]
        new_name = result["suggested_filename"]
        summary  = result["summary_sentence"]

        print(f"[watcher] Category : {category}")
        print(f"[watcher] New name : {new_name}")
        print(f"[watcher] Summary  : {summary}")

        # Step 3 — Move & rename (The "Arm")
        # specific destination path is returned by move_file
        dest = move_file(filepath, category, new_name)

        # Step 4 — Log to SQLite (The "Memory")
        logger.log(filename, new_name, category, summary, dest)

        print(f"[watcher] ✅ Done!\n")


def start_watcher():
    """
    Start the background watchdog process.
    This is the 'Ignition Switch' of the application.
    """
    # Create the drop zone if it doesn't exist
    os.makedirs(DROP_ZONE, exist_ok=True)

    handler = FileHandler()
    observer = Observer()
    
    # Schedule the observer:
    # This tells the observer to monitor the DROP_ZONE directory for file system events.
    # recursive=True means we also watch subfolders inside input_drop_zone
    observer.schedule(handler, DROP_ZONE, recursive=True)
    observer.start()

    print(f"👁  Watching '{DROP_ZONE}' for new files...")
    print(f"   Drop a PDF or TXT file in there and watch the magic.")
    print(f"   Press Ctrl+C to stop.\n")

    # Keep the main thread alive so the background thread can work
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        observer.stop()
        print("\n[watcher] Stopped.")
    observer.join()


if __name__ == "__main__":
    start_watcher()
