from pathlib import Path

from models.base import query, get_db
from services.thumbnails import ensure_thumb

VIDEO_EXTS = {".mp4", ".webm", ".ogg", ".mkv", ".avi"}

# ----------------------------
# Helpers
# ----------------------------

def is_video(filepath: str) -> bool:
    return Path(filepath).suffix.lower() in VIDEO_EXTS


# ----------------------------
# Episodes (Series support)
# ----------------------------

def get_episodes(parent_id):
    """
    Returns episodes for a series.
    If DB has no parent_id column, returns empty list.
    """
    try:
        rows = query(
            """
            SELECT *
            FROM media
            WHERE parent_id = ?
            ORDER BY episode_number ASC
            """,
            (parent_id,)
        )
    except Exception:
        # DB schema does not support episodes yet
        return []

    return [_decorate_media(r) for r in rows]


# ----------------------------
# Media listing (Home / Browse)
# ----------------------------

def list_media(user_id=None, q=None, category=None):
    sql = """
        SELECT
            m.id,
            m.title,
            m.filepath,
            m.category,
            w.progress
        FROM media m
        LEFT JOIN watch_history w
            ON w.media_id = m.id
            AND w.user_id = ?
        WHERE 1=1
    """
    params = [user_id]

    if q:
        sql += " AND m.title LIKE ?"
        params.append(f"%{q}%")

    if category:
        sql += " AND m.category = ?"
        params.append(category)

    sql += " ORDER BY m.id DESC"

    rows = query(sql, tuple(params))
    return [_decorate_media(r) for r in rows]


def get_media_by_id(media_id):
    return query(
        """
        SELECT
            m.id,
            m.title,
            m.filepath,
            m.category,
            w.progress
        FROM media m
        LEFT JOIN watch_history w
            ON w.media_id = m.id
        WHERE m.id = ?
        """,
        (media_id,),
        one=True
    )


# ----------------------------
# Auto‑play next video
# ----------------------------

def get_next_media(current_id):
    row = query(
        """
        SELECT
            m.id,
            m.title,
            m.filepath,
            m.category,
            NULL as progress
        FROM media m
        WHERE m.id > ?
        ORDER BY m.id ASC
        LIMIT 1
        """,
        (current_id,),
        one=True
    )

    return _decorate_media(row) if row else None


# ----------------------------
# Media decorator (CRITICAL)
# ----------------------------

def _decorate_media(r):
    """
    Converts sqlite3.Row → dict safely
    Handles missing columns gracefully
    """

    filepath = str(r["filepath"])
    media_id = r["id"]

    is_vid = is_video(filepath)

    # Thumbnail handling
    if is_vid:
        thumb_url = ensure_thumb(Path(filepath), media_id)
    else:
        thumb_url = "/static/thumbs/file.png"

    keys = r.keys()

    return {
        "id": media_id,
        "title": r["title"],
        "filepath": filepath,
        "category": r["category"] if "category" in keys else None,
        "progress": r["progress"] if "progress" in keys and r["progress"] is not None else 0,
        "is_video": is_vid,
        "thumb": thumb_url,
    }
