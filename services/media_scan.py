from pathlib import Path
from config import MEDIA_DIR, ALLOWED_EXT, VIDEO_EXT
from models.base import query, execute
from services.thumbnails import ensure_thumb

def scan_media():
    MEDIA_DIR.mkdir(exist_ok=True)

    existing = query("SELECT filepath FROM media")
    existing_files = {row["filepath"] for row in existing}

    added = 0

    for path in MEDIA_DIR.rglob("*"):
        if not path.is_file():
            continue

        ext = path.suffix.lower()
        if ext not in ALLOWED_EXT:
            continue

        filepath = str(path.relative_to(MEDIA_DIR))

        if filepath in existing_files:
            continue

        title = path.stem.replace("_", " ").title()

        # Generate thumbnail for videos
        if ext in VIDEO_EXT:
            ensure_thumb(path, None)

        execute(
            "INSERT INTO media (title, filepath) VALUES (?, ?)",
            [title, filepath]
        )

        added += 1

    print(f"[MEDIA SCAN] Added {added} new items")
