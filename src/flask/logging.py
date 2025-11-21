from __future__ import annotations

import logging
import sys
import typing as t

from werkzeug.local import LocalProxy

from .globals import request

if t.TYPE_CHECKING:  # pragma: no cover
    from .sansio.app import App


@LocalProxy
def wsgi_errors_stream() -> t.TextIO:
    """Tìm luồng lỗi thích hợp nhất cho ứng dụng. Nếu một request
    đang hoạt động, ghi log vào ``wsgi.errors``, nếu không sử dụng ``sys.stderr``.

    Nếu bạn cấu hình :class:`logging.StreamHandler` của riêng mình, bạn có thể muốn
    sử dụng cái này cho luồng. Nếu bạn đang sử dụng cấu hình tệp hoặc dict và
    không thể import cái này trực tiếp, bạn có thể tham chiếu đến nó như là
    ``ext://flask.logging.wsgi_errors_stream``.
    """
    if request:
        return request.environ["wsgi.errors"]  # type: ignore[no-any-return]

    return sys.stderr


def has_level_handler(logger: logging.Logger) -> bool:
    """Kiểm tra xem có một handler trong chuỗi logging sẽ xử lý
    :meth:`effective level <~logging.Logger.getEffectiveLevel>` của logger đã cho hay không.
    """
    level = logger.getEffectiveLevel()
    current = logger

    while current:
        if any(handler.level <= level for handler in current.handlers):
            return True

        if not current.propagate:
            break

        current = current.parent  # type: ignore

    return False


#: Ghi log các thông báo vào :func:`~flask.logging.wsgi_errors_stream` với định dạng
#: ``[%(asctime)s] %(levelname)s in %(module)s: %(message)s``.
default_handler = logging.StreamHandler(wsgi_errors_stream)  # type: ignore
default_handler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
)


def create_logger(app: App) -> logging.Logger:
    """Lấy logger của ứng dụng Flask và cấu hình nó nếu cần.

    Tên logger sẽ giống như
    :attr:`app.import_name <flask.Flask.name>`.

    Khi :attr:`~flask.Flask.debug` được bật, thiết lập mức logger thành
    :data:`logging.DEBUG` nếu nó chưa được thiết lập.

    Nếu không có handler cho mức hiệu quả của logger, thêm một
    :class:`~logging.StreamHandler` cho
    :func:`~flask.logging.wsgi_errors_stream` với một định dạng cơ bản.
    """
    logger = logging.getLogger(app.name)

    if app.debug and not logger.level:
        logger.setLevel(logging.DEBUG)

    if not has_level_handler(logger):
        logger.addHandler(default_handler)

    return logger
