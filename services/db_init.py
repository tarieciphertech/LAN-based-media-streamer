from werkzeug.security import generate_password_hash
from models.base import query, execute

def init_db():
    # USERS
    execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        active INTEGER NOT NULL DEFAULT 1
    )
    """)

    # MEDIA
    execute("""
    CREATE TABLE IF NOT EXISTS media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        filepath TEXT NOT NULL,
        category TEXT
    )
    """)

    # WATCH HISTORY
    execute("""
    CREATE TABLE IF NOT EXISTS watch_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        media_id INTEGER NOT NULL,
        progress INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, media_id)
    )
    """)

    ensure_root_user()
    ensure_active_column()


def ensure_root_user():
    """Ensure a built-in root admin exists."""
    root = query(
        "SELECT id FROM users WHERE role = ?",
        ("root",),
        one=True
    )

    if root:
        return

    execute(
        """
        INSERT INTO users (username, password, role, active)
        VALUES (?, ?, ?, 1)
        """,
        (
            "root",
            generate_password_hash("root123"),  # CHANGE AFTER FIRST LOGIN
            "root"
        )
    )

    print("[AUTH] Root admin created (username: root / password: root123)")


def ensure_active_column():
    """
    Migration helper: add `active` column if DB existed before.
    SQLite-safe.
    """
    cols = query("PRAGMA table_info(users)")
    col_names = [c["name"] for c in cols]

    if "active" not in col_names:
        execute("ALTER TABLE users ADD COLUMN active INTEGER NOT NULL DEFAULT 1")
        print("[DB] Added missing `active` column to users table")
