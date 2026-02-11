"""
organizer.py — Moves and renames classified files into subject folders
under organized_storage/.
"""

import os
import shutil

STORAGE_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "organized_storage")


def move_file(src: str, category: str, new_name: str) -> str:
    """
    Move a file from `src` into organized_storage/<category>/<new_name>.

    - Creates the category folder if it doesn't exist.
    - Appends _1, _2, etc. if a file with the same name already exists.
    - Returns the final destination path.
    """
    category_dir = os.path.join(STORAGE_ROOT, category)
    os.makedirs(category_dir, exist_ok=True)

    dest = os.path.join(category_dir, new_name)
    dest = _handle_duplicate(dest)

    shutil.move(src, dest)
    print(f"[organizer] Moved → {dest}")
    return dest


def _handle_duplicate(dest: str) -> str:
    """
    If `dest` already exists, append _1, _2, … before the extension
    until a free name is found.
    """
    if not os.path.exists(dest):
        return dest

    base, ext = os.path.splitext(dest)
    counter = 1
    while True:
        candidate = f"{base}_{counter}{ext}"
        if not os.path.exists(candidate):
            return candidate
        counter += 1
