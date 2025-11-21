from __future__ import annotations

import contextvars
import typing as t
from functools import update_wrapper
from types import TracebackType

from werkzeug.exceptions import HTTPException
from werkzeug.routing import MapAdapter

from . import typing as ft
from .globals import _cv_app
from .signals import appcontext_popped
from .signals import appcontext_pushed

if t.TYPE_CHECKING:
    import typing_extensions as te
    from _typeshed.wsgi import WSGIEnvironment

    from .app import Flask
    from .sessions import SessionMixin
    from .wrappers import Request


# một giá trị sentinel singleton cho các giá trị mặc định của tham số
_sentinel = object()


class _AppCtxGlobals:
    """Một đối tượng đơn giản. Được sử dụng như một namespace để lưu trữ dữ liệu trong
    ngữ cảnh ứng dụng.

    Việc tạo một ngữ cảnh ứng dụng sẽ tự động tạo đối tượng này, đối tượng này
    được cung cấp dưới dạng proxy :data:`.g`.

    .. describe:: 'key' in g

        Kiểm tra xem một thuộc tính có tồn tại hay không.

        .. versionadded:: 0.10

    .. describe:: iter(g)

        Trả về một iterator qua các tên thuộc tính.

        .. versionadded:: 0.10
    """

    # Định nghĩa các phương thức attr để cho mypy biết đây là một đối tượng namespace
    # có các thuộc tính tùy ý.

    def __getattr__(self, name: str) -> t.Any:
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError(name) from None

    def __setattr__(self, name: str, value: t.Any) -> None:
        self.__dict__[name] = value

    def __delattr__(self, name: str) -> None:
        try:
            del self.__dict__[name]
        except KeyError:
            raise AttributeError(name) from None

    def get(self, name: str, default: t.Any | None = None) -> t.Any:
        """Lấy một thuộc tính theo tên, hoặc một giá trị mặc định. Giống như
        :meth:`dict.get`.

        :param name: Tên của thuộc tính cần lấy.
        :param default: Giá trị trả về nếu thuộc tính không tồn tại.

        .. versionadded:: 0.10
        """
        return self.__dict__.get(name, default)

    def pop(self, name: str, default: t.Any = _sentinel) -> t.Any:
        """Lấy và xóa một thuộc tính theo tên. Giống như :meth:`dict.pop`.

        :param name: Tên của thuộc tính cần pop.
        :param default: Giá trị trả về nếu thuộc tính không tồn tại,
            thay vì ném ra ``KeyError``.

        .. versionadded:: 0.11
        """
        if default is _sentinel:
            return self.__dict__.pop(name)
        else:
            return self.__dict__.pop(name, default)

    def setdefault(self, name: str, default: t.Any = None) -> t.Any:
        """Lấy giá trị của một thuộc tính nếu nó tồn tại, nếu không
        thiết lập và trả về một giá trị mặc định. Giống như :meth:`dict.setdefault`.

        :param name: Tên của thuộc tính cần lấy.
        :param default: Giá trị để thiết lập và trả về nếu thuộc tính không
            tồn tại.

        .. versionadded:: 0.11
        """
        return self.__dict__.setdefault(name, default)

    def __contains__(self, item: str) -> bool:
        return item in self.__dict__

    def __iter__(self) -> t.Iterator[str]:
        return iter(self.__dict__)

    def __repr__(self) -> str:
        ctx = _cv_app.get(None)
        if ctx is not None:
            return f"<flask.g of '{ctx.app.name}'>"
        return object.__repr__(self)


def after_this_request(
    f: ft.AfterRequestCallable[t.Any],
) -> ft.AfterRequestCallable[t.Any]:
    """Trang trí một hàm để chạy sau request hiện tại. Hành vi là
    giống như :meth:`.Flask.after_request`, ngoại trừ việc nó chỉ áp dụng cho request
    hiện tại, thay vì mọi request. Do đó, nó phải được sử dụng trong một
    ngữ cảnh request, thay vì trong quá trình thiết lập.

    .. code-block:: python

        @app.route("/")
        def index():
            @after_this_request
            def add_header(response):
                response.headers["X-Foo"] = "Parachute"
                return response

            return "Hello, World!"

    .. versionadded:: 0.9
    """
    ctx = _cv_app.get(None)

    if ctx is None or not ctx.has_request:
        raise RuntimeError(
            "'after_this_request' can only be used when a request"
            " context is active, such as in a view function."
        )

    ctx._after_request_functions.append(f)
    return f


F = t.TypeVar("F", bound=t.Callable[..., t.Any])


