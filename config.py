
from pathlib import Path
import os

MEDIA_DIR = Path(os.environ.get("MEDIA_DIR", "./media")).resolve()
DB_PATH = Path("netflix_clone.db")

SECRET_KEY = "dev-secret"

ALLOWED_EXT = {".mp4", ".mkv", ".webm", ".avi", ".mp3", ".ogg"}
VIDEO_EXT = {".mp4", ".mkv", ".webm", ".avi"}
