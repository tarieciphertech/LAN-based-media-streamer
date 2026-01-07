from functools import wraps
from flask import session, redirect, url_for
from models.base import query

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("login_view"))

        user = query(
            "SELECT role FROM users WHERE id = ?",
            [user_id],
            one=True
        )

        if not user or user["role"] not in ("admin", "root"):
            return "Forbidden", 403

        return view(*args, **kwargs)

    return wrapped
