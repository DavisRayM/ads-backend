import functools
from collections.abc import Callable

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from ads.db import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view: Callable):
    """
    Function decorator that ensures user is logged in before view is called
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g._user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_user_from_session():
    """
    Loads logged in user from session before a request is processed
    """
    user_id = session.get("user")
    if user_id is None:
        g._user = None
    else:
        result = User.get(id=user_id)
        if result:
            g._user = result


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        errors = None

        if not username:
            errors = "Username is required"
        elif not password:
            errors = "Password is required"

        if errors:
            flash(errors)
        elif User.get(username=username):
            flash("user already exists")
        else:
            User.create(username, password)
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        errors = None

        if not username:
            errors = "Username is required"
        elif not password:
            errors = "Password is required"

        user = User.get(username=username)

        if errors:
            flash(errors)
        elif not user or not check_password_hash(user.hashed_password, password):
            flash("invalid username/password")
        else:
            g._user = user
            session.clear()
            session["user"] = user.id

            return redirect(url_for("health_check"))

    return render_template("auth/login.html")


@bp.route("/logout", methods=("POST",))
def logout():
    session.clear()
    g._user = None
    return redirect(url_for("auth.login"))
