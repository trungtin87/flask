from __future__ import annotations

import typing as t
from contextvars import ContextVar

from werkzeug.local import LocalProxy

if t.TYPE_CHECKING:  # pragma: no cover
    from .app import Flask
    from .ctx import _AppCtxGlobals
    from .ctx import AppContext
    from .sessions import SessionMixin
    from .wrappers import Request

    T = t.TypeVar("T", covariant=True)

    class ProxyMixin(t.Protocol[T]):
        def _get_current_object(self) -> T: ...

    # Các lớp con này thông báo cho trình kiểm tra kiểu rằng các đối tượng proxy trông giống như
    # loại được proxy cùng với phương thức _get_current_object.
    class FlaskProxy(ProxyMixin[Flask], Flask): ...

    class AppContextProxy(ProxyMixin[AppContext], AppContext): ...

    class _AppCtxGlobalsProxy(ProxyMixin[_AppCtxGlobals], _AppCtxGlobals): ...

    class RequestProxy(ProxyMixin[Request], Request): ...

    class SessionMixinProxy(ProxyMixin[SessionMixin], SessionMixin): ...


_no_app_msg = """\
Đang làm việc bên ngoài ngữ cảnh ứng dụng.

Đã cố gắng sử dụng chức năng mong đợi một ứng dụng hiện tại được thiết lập. Để
giải quyết vấn đề này, hãy thiết lập một ngữ cảnh ứng dụng bằng cách sử dụng 'with app.app_context()'. Xem
tài liệu về ngữ cảnh ứng dụng để biết thêm thông tin.\
"""
_cv_app: ContextVar[AppContext] = ContextVar("flask.app_ctx")
app_ctx: AppContextProxy = LocalProxy(  # type: ignore[assignment]
    _cv_app, unbound_message=_no_app_msg
)
current_app: FlaskProxy = LocalProxy(  # type: ignore[assignment]
    _cv_app, "app", unbound_message=_no_app_msg
)
g: _AppCtxGlobalsProxy = LocalProxy(  # type: ignore[assignment]
    _cv_app, "g", unbound_message=_no_app_msg
)

_no_req_msg = """\
Đang làm việc bên ngoài ngữ cảnh request.

Đã cố gắng sử dụng chức năng mong đợi một HTTP request đang hoạt động. Xem
tài liệu về ngữ cảnh request để biết thêm thông tin.\
"""
request: RequestProxy = LocalProxy(  # type: ignore[assignment]
    _cv_app, "request", unbound_message=_no_req_msg
)
session: SessionMixinProxy = LocalProxy(  # type: ignore[assignment]
    _cv_app, "session", unbound_message=_no_req_msg
)


def __getattr__(name: str) -> t.Any:
    import warnings

    if name == "request_ctx":
        warnings.warn(
            "'request_ctx' đã hợp nhất với 'app_ctx', và sẽ bị xóa"
            " trong Flask 4.0. Sử dụng 'app_ctx' thay thế.",
            DeprecationWarning,
            stacklevel=2,
        )
        return app_ctx

    raise AttributeError(name)
