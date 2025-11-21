from __future__ import annotations

import importlib.util
import os
import sys
import typing as t
from datetime import datetime
from functools import cache
from functools import update_wrapper

import werkzeug.utils
from werkzeug.exceptions import abort as _wz_abort
from werkzeug.utils import redirect as _wz_redirect
from werkzeug.wrappers import Response as BaseResponse

from .globals import _cv_app
from .globals import app_ctx
from .globals import current_app
from .globals import request
from .globals import session
from .signals import message_flashed

if t.TYPE_CHECKING:  # pragma: no cover
    from .wrappers import Response


def get_debug_flag() -> bool:
    """Lấy xem chế độ debug có nên được bật cho ứng dụng hay không, được chỉ định bởi
    biến môi trường :envvar:`FLASK_DEBUG`. Mặc định là ``False``.
    """
    val = os.environ.get("FLASK_DEBUG")
    return bool(val and val.lower() not in {"0", "false", "no"})


def get_load_dotenv(default: bool = True) -> bool:
    """Lấy xem người dùng có tắt việc tải các tệp dotenv mặc định hay không bằng cách
    thiết lập :envvar:`FLASK_SKIP_DOTENV`. Mặc định là ``True``, tải
    các tệp.

    :param default: Cái gì để trả về nếu biến môi trường không được thiết lập.
    """
    val = os.environ.get("FLASK_SKIP_DOTENV")

    if not val:
        return default

    return val.lower() in ("0", "false", "no")


@t.overload
def stream_with_context(
    generator_or_function: t.Iterator[t.AnyStr],
) -> t.Iterator[t.AnyStr]: ...


@t.overload
def stream_with_context(
    generator_or_function: t.Callable[..., t.Iterator[t.AnyStr]],
) -> t.Callable[[t.Iterator[t.AnyStr]], t.Iterator[t.AnyStr]]: ...


def stream_with_context(
    generator_or_function: t.Iterator[t.AnyStr] | t.Callable[..., t.Iterator[t.AnyStr]],
) -> t.Iterator[t.AnyStr] | t.Callable[[t.Iterator[t.AnyStr]], t.Iterator[t.AnyStr]]:
    """Bọc một hàm generator phản hồi để nó chạy bên trong ngữ cảnh request
    hiện tại. Điều này giữ cho :data:`.request`, :data:`.session`, và :data:`.g`
    có sẵn, mặc dù tại thời điểm generator chạy ngữ cảnh request
    thường sẽ đã kết thúc.

    Sử dụng nó như một decorator trên một hàm generator:

    .. code-block:: python

        from flask import stream_with_context, request, Response

        @app.get("/stream")
        def streamed_response():
            @stream_with_context
            def generate():
                yield "Hello "
                yield request.args["name"]
                yield "!"

            return Response(generate())

    Hoặc sử dụng nó như một wrapper xung quanh một generator đã tạo:

    .. code-block:: python

        from flask import stream_with_context, request, Response

        @app.get("/stream")
        def streamed_response():
            def generate():
                yield "Hello "
                yield request.args["name"]
                yield "!"

            return Response(stream_with_context(generate()))

    .. versionadded:: 0.9
    """
    try:
        gen = iter(generator_or_function)  # type: ignore[arg-type]
    except TypeError:

        def decorator(*args: t.Any, **kwargs: t.Any) -> t.Any:
            gen = generator_or_function(*args, **kwargs)  # type: ignore[operator]
            return stream_with_context(gen)

        return update_wrapper(decorator, generator_or_function)  # type: ignore[arg-type]

    def generator() -> t.Iterator[t.AnyStr]:
        if (ctx := _cv_app.get(None)) is None:
            raise RuntimeError(
                "'stream_with_context' chỉ có thể được sử dụng khi một ngữ cảnh"
                " request đang hoạt động, chẳng hạn như trong một hàm view."
            )

        with ctx:
            yield None  # type: ignore[misc]

            try:
                yield from gen
            finally:
                # Dọn dẹp trong trường hợp người dùng đã bọc một WSGI iterator.
                if hasattr(gen, "close"):
                    gen.close()

    # Thực thi generator đến giá trị sentinel. Điều này bắt giữ ngữ cảnh
    # hiện tại và push nó để bảo tồn nó. Việc lặp lại thêm sẽ yield từ
    # iterator ban đầu.
    wrapped_g = generator()
    next(wrapped_g)
    return wrapped_g