def copy_current_request_context(f: F) -> F:
    """Trang trí một hàm để chạy bên trong ngữ cảnh request hiện tại. Điều này có thể
    được sử dụng khi bắt đầu một tác vụ nền, nếu không nó sẽ không thấy ứng dụng
    và các đối tượng request đã hoạt động trong cha.

    .. warning::

        Do những cảnh báo sau đây, thường an toàn hơn (và đơn giản hơn) để truyền
        dữ liệu bạn cần khi bắt đầu tác vụ, thay vì sử dụng cái này và
        dựa vào các đối tượng ngữ cảnh.

    Để tránh chuyển đổi thực thi một phần thông qua việc đọc dữ liệu, hoặc
    đọc body request (truy cập ``form``, ``json``, ``data``, v.v.) trước khi
    bắt đầu tác vụ, hoặc sử dụng một khóa. Điều này có thể là một vấn đề khi sử dụng threading,
    nhưng không nên là một vấn đề khi sử dụng greenlet/gevent hoặc asyncio.

    Nếu tác vụ sẽ truy cập ``session``, hãy chắc chắn làm như vậy trong cha cũng như
    để header ``Vary: cookie`` sẽ được thiết lập. Việc sửa đổi ``session`` trong
    tác vụ nên tránh, vì nó có thể thực thi sau khi cookie phản hồi đã
    được ghi.

    .. code-block:: python

        import gevent
        from flask import copy_current_request_context

        @app.route('/')
        def index():
            @copy_current_request_context
            def do_some_work():
                # do some work here, it can access flask.request or
                # flask.session like you would otherwise in the view function.
                ...
            gevent.spawn(do_some_work)
            return 'Regular response'

    .. versionadded:: 0.10
    """
    ctx = _cv_app.get(None)

    if ctx is None:
        raise RuntimeError(
            "'copy_current_request_context' can only be used when a"
            " request context is active, such as in a view function."
        )

    ctx = ctx.copy()

    def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
        with ctx:
            return ctx.app.ensure_sync(f)(*args, **kwargs)

    return update_wrapper(wrapper, f)  # type: ignore[return-value]


def has_request_context() -> bool:
    """Kiểm tra xem một ngữ cảnh ứng dụng có đang hoạt động và nếu nó có thông tin request.

    .. code-block:: python

        from flask import has_request_context, request

        if has_request_context():
            remote_addr = request.remote_addr

    Nếu một ngữ cảnh request đang hoạt động, các proxy ngữ cảnh :data:`.request` và :data:`.session`
    sẽ có sẵn và ``True``, nếu không thì ``False``. Bạn có thể
    sử dụng điều đó để kiểm tra dữ liệu bạn sử dụng, thay vì sử dụng hàm này.

    .. code-block:: python

        from flask import request

        if request:
            remote_addr = request.remote_addr

    .. versionadded:: 0.7
    """
    return (ctx := _cv_app.get(None)) is not None and ctx.has_request


def has_app_context() -> bool:
    """Kiểm tra xem một ngữ cảnh ứng dụng có đang hoạt động hay không. Không giống như :func:`has_request_context`
    điều này có thể đúng bên ngoài một request, chẳng hạn như trong một lệnh CLI.

    .. code-block:: python

        from flask import has_app_context, g

        if has_app_context():
            g.cached_data = ...

    Nếu một ngữ cảnh ứng dụng đang hoạt động, các proxy ngữ cảnh :data:`.g` và :data:`.current_app`
    sẽ có sẵn và ``True``, nếu không thì ``False``. Bạn có thể sử dụng điều đó
    để kiểm tra dữ liệu bạn sử dụng, thay vì sử dụng hàm này.

        from flask import g

        if g:
            g.cached_data = ...

    .. versionadded:: 0.9
    """
    return _cv_app.get(None) is not None


