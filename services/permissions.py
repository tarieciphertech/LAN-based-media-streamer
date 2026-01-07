from functools import wraps
from flask import session, redirect, url_for, abort
from models.base import query

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return query("SELECT * FROM users WHERE id = ?", (user_id,), one=True)

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_view"))
        return view(*args, **kwargs)
    return wrapped

def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = get_current_user()
            if not user:
                return redirect(url_for("login_view"))

            if user["role"] not in roles:
                abort(403)

            return view(*args, **kwargs)
        return wrapped
    return decorator