def make_response(*args: t.Any) -> Response:
    """Đôi khi cần thiết để thiết lập các header bổ sung trong một view. Vì
    các view không cần phải trả về các đối tượng response mà có thể trả về một giá trị
    được chuyển đổi thành một đối tượng response bởi chính Flask, nên việc thêm
    các header vào nó trở nên khó khăn. Hàm này có thể được gọi thay vì sử dụng return
    và bạn sẽ nhận được một đối tượng response mà bạn có thể sử dụng để đính kèm các header.

    Nếu view trông giống như thế này và bạn muốn thêm một header mới::

        def index():
            return render_template('index.html', foo=42)

    Bây giờ bạn có thể làm một cái gì đó như thế này::

        def index():
            response = make_response(render_template('index.html', foo=42))
            response.headers['X-Parachutes'] = 'parachutes are cool'
            return response

    Hàm này chấp nhận các đối số giống hệt như bạn có thể trả về từ một
    hàm view. Ví dụ này tạo một response với mã lỗi 404::

        response = make_response(render_template('not_found.html'), 404)

    Trường hợp sử dụng khác của hàm này là ép buộc giá trị trả về của một
    hàm view thành một response, điều này hữu ích với các decorator
    view::

        response = make_response(view_function())
        response.headers['X-Parachutes'] = 'parachutes are cool'

    Bên trong hàm này thực hiện những việc sau:

    -   nếu không có đối số nào được truyền, nó tạo một đối số response mới
    -   nếu một đối số được truyền, :meth:`flask.Flask.make_response`
        được gọi với nó.
    -   nếu nhiều hơn một đối số được truyền, các đối số được truyền
        cho hàm :meth:`flask.Flask.make_response` dưới dạng tuple.

    .. versionadded:: 0.6
    """
    if not args:
        return current_app.response_class()
    if len(args) == 1:
        args = args[0]
    return current_app.make_response(args)


def url_for(
    endpoint: str,
    *,
    _anchor: str | None = None,
    _method: str | None = None,
    _scheme: str | None = None,
    _external: bool | None = None,
    **values: t.Any,
) -> str:
    """Tạo một URL đến endpoint đã cho với các giá trị đã cho.

    Điều này yêu cầu một ngữ cảnh request hoặc ứng dụng đang hoạt động, và gọi
    :meth:`current_app.url_for() <flask.Flask.url_for>`. Xem phương thức đó
    để biết tài liệu đầy đủ.

    :param endpoint: Tên endpoint được liên kết với URL để
        tạo. Nếu cái này bắt đầu bằng một ``.``, tên blueprint hiện tại
        (nếu có) sẽ được sử dụng.
    :param _anchor: Nếu được đưa ra, thêm cái này dưới dạng ``#anchor`` vào URL.
    :param _method: Nếu được đưa ra, tạo URL được liên kết với phương thức này
        cho endpoint.
    :param _scheme: Nếu được đưa ra, URL sẽ có scheme này nếu nó là
        external.
    :param _external: Nếu được đưa ra, ưu tiên URL là nội bộ (False) hoặc
        yêu cầu nó là bên ngoài (True). Các URL bên ngoài bao gồm
        scheme và domain. Khi không ở trong một request đang hoạt động, các URL là
        bên ngoài theo mặc định.
    :param values: Các giá trị để sử dụng cho các phần biến của quy tắc URL.
        Các khóa không xác định được thêm vào dưới dạng đối số query string, giống như
        ``?a=b&c=d``.

    .. versionchanged:: 2.2
        Gọi ``current_app.url_for``, cho phép một ứng dụng ghi đè
        hành vi.

    .. versionchanged:: 0.10
       Tham số ``_scheme`` đã được thêm vào.

    .. versionchanged:: 0.9
       Các tham số ``_anchor`` và ``_method`` đã được thêm vào.

    .. versionchanged:: 0.9
       Gọi ``app.handle_url_build_error`` khi có lỗi build.
    """
    return current_app.url_for(
        endpoint,
        _anchor=_anchor,
        _method=_method,
        _scheme=_scheme,
        _external=_external,
        **values,
    )