class AppContext:
    """Một ngữ cảnh ứng dụng chứa thông tin về một ứng dụng, và về request
    khi xử lý một request. Một ngữ cảnh được push ở đầu mỗi
    request và lệnh CLI, và pop ở cuối. Ngữ cảnh được gọi là
    "ngữ cảnh request" nếu nó có thông tin request, và "ngữ cảnh ứng dụng"
    nếu không.

    Không sử dụng lớp này trực tiếp. Sử dụng :meth:`.Flask.app_context` để tạo một
    ngữ cảnh ứng dụng nếu cần trong quá trình thiết lập, và :meth:`.Flask.test_request_context`
    để tạo một ngữ cảnh request nếu cần trong quá trình kiểm thử.

    Khi ngữ cảnh được pop, nó sẽ đánh giá tất cả các hàm teardown
    được đăng ký với :meth:`~flask.Flask.teardown_request` (nếu xử lý một
    request) sau đó :meth:`.Flask.teardown_appcontext`.

    Khi sử dụng trình gỡ lỗi tương tác, ngữ cảnh sẽ được khôi phục để
    ``request`` vẫn có thể truy cập được. Tương tự, test client có thể bảo tồn
    ngữ cảnh sau khi request kết thúc. Tuy nhiên, các hàm teardown có thể đã
    đóng một số tài nguyên như kết nối cơ sở dữ liệu, và sẽ chạy lại khi
    ngữ cảnh đã khôi phục được pop.

    :param app: Ứng dụng mà ngữ cảnh này đại diện.
    :param request: Dữ liệu request mà ngữ cảnh này đại diện.
    :param session: Dữ liệu session mà ngữ cảnh này đại diện. Nếu không được đưa ra,
        được tải từ request khi truy cập lần đầu.

    .. versionchanged:: 3.2
        Đã hợp nhất với ``RequestContext``. Alias ``RequestContext`` sẽ bị
        xóa trong Flask 4.0.

    .. versionchanged:: 3.2
        Một ngữ cảnh ứng dụng và request kết hợp được push cho mỗi request và lệnh CLI,
        thay vì cố gắng phát hiện xem một ngữ cảnh ứng dụng đã được
        push hay chưa.

    .. versionchanged:: 3.2
        Session được tải lần đầu tiên nó được truy cập, thay vì khi
        ngữ cảnh được push.
    """

    def __init__(
        self,
        app: Flask,
        *,
        request: Request | None = None,
        session: SessionMixin | None = None,
    ) -> None:
        self.app = app
        """Ứng dụng được đại diện bởi ngữ cảnh này. Được truy cập thông qua
        :data:`.current_app`.
        """

        self.g: _AppCtxGlobals = app.app_ctx_globals_class()
        """Dữ liệu toàn cục cho ngữ cảnh này. Được truy cập thông qua :data:`.g`."""

        self.url_adapter: MapAdapter | None = None
        """Bộ chuyển đổi URL bị ràng buộc với request, hoặc ứng dụng nếu không trong một request.
        Có thể là ``None`` nếu ràng buộc thất bại.
        """

        self._request: Request | None = request
        self._session: SessionMixin | None = session
        self._flashes: list[tuple[str, str]] | None = None
        self._after_request_functions: list[ft.AfterRequestCallable[t.Any]] = []

        try:
            self.url_adapter = app.create_url_adapter(self._request)
        except HTTPException as e:
            if self._request is not None:
                self._request.routing_exception = e

        self._cv_token: contextvars.Token[AppContext] | None = None
        """Trạng thái trước đó để khôi phục khi pop."""

        self._push_count: int = 0
        """Theo dõi các lần push lồng nhau của ngữ cảnh này. Dọn dẹp sẽ chỉ chạy một lần khi
        lần push ban đầu đã được pop.
        """

    @classmethod
    def from_environ(cls, app: Flask, environ: WSGIEnvironment, /) -> te.Self:
        """Tạo một ngữ cảnh ứng dụng với dữ liệu request từ WSGI environ đã cho.

        :param app: Ứng dụng mà ngữ cảnh này đại diện.
        :param environ: Dữ liệu request mà ngữ cảnh này đại diện.
        """
        request = app.request_class(environ)
        request.json_module = app.json
        return cls(app, request=request)

    @property
    def has_request(self) -> bool:
        """True nếu ngữ cảnh này được tạo với dữ liệu request."""
        return self._request is not None

    def copy(self) -> te.Self:
        """Tạo một ngữ cảnh mới với cùng các đối tượng dữ liệu như ngữ cảnh này. Xem
        :func:`.copy_current_request_context`.

        .. versionchanged:: 1.1
            Dữ liệu session hiện tại được sử dụng thay vì tải lại dữ liệu gốc.

        .. versionadded:: 0.10
        """
        return self.__class__(
            self.app,
            request=self._request,
            session=self._session,
        )

    @property
    def request(self) -> Request:
        """Đối tượng request được liên kết với ngữ cảnh này. Được truy cập thông qua
        :data:`.request`. Chỉ có sẵn trong các ngữ cảnh request, nếu không sẽ ném ra
        :exc:`RuntimeError`.
        """
        if self._request is None:
            raise RuntimeError("There is no request in this context.")

        return self._request

    @property
    def session(self) -> SessionMixin:
        """Đối tượng session được liên kết với ngữ cảnh này. Được truy cập thông qua
        :data:`.session`. Chỉ có sẵn trong các ngữ cảnh request, nếu không sẽ ném ra
        :exc:`RuntimeError`.
        """
        if self._request is None:
            raise RuntimeError("There is no request in this context.")

        if self._session is None:
            si = self.app.session_interface
            self._session = si.open_session(self.app, self.request)

            if self._session is None:
                self._session = si.make_null_session(self.app)

        return self._session

    def match_request(self) -> None:
        """Áp dụng routing cho request hiện tại, lưu trữ hoặc endpoint và args đã khớp,
        hoặc một ngoại lệ routing.
        """
        try:
            result = self.url_adapter.match(return_rule=True)  # type: ignore[union-attr]
        except HTTPException as e:
            self._request.routing_exception = e  # type: ignore[union-attr]
        else:
            self._request.url_rule, self._request.view_args = result  # type: ignore[union-attr]

    def push(self) -> None:
        """Push ngữ cảnh này để nó trở thành ngữ cảnh hoạt động. Nếu đây là một
        ngữ cảnh request, gọi :meth:`match_request` để thực hiện routing với
        ngữ cảnh đang hoạt động.

        Thông thường, điều này không được sử dụng trực tiếp. Thay vào đó, sử dụng một khối ``with``
        để quản lý ngữ cảnh.

        Trong một số tình huống, chẳng hạn như streaming hoặc testing, ngữ cảnh có thể được
        push nhiều lần. Nó sẽ chỉ kích hoạt matching và signals nếu nó
        hiện không được push.
        """
        self._push_count += 1

        if self._cv_token is not None:
            return

        self._cv_token = _cv_app.set(self)
        appcontext_pushed.send(self.app, _async_wrapper=self.app.ensure_sync)

        if self._request is not None and self.url_adapter is not None:
            self.match_request()

    def pop(self, exc: BaseException | None = None) -> None:
        """Pop ngữ cảnh này để nó không còn là ngữ cảnh hoạt động nữa. Sau đó
        gọi các hàm teardown và signals.

        Thông thường, điều này không được sử dụng trực tiếp. Thay vào đó, sử dụng một khối ``with``
        để quản lý ngữ cảnh.

        Ngữ cảnh này hiện phải là ngữ cảnh hoạt động, nếu không một
        :exc:`RuntimeError` sẽ được ném ra. Trong một số tình huống, chẳng hạn như streaming hoặc
        testing, ngữ cảnh có thể đã được push nhiều lần. Nó sẽ chỉ
        kích hoạt dọn dẹp một lần khi nó đã được pop nhiều lần như nó đã được push.
        Cho đến lúc đó, nó sẽ vẫn là ngữ cảnh hoạt động.

        :param exc: Một ngoại lệ không được xử lý đã được ném ra trong khi ngữ cảnh đang
            hoạt động. Được truyền cho các hàm teardown.

        .. versionchanged:: 0.9
            Đã thêm đối số ``exc``.
        """
        if self._cv_token is None:
            raise RuntimeError(f"Cannot pop this context ({self!r}), it is not pushed.")

        ctx = _cv_app.get(None)

        if ctx is None or self._cv_token is None:
            raise RuntimeError(
                f"Cannot pop this context ({self!r}), there is no active context."
            )

        if ctx is not self:
            raise RuntimeError(
                f"Cannot pop this context ({self!r}), it is not the active"
                f" context ({ctx!r})."
            )

        self._push_count -= 1

        if self._push_count > 0:
            return

        try:
            if self._request is not None:
                self.app.do_teardown_request(exc)
                self._request.close()
        finally:
            self.app.do_teardown_appcontext(exc)
            _cv_app.reset(self._cv_token)
            self._cv_token = None
            appcontext_popped.send(self.app, _async_wrapper=self.app.ensure_sync)

    def __enter__(self) -> te.Self:
        self.push()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.pop(exc_value)

    def __repr__(self) -> str:
        if self._request is not None:
            return (
                f"<{type(self).__name__} {id(self)} of {self.app.name},"
                f" {self.request.method} {self.request.url!r}>"
            )

        return f"<{type(self).__name__} {id(self)} of {self.app.name}>"


def __getattr__(name: str) -> t.Any:
    import warnings

    if name == "RequestContext":
        warnings.warn(
            "'RequestContext' has merged with 'AppContext', and will be removed"
            " in Flask 4.0. Use 'AppContext' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return AppContext

    raise AttributeError(name)
