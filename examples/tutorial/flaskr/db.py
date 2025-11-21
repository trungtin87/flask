import sqlite3
from datetime import datetime

import click
from flask import current_app
from flask import g


def get_db():
    """Kết nối đến cơ sở dữ liệu đã cấu hình của ứng dụng. Kết nối
    là duy nhất cho mỗi yêu cầu và sẽ được sử dụng lại nếu hàm này được gọi
    lại.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """Nếu yêu cầu này đã kết nối đến cơ sở dữ liệu, đóng
    kết nối.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """Xóa dữ liệu hiện có và tạo các bảng mới."""
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Xóa dữ liệu hiện có và tạo các bảng mới."""
    init_db()
    click.echo("Đã khởi tạo cơ sở dữ liệu.")


sqlite3.register_converter("timestamp", lambda v: datetime.fromisoformat(v.decode()))


def init_app(app):
    """Đăng ký các hàm cơ sở dữ liệu với ứng dụng Flask. Hàm này được gọi bởi
    application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