def redirect(
    location: str, code: int = 302, Response: type[BaseResponse] | None = None
) -> BaseResponse:
    """Tạo một đối tượng response chuyển hướng.

    Nếu :data:`~flask.current_app` có sẵn, nó sẽ sử dụng phương thức
    :meth:`~flask.Flask.redirect` của nó, nếu không nó sẽ sử dụng
    :func:`werkzeug.utils.redirect`.

    :param location: URL để chuyển hướng đến.
    :param code: Mã trạng thái cho chuyển hướng.
    :param Response: Lớp response để sử dụng. Không được sử dụng khi
        ``current_app`` đang hoạt động, cái mà sử dụng ``app.response_class``.

    .. versionadded:: 2.2
        Gọi ``current_app.redirect`` nếu có sẵn thay vì luôn luôn
        sử dụng ``redirect`` mặc định của Werkzeug.
    """
    if (ctx := _cv_app.get(None)) is not None:
        return ctx.app.redirect(location, code=code)

    return _wz_redirect(location, code=code, Response=Response)


def abort(code: int | BaseResponse, *args: t.Any, **kwargs: t.Any) -> t.NoReturn:
    """Ném ra một :exc:`~werkzeug.exceptions.HTTPException` cho mã trạng thái
    đã cho.

    Nếu :data:`~flask.current_app` có sẵn, nó sẽ gọi đối tượng
    :attr:`~flask.Flask.aborter` của nó, nếu không nó sẽ sử dụng
    :func:`werkzeug.exceptions.abort`.

    :param code: Mã trạng thái cho ngoại lệ, cái mà phải được
        đăng ký trong ``app.aborter``.
    :param args: Được truyền cho ngoại lệ.
    :param kwargs: Được truyền cho ngoại lệ.

    .. versionadded:: 2.2
        Gọi ``current_app.aborter`` nếu có sẵn thay vì luôn luôn
        sử dụng ``abort`` mặc định của Werkzeug.
    """
    if (ctx := _cv_app.get(None)) is not None:
        ctx.app.aborter(code, *args, **kwargs)

    _wz_abort(code, *args, **kwargs)


def get_template_attribute(template_name: str, attribute: str) -> t.Any:
    """Tải một macro (hoặc biến) mà một template xuất ra. Điều này có thể được sử dụng để
    gọi một macro từ bên trong mã Python. Nếu bạn ví dụ có một
    template tên là :file:`_cider.html` với nội dung sau:

    .. sourcecode:: html+jinja

       {% macro hello(name) %}Hello {{ name }}!{% endmacro %}

    Bạn có thể truy cập cái này từ mã Python như thế này::

        hello = get_template_attribute('_cider.html', 'hello')
        return hello('World')

    .. versionadded:: 0.2

    :param template_name: tên của template
    :param attribute: tên của biến hoặc macro để truy cập
    """
    return getattr(current_app.jinja_env.get_template(template_name).module, attribute)


def flash(message: str, category: str = "message") -> None:
    """Flash một thông báo đến request tiếp theo. Để xóa thông báo
    đã flash khỏi session và hiển thị nó cho người dùng,
    template phải gọi :func:`get_flashed_messages`.

    .. versionchanged:: 0.3
       Tham số `category` đã được thêm vào.

    :param message: thông báo để flash.
    :param category: danh mục cho thông báo. Các giá trị sau đây
                     được khuyến nghị: ``'message'`` cho bất kỳ loại thông báo nào,
                     ``'error'`` cho lỗi, ``'info'`` cho thông báo thông tin
                     và ``'warning'`` cho cảnh báo. Tuy nhiên bất kỳ
                     loại chuỗi nào cũng có thể được sử dụng làm danh mục.
    """
    # Triển khai ban đầu:
    #
    #     session.setdefault('_flashes', []).append((category, message))
    #
    # Điều này giả định rằng các thay đổi được thực hiện đối với các cấu trúc có thể thay đổi trong session luôn
    # đồng bộ với đối tượng session, điều này không đúng đối với các triển khai
    # session sử dụng lưu trữ bên ngoài để giữ các khóa/giá trị của chúng.
    flashes = session.get("_flashes", [])
    flashes.append((category, message))
    session["_flashes"] = flashes
    app = current_app._get_current_object()
    message_flashed.send(
        app,
        _async_wrapper=app.ensure_sync,
        message=message,
        category=category,
    )


