# services/thumbnails.py

from pathlib import Path
import subprocess

THUMB_DIR = Path("static/thumbs/videos")

def ensure_thumb(video_path: Path, media_id: int) -> str:
    """
    Generate a thumbnail for a video if it doesn't exist.
    Returns the public URL.
    """
    THUMB_DIR.mkdir(parents=True, exist_ok=True)

    thumb_file = THUMB_DIR / f"{media_id}.jpg"

    if thumb_file.exists():
        return f"/static/thumbs/videos/{media_id}.jpg"

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-ss", "00:00:05",
            "-i", str(video_path),
            "-frames:v", "1",
            "-q:v", "2",
            str(thumb_file),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return f"/static/thumbs/videos/{media_id}.jpg"
