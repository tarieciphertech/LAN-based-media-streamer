from functools import wraps
from flask import session, redirect, url_for, abort

def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login_view"))

            user_role = session.get("role")
            if user_role not in roles:
                abort(403)

            return view(*args, **kwargs)
        return wrapped
    return decorator