def get_flashed_messages(
    with_categories: bool = False, category_filter: t.Iterable[str] = ()
) -> list[str] | list[tuple[str, str]]:
    """Lấy tất cả các thông báo đã flash từ session và trả về chúng.
    Các cuộc gọi tiếp theo trong cùng một request đến hàm sẽ trả về
    cùng các thông báo. Theo mặc định chỉ các thông báo được trả về,
    nhưng khi `with_categories` được đặt thành ``True``, giá trị trả về sẽ
    là một danh sách các tuple ở dạng ``(category, message)`` thay thế.

    Lọc các thông báo đã flash theo một hoặc nhiều danh mục bằng cách cung cấp các
    danh mục đó trong `category_filter`. Điều này cho phép render các danh mục trong
    các khối html riêng biệt. Các đối số `with_categories` và `category_filter`
    là riêng biệt:

    * `with_categories` kiểm soát xem các danh mục có được trả về cùng với văn bản
      thông báo hay không (``True`` đưa ra một tuple, trong khi ``False`` chỉ đưa ra văn bản thông báo).
    * `category_filter` lọc các thông báo xuống chỉ những thông báo khớp với các
      danh mục đã cung cấp.

    Xem :doc:`/patterns/flashing` để biết các ví dụ.

    .. versionchanged:: 0.3
       Tham số `with_categories` đã được thêm vào.

    .. versionchanged:: 0.9
        Tham số `category_filter` đã được thêm vào.

    :param with_categories: đặt thành ``True`` để cũng nhận các danh mục.
    :param category_filter: bộ lọc các danh mục để giới hạn các giá trị trả về. Chỉ
                            các danh mục trong danh sách sẽ được trả về.
    """
    flashes = app_ctx._flashes
    if flashes is None:
        flashes = session.pop("_flashes") if "_flashes" in session else []
        app_ctx._flashes = flashes
    if category_filter:
        flashes = list(filter(lambda f: f[0] in category_filter, flashes))
    if not with_categories:
        return [x[1] for x in flashes]
    return flashes


def _prepare_send_file_kwargs(**kwargs: t.Any) -> dict[str, t.Any]:
    ctx = app_ctx._get_current_object()

    if kwargs.get("max_age") is None:
        kwargs["max_age"] = ctx.app.get_send_file_max_age

    kwargs.update(
        environ=ctx.request.environ,
        use_x_sendfile=ctx.app.config["USE_X_SENDFILE"],
        response_class=ctx.app.response_class,
        _root_path=ctx.app.root_path,
    )
    return kwargs


