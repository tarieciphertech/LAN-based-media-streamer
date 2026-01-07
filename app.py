from flask import (
    Flask, render_template, request,
    redirect, session, send_from_directory,
    jsonify, url_for, abort
)
from werkzeug.utils import secure_filename
from functools import wraps
import os

from config import SECRET_KEY, MEDIA_DIR, ALLOWED_EXT

from services.auth import login_user, register_user
from services.media import (
    list_media,
    get_media_by_id,
    get_next_media,
    get_episodes,
)
from services.db_init import init_db
from services.media_scan import scan_media
from services.watch import update_progress
from services.roles import role_required

from models.base import execute, query
from werkzeug.security import generate_password_hash

# ================= APP =================
app = Flask(__name__)
app.secret_key = SECRET_KEY

# ================= LOGIN REQUIRED =================
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_view"))
        return view(*args, **kwargs)
    return wrapped

# ================= ROOT ADMIN BOOTSTRAP =================
def ensure_root_admin():
    root = query(
        "SELECT id FROM users WHERE role = 'root'",
        one=True
    )

    if not root:
        print("[INIT] Creating ROOT admin account")
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

# ================= INIT =================
with app.app_context():
    init_db()
    ensure_root_admin()
    added = scan_media()
    print(f"[MEDIA SCAN] Added {added} new items")

# ================= HOME =================
@app.route("/")
def index():
    user_id = session.get("user_id")

    q = request.args.get("q")
    category = request.args.get("category")

    media = list_media(
        user_id=user_id,
        q=q,
        category=category
    )

    return render_template(
        "index.html",
        media=media,
        q=q,
        category=category
    )

# ================= PROTECTED MEDIA =================
@app.route("/media/<path:filename>")
@login_required
def media_file(filename):
    return send_from_directory(MEDIA_DIR, filename)

# ================= WATCH =================
@app.route("/watch/<int:media_id>")
def watch(media_id):
    media = get_media_by_id(media_id)

    if not media:
        abort(404)

    # media is a DICT (decorated)
    episodes = get_episodes(media_id) or []

    progress = media["progress"]
    next_media = get_next_media(media_id)

    return render_template(
        "watch.html",
        media=media,
        episodes=episodes,
        progress=progress,
        next_media=next_media,
    )

# ================= SAVE WATCH PROGRESS =================
@app.route("/progress", methods=["POST"])
@login_required
def save_progress():
    data = request.get_json()

    update_progress(
        session["user_id"],
        int(data["media_id"]),
        int(data["progress"])
    )

    return jsonify({"ok": True})

# ================= ADMIN DASHBOARD =================
@app.route("/admin")
@role_required("root", "admin")
def admin_dashboard():
    return render_template("admin/dashboard.html")

# ================= USER MANAGEMENT =================
@app.route("/admin/users")
@role_required("root", "admin")
def admin_users():
    q = request.args.get("q", "").strip()
    role = request.args.get("role", "")
    status = request.args.get("status", "")

    sql = "SELECT id, username, role, active FROM users WHERE 1=1"
    params = []

    if q:
        sql += " AND username LIKE ?"
        params.append(f"%{q}%")

    if role in ("user", "admin", "root"):
        sql += " AND role = ?"
        params.append(role)

    if status == "active":
        sql += " AND active = 1"
    elif status == "disabled":
        sql += " AND active = 0"

    sql += " ORDER BY id"

    users = query(sql, tuple(params))
    return render_template("admin/users.html", users=users)

@app.route("/admin/users/create", methods=["POST"])
@role_required("root")
def create_admin_user():
    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]

    if role not in ("user", "admin"):
        abort(400)

    existing = query(
        "SELECT id FROM users WHERE username=?",
        (username,),
        one=True
    )
    if existing:
        abort(400)

    execute(
        """
        INSERT INTO users (username, password, role, active)
        VALUES (?, ?, ?, 1)
        """,
        (username, generate_password_hash(password), role)
    )

    return redirect(url_for("admin_users"))

@app.route("/admin/users/<int:user_id>/toggle")
@role_required("root", "admin")
def toggle_user(user_id):
    target = query(
        "SELECT role FROM users WHERE id=?",
        (user_id,),
        one=True
    )

    if not target or target["role"] == "root":
        abort(403)

    execute(
        "UPDATE users SET active = NOT active WHERE id=?",
        (user_id,)
    )

    return redirect(url_for("admin_users"))

# ================= ADMIN UPLOAD =================
@app.route("/admin/upload", methods=["GET", "POST"])
@role_required("root", "admin")
def upload_media():
    if request.method == "POST":
        file = request.files.get("file")
        title = request.form.get("title")
        category = request.form.get("category", "general")

        if not file or not title:
            abort(400)

        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1].lower()

        if ext not in ALLOWED_EXT:
            abort(400)

        path = MEDIA_DIR / filename
        file.save(path)

        execute(
            "INSERT INTO media (title, filepath, category) VALUES (?, ?, ?)",
            (title, filename, category)
        )

        return redirect(url_for("admin_dashboard"))

    return render_template("admin/upload.html")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login_view():
    if request.method == "POST":
        user = login_user(
            request.form["username"],
            request.form["password"]
        )

        if user and user["active"]:
            session["user_id"] = user["id"]
            session["role"] = user["role"]

            if user["role"] in ("admin", "root"):
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("index"))

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register_view():
    if request.method == "POST":
        success, error = register_user(
            request.form["username"],
            request.form["password"]
        )

        if success:
            return redirect("/login")

        return render_template("register.html", error=error)

    return render_template("register.html")

# ================= LOGOUT =================
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/login")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
