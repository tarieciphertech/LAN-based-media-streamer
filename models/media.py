from pathlib import Path
from config import VIDEO_EXT, MEDIA_DIR
from services.thumbnails import ensure_thumb


class Media:
    """
    Base media class (images, posters, etc.)
    """

    def __init__(self, row):
        self.id = row["id"]
        self.filepath = Path(row["filepath"])
        self.title = row["title"]
        self.category = row["category"] if "category" in row.keys() else "general"
        self.progress = row["progress"] if "progress" in row.keys() else 0

    @property
    def full_path(self):
        return MEDIA_DIR / self.filepath

    @property
    def filename(self):
        return self.filepath.name

    @property
    def extension(self):
        return self.filepath.suffix.lower()

    def is_video(self):
        return False

    def icon(self):
        return None

    def thumb_url(self):
        """
        Default thumbnail (used by templates)
        """
        return "/static/thumbs/placeholder.jpg"


class VideoMedia(Media):
    """
    Video media (movies, series, clips)
    """

    def is_video(self):
        return True

    def icon(self):
        return "▶"

    def thumb_url(self):
        # auto-generate thumbnail using ffmpeg
        return ensure_thumb(self.full_path, self.id)


def media_factory(row):
    """
    Factory method that returns the correct Media type
    """
    ext = Path(row["filepath"]).suffix.lower()

    if ext in VIDEO_EXT:
        return VideoMedia(row)

    return Media(row)
