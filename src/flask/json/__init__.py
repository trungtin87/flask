from __future__ import annotations

import json as _json
import typing as t

from ..globals import current_app
from .provider import _default

if t.TYPE_CHECKING:  # pragma: no cover
    from ..wrappers import Response


def dumps(obj: t.Any, **kwargs: t.Any) -> str:
    """Tuần tự hóa dữ liệu thành JSON.

    Nếu :data:`~flask.current_app` có sẵn, nó sẽ sử dụng phương thức
    :meth:`app.json.dumps() <flask.json.provider.JSONProvider.dumps>`
    của nó, nếu không nó sẽ sử dụng :func:`json.dumps`.

    :param obj: Dữ liệu để tuần tự hóa.
    :param kwargs: Các đối số được truyền cho triển khai ``dumps``.

    .. versionchanged:: 2.3
        The ``app`` parameter was removed.

    .. versionchanged:: 2.2
        Calls ``current_app.json.dumps``, allowing an app to override
        the behavior.

    .. versionchanged:: 2.0.2
        :class:`decimal.Decimal` is supported by converting to a string.

    .. versionchanged:: 2.0
        ``encoding`` will be removed in Flask 2.1.

    .. versionchanged:: 1.0.3
        ``app`` can be passed directly, rather than requiring an app
        context for configuration.
    """
    if current_app:
        return current_app.json.dumps(obj, **kwargs)

    kwargs.setdefault("default", _default)
    return _json.dumps(obj, **kwargs)


def dump(obj: t.Any, fp: t.IO[str], **kwargs: t.Any) -> None:
    """Tuần tự hóa dữ liệu thành JSON và ghi vào một tệp.

    Nếu :data:`~flask.current_app` có sẵn, nó sẽ sử dụng phương thức
    :meth:`app.json.dump() <flask.json.provider.JSONProvider.dump>`
    của nó, nếu không nó sẽ sử dụng :func:`json.dump`.

    :param obj: Dữ liệu để tuần tự hóa.
    :param fp: Một tệp được mở để ghi văn bản. Nên sử dụng mã hóa UTF-8
        để là JSON hợp lệ.
    :param kwargs: Các đối số được truyền cho triển khai ``dump``.

    .. versionchanged:: 2.3
        The ``app`` parameter was removed.

    .. versionchanged:: 2.2
        Calls ``current_app.json.dump``, allowing an app to override
        the behavior.

    .. versionchanged:: 2.0
        Writing to a binary file, and the ``encoding`` argument, will be
        removed in Flask 2.1.
    """
    if current_app:
        current_app.json.dump(obj, fp, **kwargs)
    else:
        kwargs.setdefault("default", _default)
        _json.dump(obj, fp, **kwargs)


def loads(s: str | bytes, **kwargs: t.Any) -> t.Any:
    """Giải tuần tự hóa dữ liệu thành JSON.

    Nếu :data:`~flask.current_app` có sẵn, nó sẽ sử dụng phương thức
    :meth:`app.json.loads() <flask.json.provider.JSONProvider.loads>`
    của nó, nếu không nó sẽ sử dụng :func:`json.loads`.

    :param s: Văn bản hoặc byte UTF-8.
    :param kwargs: Các đối số được truyền cho triển khai ``loads``.

    .. versionchanged:: 2.3
        The ``app`` parameter was removed.

    .. versionchanged:: 2.2
        Calls ``current_app.json.loads``, allowing an app to override
        the behavior.

    .. versionchanged:: 2.0
        ``encoding`` will be removed in Flask 2.1. The data must be a
        string or UTF-8 bytes.

    .. versionchanged:: 1.0.3
        ``app`` can be passed directly, rather than requiring an app
        context for configuration.
    """
    if current_app:
        return current_app.json.loads(s, **kwargs)

    return _json.loads(s, **kwargs)


def load(fp: t.IO[t.AnyStr], **kwargs: t.Any) -> t.Any:
    """Giải tuần tự hóa dữ liệu thành JSON đọc từ một tệp.

    Nếu :data:`~flask.current_app` có sẵn, nó sẽ sử dụng phương thức
    :meth:`app.json.load() <flask.json.provider.JSONProvider.load>`
    của nó, nếu không nó sẽ sử dụng :func:`json.load`.

    :param fp: Một tệp được mở để đọc văn bản hoặc byte UTF-8.
    :param kwargs: Các đối số được truyền cho triển khai ``load``.

    .. versionchanged:: 2.3
        The ``app`` parameter was removed.

    .. versionchanged:: 2.2
        Calls ``current_app.json.load``, allowing an app to override
        the behavior.

    .. versionchanged:: 2.2
        The ``app`` parameter will be removed in Flask 2.3.

    .. versionchanged:: 2.0
        ``encoding`` will be removed in Flask 2.1. The file must be text
        mode, or binary mode with UTF-8 bytes.
    """
    if current_app:
        return current_app.json.load(fp, **kwargs)

    return _json.load(fp, **kwargs)


def jsonify(*args: t.Any, **kwargs: t.Any) -> Response:
    """Tuần tự hóa các đối số đã cho thành JSON, và trả về một
    đối tượng :class:`~flask.Response` với mimetype ``application/json``.
    Một dict hoặc list được trả về từ một view sẽ được chuyển đổi thành một
    phản hồi JSON tự động mà không cần phải gọi cái này.

    Điều này yêu cầu một ngữ cảnh ứng dụng đang hoạt động, và gọi
    :meth:`app.json.response() <flask.json.provider.JSONProvider.response>`.

    Trong chế độ debug, đầu ra được định dạng với thụt đầu dòng để làm cho nó
    dễ đọc hơn. Điều này cũng có thể được kiểm soát bởi provider.

    Hoặc đối số vị trí hoặc đối số từ khóa có thể được đưa ra, không phải cả hai.
    Nếu không có đối số nào được đưa ra, ``None`` được tuần tự hóa.

    :param args: Một giá trị duy nhất để tuần tự hóa, hoặc nhiều giá trị để
        xử lý như một danh sách để tuần tự hóa.
    :param kwargs: Xử lý như một dict để tuần tự hóa.

    .. versionchanged:: 2.2
        Calls ``current_app.json.response``, allowing an app to override
        the behavior.

    .. versionchanged:: 2.0.2
        :class:`decimal.Decimal` is supported by converting to a string.

    .. versionchanged:: 0.11
        Added support for serializing top-level arrays. This was a
        security risk in ancient browsers. See :ref:`security-json`.

    .. versionadded:: 0.2
    """
    return current_app.json.response(*args, **kwargs)  # type: ignore[return-value]