def send_file(
    path_or_file: os.PathLike[t.AnyStr] | str | t.IO[bytes],
    mimetype: str | None = None,
    as_attachment: bool = False,
    download_name: str | None = None,
    conditional: bool = True,
    etag: bool | str = True,
    last_modified: datetime | int | float | None = None,
    max_age: None | (int | t.Callable[[str | None], int | None]) = None,
) -> Response:
    """Gửi nội dung của một tệp đến client.

    Đối số đầu tiên có thể là một đường dẫn tệp hoặc một đối tượng giống tệp. Các đường dẫn
    được ưu tiên trong hầu hết các trường hợp vì Werkzeug có thể quản lý tệp và
    lấy thêm thông tin từ đường dẫn. Truyền một đối tượng giống tệp
    yêu cầu tệp phải được mở ở chế độ nhị phân, và chủ yếu
    hữu ích khi xây dựng một tệp trong bộ nhớ với :class:`io.BytesIO`.

    Không bao giờ truyền các đường dẫn tệp được cung cấp bởi người dùng. Đường dẫn được giả định là
    đáng tin cậy, vì vậy người dùng có thể tạo ra một đường dẫn để truy cập một tệp bạn không
    có ý định. Sử dụng :func:`send_from_directory` để phục vụ an toàn
    các đường dẫn được yêu cầu bởi người dùng từ bên trong một thư mục.

    Nếu server WSGI thiết lập một ``file_wrapper`` trong ``environ``, nó được
    sử dụng, nếu không wrapper tích hợp của Werkzeug được sử dụng. Thay vào đó,
    nếu server HTTP hỗ trợ ``X-Sendfile``, cấu hình Flask với
    ``USE_X_SENDFILE = True`` sẽ bảo server gửi đường dẫn đã cho,
    điều này hiệu quả hơn nhiều so với việc đọc nó trong Python.

    :param path_or_file: Đường dẫn đến tệp để gửi, tương đối với
        thư mục làm việc hiện tại nếu một đường dẫn tương đối được đưa ra.
        Thay vào đó, một đối tượng giống tệp được mở ở chế độ nhị phân. Hãy chắc chắn
        rằng con trỏ tệp được seek đến đầu dữ liệu.
    :param mimetype: Loại MIME để gửi cho tệp. Nếu không được
        cung cấp, nó sẽ cố gắng phát hiện nó từ tên tệp.
    :param as_attachment: Chỉ ra cho trình duyệt rằng nó nên đề nghị
        lưu tệp thay vì hiển thị nó.
    :param download_name: Tên mặc định mà các trình duyệt sẽ sử dụng khi lưu
        tệp. Mặc định là tên tệp đã truyền.
    :param conditional: Bật các phản hồi có điều kiện và phạm vi dựa trên
        các header request. Yêu cầu truyền một đường dẫn tệp và ``environ``.
    :param etag: Tính toán một ETag cho tệp, điều này yêu cầu truyền
        một đường dẫn tệp. Cũng có thể là một chuỗi để sử dụng thay thế.
    :param last_modified: Thời gian sửa đổi cuối cùng để gửi cho tệp,
        tính bằng giây. Nếu không được cung cấp, nó sẽ cố gắng phát hiện nó từ
        đường dẫn tệp.
    :param max_age: Thời gian client nên cache tệp, tính bằng
        giây. Nếu được thiết lập, ``Cache-Control`` sẽ là ``public``, nếu không
        nó sẽ là ``no-cache`` để ưu tiên caching có điều kiện.

    .. versionchanged:: 2.0
        ``download_name`` thay thế tham số ``attachment_filename``.
        Nếu ``as_attachment=False``, nó được truyền với
        ``Content-Disposition: inline`` thay thế.

    .. versionchanged:: 2.0
        ``max_age`` thay thế tham số ``cache_timeout``.
        ``conditional`` được bật và ``max_age`` không được thiết lập theo
        mặc định.

    .. versionchanged:: 2.0
        ``etag`` thay thế tham số ``add_etags``. Nó có thể là một
        chuỗi để sử dụng thay vì tạo ra một cái.

    .. versionchanged:: 2.0
        Truyền một đối tượng giống tệp kế thừa từ
        :class:`~io.TextIOBase` sẽ ném ra một :exc:`ValueError` thay vì
        gửi một tệp trống.

    .. versionadded:: 2.0
        Đã di chuyển triển khai sang Werkzeug. Đây hiện là một wrapper để
        truyền một số đối số cụ thể của Flask.

    .. versionchanged:: 1.1
        ``filename`` có thể là một đối tượng :class:`~os.PathLike`.

    .. versionchanged:: 1.1
        Truyền một đối tượng :class:`~io.BytesIO` hỗ trợ các request phạm vi.

    .. versionchanged:: 1.0.3
        Tên tệp được mã hóa bằng ASCII thay vì Latin-1 để tương thích
        rộng hơn với các server WSGI.

    .. versionchanged:: 1.0
        Tên tệp UTF-8 như được chỉ định trong :rfc:`2231` được hỗ trợ.

    .. versionchanged:: 0.12
        Tên tệp không còn được tự động suy ra từ các đối tượng
        tệp. Nếu bạn muốn sử dụng hỗ trợ MIME và etag tự động,
        hãy truyền một tên tệp qua ``filename_or_fp`` hoặc
        ``attachment_filename``.

    .. versionchanged:: 0.12
        ``attachment_filename`` được ưu tiên hơn ``filename`` cho phát hiện
        MIME.

    .. versionchanged:: 0.9
        ``cache_timeout`` mặc định là
        :meth:`Flask.get_send_file_max_age`.

    .. versionchanged:: 0.7
        Đoán MIME và hỗ trợ etag cho các đối tượng giống tệp đã bị
        xóa vì nó không đáng tin cậy. Truyền một tên tệp nếu bạn có thể,
        nếu không hãy tự đính kèm một etag.

    .. versionchanged:: 0.5
        Các tham số ``add_etags``, ``cache_timeout`` và ``conditional``
        đã được thêm vào. Hành vi mặc định là thêm etags.

    .. versionadded:: 0.2
    """
    return werkzeug.utils.send_file(  # type: ignore[return-value]
        **_prepare_send_file_kwargs(
            path_or_file=path_or_file,
            environ=request.environ,
            mimetype=mimetype,
            as_attachment=as_attachment,
            download_name=download_name,
            conditional=conditional,
            etag=etag,
            last_modified=last_modified,
            max_age=max_age,
        )
    )


