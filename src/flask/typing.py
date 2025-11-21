from __future__ import annotations

import collections.abc as cabc
import typing as t

if t.TYPE_CHECKING:  # pragma: no cover
    from _typeshed.wsgi import WSGIApplication  # noqa: F401
    from werkzeug.datastructures import Headers  # noqa: F401
    from werkzeug.sansio.response import Response  # noqa: F401

# Các loại có thể chuyển đổi trực tiếp hoặc là một đối tượng Response.
ResponseValue = t.Union[
    "Response",
    str,
    bytes,
    list[t.Any],
    # Chỉ dict thực sự được chấp nhận, nhưng Mapping cho phép TypedDict.
    t.Mapping[str, t.Any],
    t.Iterator[str],
    t.Iterator[bytes],
    cabc.AsyncIterable[str],  # for Quart, until App is generic.
    cabc.AsyncIterable[bytes],
]

# các loại có thể cho một HTTP header riêng lẻ
HeaderValue = str | list[str] | tuple[str, ...]

# các loại có thể cho các HTTP header
HeadersValue = t.Union[
    "Headers",
    t.Mapping[str, HeaderValue],
    t.Sequence[tuple[str, HeaderValue]],
]

# Các loại có thể được trả về bởi một hàm route.
ResponseReturnValue = t.Union[
    ResponseValue,
    tuple[ResponseValue, HeadersValue],
    tuple[ResponseValue, int],
    tuple[ResponseValue, int, HeadersValue],
    "WSGIApplication",
]

# Cho phép bất kỳ lớp con nào của werkzeug.Response, chẳng hạn như lớp từ Flask,
# làm đối số callback. Sử dụng werkzeug.Response trực tiếp làm cho một
# callback được chú thích với flask.Response thất bại kiểm tra kiểu.
ResponseClass = t.TypeVar("ResponseClass", bound="Response")

AppOrBlueprintKey = str | None  # Khóa App là None, trong khi các blueprint được đặt tên
AfterRequestCallable = (
    t.Callable[[ResponseClass], ResponseClass]
    | t.Callable[[ResponseClass], t.Awaitable[ResponseClass]]
)
BeforeFirstRequestCallable = t.Callable[[], None] | t.Callable[[], t.Awaitable[None]]
BeforeRequestCallable = (
    t.Callable[[], ResponseReturnValue | None]
    | t.Callable[[], t.Awaitable[ResponseReturnValue | None]]
)
ShellContextProcessorCallable = t.Callable[[], dict[str, t.Any]]
TeardownCallable = (
    t.Callable[[BaseException | None], None]
    | t.Callable[[BaseException | None], t.Awaitable[None]]
)
TemplateContextProcessorCallable = (
    t.Callable[[], dict[str, t.Any]] | t.Callable[[], t.Awaitable[dict[str, t.Any]]]
)
TemplateFilterCallable = t.Callable[..., t.Any]
TemplateGlobalCallable = t.Callable[..., t.Any]
TemplateTestCallable = t.Callable[..., bool]
URLDefaultCallable = t.Callable[[str, dict[str, t.Any]], None]
URLValuePreprocessorCallable = t.Callable[[str | None, dict[str, t.Any] | None], None]

# Cái này nên nhận Exception, nhưng điều đó hoặc phá vỡ việc gõ đối số
# với một ngoại lệ cụ thể, hoặc trang trí nhiều lần với các ngoại lệ
# khác nhau (và sử dụng một loại union trên đối số).
# https://github.com/pallets/flask/issues/4095
# https://github.com/pallets/flask/issues/4295
# https://github.com/pallets/flask/issues/4297
ErrorHandlerCallable = (
    t.Callable[[t.Any], ResponseReturnValue]
    | t.Callable[[t.Any], t.Awaitable[ResponseReturnValue]]
)

RouteCallable = (
    t.Callable[..., ResponseReturnValue]
    | t.Callable[..., t.Awaitable[ResponseReturnValue]]
)
