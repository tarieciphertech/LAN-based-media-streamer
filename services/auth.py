from werkzeug.security import generate_password_hash, check_password_hash
from models.base import query, execute

# ================= ROOT CONFIG =================
ROOT_USERNAME = "root"
ROOT_PASSWORD = "change_this_now"  # 🔴 change after first run
ROOT_ROLE = "root"


# ================= INIT ROOT USER =================
def ensure_root_user():
    """
    Creates a root admin account if it does not exist.
    This runs safely on every startup.
    """
    existing = query(
        "SELECT id FROM users WHERE role = ?",
        [ROOT_ROLE],
        one=True
    )

    if not existing:
        execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            [
                ROOT_USERNAME,
                generate_password_hash(ROOT_PASSWORD),
                ROOT_ROLE
            ]
        )
        print("[AUTH] Root user created")
    else:
        print("[AUTH] Root user already exists")


# ================= REGISTER USER =================
def register_user(username, password):
    if not username or not password:
        return False, "All fields are required"

    if username.lower() == ROOT_USERNAME:
        return False, "Username not allowed"

    existing = query(
        "SELECT id FROM users WHERE username = ?",
        [username],
        one=True
    )

    if existing:
        return False, "Username already exists"

    execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        [
            username,
            generate_password_hash(password),
            "user"
        ]
    )

    return True, None


# ================= LOGIN =================
def login_user(username, password):
    user = query(
        "SELECT * FROM users WHERE username = ?",
        [username],
        one=True
    )

    if user and check_password_hash(user["password"], password):
        return user

    return None
