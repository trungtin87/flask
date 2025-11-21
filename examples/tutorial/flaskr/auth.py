import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from .db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator chuyển hướng người dùng ẩn danh đến trang đăng nhập."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """Nếu một user id được lưu trữ trong session, tải đối tượng user từ
    cơ sở dữ liệu vào ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Đăng ký một người dùng mới.

    Xác thực rằng tên người dùng chưa được sử dụng. Băm
    mật khẩu để bảo mật.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Tên người dùng là bắt buộc."
        elif not password:
            error = "Mật khẩu là bắt buộc."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                # Tên người dùng đã được sử dụng, điều này gây ra
                # lỗi commit. Hiển thị một lỗi xác thực.
                error = f"Người dùng {username} đã được đăng ký."
            else:
                # Thành công, đi đến trang đăng nhập.
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Đăng nhập một người dùng đã đăng ký bằng cách thêm user id vào session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Tên người dùng không chính xác."
        elif not check_password_hash(user["password"], password):
            error = "Mật khẩu không chính xác."

        if error is None:
            # lưu trữ user id trong một session mới và quay lại index
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Xóa session hiện tại, bao gồm user id đã lưu trữ."""
    session.clear()
    return redirect(url_for("index"))