def send_from_directory(
    directory: os.PathLike[str] | str,
    path: os.PathLike[str] | str,
    **kwargs: t.Any,
) -> Response:
    """Gửi một tệp từ bên trong một thư mục sử dụng :func:`send_file`.

    .. code-block:: python

        @app.route("/uploads/<path:name>")
        def download_file(name):
            return send_from_directory(
                app.config['UPLOAD_FOLDER'], name, as_attachment=True
            )

    Đây là một cách an toàn để phục vụ các tệp từ một thư mục, chẳng hạn như các tệp
    tĩnh hoặc các tệp tải lên. Sử dụng :func:`~werkzeug.security.safe_join` để
    đảm bảo đường dẫn đến từ client không được tạo ra một cách độc hại để
    trỏ ra bên ngoài thư mục đã chỉ định.

    Nếu đường dẫn cuối cùng không trỏ đến một tệp thông thường hiện có,
    ném ra một lỗi 404 :exc:`~werkzeug.exceptions.NotFound`.

    :param directory: Thư mục mà ``path`` phải nằm dưới đó,
        tương đối với đường dẫn gốc của ứng dụng hiện tại. Giá trị này *không được*
        là một giá trị được cung cấp bởi client, nếu không nó trở nên không an toàn.
    :param path: Đường dẫn đến tệp để gửi, tương đối với
        ``directory``.
    :param kwargs: Các đối số để truyền cho :func:`send_file`.

    .. versionchanged:: 2.0
        ``path`` thay thế tham số ``filename``.

    .. versionadded:: 2.0
        Đã di chuyển triển khai sang Werkzeug. Đây hiện là một wrapper để
        truyền một số đối số cụ thể của Flask.

    .. versionadded:: 0.5
    """
    return werkzeug.utils.send_from_directory(  # type: ignore[return-value]
        directory, path, **_prepare_send_file_kwargs(**kwargs)
    )


def get_root_path(import_name: str) -> str:
    """Tìm đường dẫn gốc của một gói, hoặc đường dẫn chứa một
    module. Nếu nó không thể được tìm thấy, trả về thư mục làm việc
    hiện tại.

    Không nhầm lẫn với giá trị được trả về bởi :func:`find_package`.

    :meta private:
    """
    # Module đã được import và có thuộc tính file. Sử dụng cái đó trước.
    mod = sys.modules.get(import_name)

    if mod is not None and hasattr(mod, "__file__") and mod.__file__ is not None:
        return os.path.dirname(os.path.abspath(mod.__file__))

    # Nỗ lực tiếp theo: kiểm tra loader.
    try:
        spec = importlib.util.find_spec(import_name)

        if spec is None:
            raise ValueError
    except (ImportError, ValueError):
        loader = None
    else:
        loader = spec.loader

    # Loader không tồn tại hoặc chúng ta đang tham chiếu đến một module chính chưa tải
    # hoặc một module chính không có đường dẫn (các phiên tương tác), đi
    # với thư mục làm việc hiện tại.
    if loader is None:
        return os.getcwd()

    if hasattr(loader, "get_filename"):
        filepath = loader.get_filename(import_name)  # pyright: ignore
    else:
        # Quay lại imports.
        __import__(import_name)
        mod = sys.modules[import_name]
        filepath = getattr(mod, "__file__", None)

        # Nếu chúng ta không có đường dẫn tệp, có thể là do nó là một
        # namespace package. Trong trường hợp này chọn đường dẫn gốc từ
        # module đầu tiên được chứa trong gói.
        if filepath is None:
            raise RuntimeError(
                "Không thể tìm thấy đường dẫn gốc cho module đã cung cấp"
                f" {import_name!r}. Điều này có thể xảy ra vì module"
                " đến từ một import hook không cung cấp thông tin tên"
                " tệp hoặc vì nó là một namespace package."
                " Trong trường hợp này đường dẫn gốc cần được cung cấp"
                " một cách rõ ràng."
            )

    # filepath là import_name.py cho một module, hoặc __init__.py cho một gói.
    return os.path.dirname(os.path.abspath(filepath))  # type: ignore[no-any-return]


@cache
def _split_blueprint_path(name: str) -> list[str]:
    out: list[str] = [name]

    if "." in name:
        out.extend(_split_blueprint_path(name.rpartition(".")[0]))

    return out
