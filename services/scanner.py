from pathlib import Path
from config import MEDIA_DIR, ALLOWED_EXT
from models.base import query, execute

def scan_media():
    MEDIA_DIR.mkdir(exist_ok=True)

    existing = query("SELECT filepath FROM media")
    existing_files = {row["filepath"] for row in existing}

    for path in MEDIA_DIR.rglob("*"):
        if path.suffix.lower() not in ALLOWED_EXT:
            continue

        filepath = str(path.relative_to(MEDIA_DIR))
        if filepath in existing_files:
            continue

        title = path.stem.replace("_", " ").title()

        execute(
            "INSERT INTO media (title, filepath) VALUES (?, ?)",
            [title, filepath]
        )
