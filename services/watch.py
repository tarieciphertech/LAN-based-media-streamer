from models.base import query, execute

def get_watch_progress(user_id):
    rows = query(
        "SELECT media_id, progress FROM watch_history WHERE user_id=?",
        [user_id]
    )
    return {row["media_id"]: row["progress"] for row in rows}

def update_progress(user_id, media_id, progress):
    execute("""
        INSERT INTO watch_history (user_id, media_id, progress)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, media_id)
        DO UPDATE SET progress=excluded.progress
    """, [user_id, media_id, progress])
