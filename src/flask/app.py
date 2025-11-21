from __future__ import annotations

import collections.abc as cabc
import os
import sys
import typing as t
import weakref
from datetime import timedelta
from inspect import iscoroutinefunction
from itertools import chain
from types import TracebackType
from urllib.parse import quote as _url_quote

import click
from werkzeug.datastructures import Headers
from werkzeug.datastructures import ImmutableDict
from werkzeug.exceptions import BadRequestKeyError
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import InternalServerError
from werkzeug.routing import BuildError
from werkzeug.routing import MapAdapter
from werkzeug.routing import RequestRedirect
from werkzeug.routing import RoutingException
from werkzeug.routing import Rule
from werkzeug.serving import is_running_from_reloader
from werkzeug.wrappers import Response as BaseResponse
from werkzeug.wsgi import get_host

from . import cli
from . import typing as ft
from .ctx import AppContext
from .globals import _cv_app
from .globals import g
from .globals import request
from .globals import session
from .helpers import get_debug_flag
from .helpers import get_flashed_messages
from .helpers import get_load_dotenv
from .helpers import send_from_directory
from .sansio.app import App
from .sessions import SecureCookieSessionInterface
from .sessions import SessionInterface
from .signals import appcontext_tearing_down
from .signals import got_request_exception
from .signals import request_finished
from .signals import request_started
from .signals import request_tearing_down
from .templating import Environment
from .wrappers import Request
from .wrappers import Response

if t.TYPE_CHECKING:  # pragma: no cover
    from _typeshed.wsgi import StartResponse
    from _typeshed.wsgi import WSGIEnvironment

    from .testing import FlaskClient
    from .testing import FlaskCliRunner
    from .typing import HeadersValue

T_shell_context_processor = t.TypeVar(
    "T_shell_context_processor", bound=ft.ShellContextProcessorCallable
)
T_teardown = t.TypeVar("T_teardown", bound=ft.TeardownCallable)
T_template_filter = t.TypeVar("T_template_filter", bound=ft.TemplateFilterCallable)
T_template_global = t.TypeVar("T_template_global", bound=ft.TemplateGlobalCallable)
T_template_test = t.TypeVar("T_template_test", bound=ft.TemplateTestCallable)


def _make_timedelta(value: timedelta | int | None) -> timedelta | None:
    if value is None or isinstance(value, timedelta):
        return value

    return timedelta(seconds=value)


class Flask(App):
    """Đối tượng flask triển khai một ứng dụng WSGI và đóng vai trò là đối tượng
    trung tâm. Nó được truyền tên của module hoặc package của
    ứng dụng. Sau khi được tạo, nó sẽ hoạt động như một sổ đăng ký trung tâm cho
    các hàm view, các quy tắc URL, cấu hình template và nhiều thứ khác.

    Tên của package được sử dụng để giải quyết các tài nguyên từ bên trong
    package hoặc thư mục chứa module tùy thuộc vào việc tham số
    package giải quyết thành một package python thực sự (một thư mục với
    tệp :file:`__init__.py` bên trong) hay một module chuẩn (chỉ là một tệp ``.py``).

    Để biết thêm thông tin về việc tải tài nguyên, xem :func:`open_resource`.

    Thông thường bạn tạo một thể hiện :class:`Flask` trong module chính của bạn hoặc
    trong tệp :file:`__init__.py` của package của bạn như thế này::

        from flask import Flask
        app = Flask(__name__)

    .. admonition:: Về tham số đầu tiên

        Ý tưởng của tham số đầu tiên là cung cấp cho Flask một ý tưởng về những gì
        thuộc về ứng dụng của bạn. Tên này được sử dụng để tìm tài nguyên
        trên hệ thống tệp, có thể được sử dụng bởi các tiện ích mở rộng để cải thiện thông tin
        gỡ lỗi và nhiều thứ khác.

        Vì vậy, điều quan trọng là những gì bạn cung cấp ở đó. Nếu bạn đang sử dụng một
        module đơn lẻ, `__name__` luôn là giá trị chính xác. Tuy nhiên, nếu bạn đang
        sử dụng một package, thường nên hardcode tên của
        package của bạn ở đó.

        Ví dụ: nếu ứng dụng của bạn được định nghĩa trong :file:`yourapplication/app.py`
        bạn nên tạo nó với một trong hai phiên bản dưới đây::

            app = Flask('yourapplication')
            app = Flask(__name__.split('.')[0])

        Tại sao lại như vậy? Ứng dụng sẽ hoạt động ngay cả với `__name__`, nhờ
        cách các tài nguyên được tra cứu. Tuy nhiên, nó sẽ làm cho việc gỡ lỗi trở nên
        đau đớn hơn. Một số tiện ích mở rộng nhất định có thể đưa ra các giả định dựa trên
        tên import của ứng dụng của bạn. Ví dụ: tiện ích mở rộng Flask-SQLAlchemy
        sẽ tìm mã trong ứng dụng của bạn đã kích hoạt
        truy vấn SQL trong chế độ gỡ lỗi. Nếu tên import không được thiết lập đúng
        cách, thông tin gỡ lỗi đó sẽ bị mất. (Ví dụ: nó sẽ chỉ
        nhận các truy vấn SQL trong `yourapplication.app` và không phải
        `yourapplication.views.frontend`)

    .. versionadded:: 0.7
       Các tham số `static_url_path`, `static_folder`, và `template_folder`
       đã được thêm vào.

    .. versionadded:: 0.8
       Các tham số `instance_path` và `instance_relative_config` đã được
       thêm vào.

    .. versionadded:: 0.11
       Tham số `root_path` đã được thêm vào.

    .. versionadded:: 1.0
       Các tham số ``host_matching`` và ``static_host`` đã được thêm vào.

    .. versionadded:: 1.0
       Tham số ``subdomain_matching`` đã được thêm vào. Khớp subdomain
       cần được kích hoạt thủ công ngay bây giờ. Thiết lập
       :data:`SERVER_NAME` không ngầm kích hoạt nó.

    :param import_name: tên của package ứng dụng
    :param static_url_path: có thể được sử dụng để chỉ định một đường dẫn khác cho
                            các tệp tĩnh trên web. Mặc định là tên
                            của thư mục `static_folder`.
    :param static_folder: Thư mục chứa các tệp tĩnh được phục vụ tại
        ``static_url_path``. Tương đối với ``root_path`` của ứng dụng
        hoặc một đường dẫn tuyệt đối. Mặc định là ``'static'``.
    :param static_host: host để sử dụng khi thêm route tĩnh.
        Mặc định là None. Bắt buộc khi sử dụng ``host_matching=True``
        với một ``static_folder`` được cấu hình.
    :param host_matching: thiết lập thuộc tính ``url_map.host_matching``.
        Mặc định là False.
    :param subdomain_matching: xem xét subdomain tương đối với
        :data:`SERVER_NAME` khi khớp các route. Mặc định là False.
    :param template_folder: thư mục chứa các template nên
                            được sử dụng bởi ứng dụng. Mặc định là
                            thư mục ``'templates'`` trong đường dẫn gốc của
                            ứng dụng.
    :param instance_path: Một đường dẫn instance thay thế cho ứng dụng.
                          Theo mặc định, thư mục ``'instance'`` bên cạnh
                          package hoặc module được giả định là đường dẫn
                          instance.
    :param instance_relative_config: nếu được đặt thành ``True`` các tên tệp tương đối
                                     để tải cấu hình được giả định là
                                     tương đối với đường dẫn instance thay vì
                                     gốc ứng dụng.
    :param root_path: Đường dẫn đến gốc của các tệp ứng dụng.
        Điều này chỉ nên được thiết lập thủ công khi nó không thể được phát hiện
        tự động, chẳng hạn như đối với các namespace package.
    """

    default_config = ImmutableDict(
        {
            "DEBUG": None,
            "TESTING": False,
            "PROPAGATE_EXCEPTIONS": None,
            "SECRET_KEY": None,
            "SECRET_KEY_FALLBACKS": None,
            "PERMANENT_SESSION_LIFETIME": timedelta(days=31),
            "USE_X_SENDFILE": False,
            "TRUSTED_HOSTS": None,
            "SERVER_NAME": None,
            "APPLICATION_ROOT": "/",
            "SESSION_COOKIE_NAME": "session",
            "SESSION_COOKIE_DOMAIN": None,
            "SESSION_COOKIE_PATH": None,
            "SESSION_COOKIE_HTTPONLY": True,
            "SESSION_COOKIE_SECURE": False,
            "SESSION_COOKIE_PARTITIONED": False,
            "SESSION_COOKIE_SAMESITE": None,
            "SESSION_REFRESH_EACH_REQUEST": True,
            "MAX_CONTENT_LENGTH": None,
            "MAX_FORM_MEMORY_SIZE": 500_000,
            "MAX_FORM_PARTS": 1_000,
            "SEND_FILE_MAX_AGE_DEFAULT": None,
            "TRAP_BAD_REQUEST_ERRORS": None,
            "TRAP_HTTP_EXCEPTIONS": False,
            "EXPLAIN_TEMPLATE_LOADING": False,
            "PREFERRED_URL_SCHEME": "http",
            "TEMPLATES_AUTO_RELOAD": None,
            "MAX_COOKIE_SIZE": 4093,
            "PROVIDE_AUTOMATIC_OPTIONS": True,
        }
    )

    #: Lớp được sử dụng cho các đối tượng request. Xem :class:`~flask.Request`
    #: để biết thêm thông tin.
    request_class: type[Request] = Request

    #: Lớp được sử dụng cho các đối tượng response. Xem
    #: :class:`~flask.Response` để biết thêm thông tin.
    response_class: type[Response] = Response

    #: giao diện session để sử dụng. Theo mặc định, một thể hiện của
    #: :class:`~flask.sessions.SecureCookieSessionInterface` được sử dụng ở đây.
    #:
    #: .. versionadded:: 0.8
    session_interface: SessionInterface = SecureCookieSessionInterface()

    def __init__(
        self,
        import_name: str,
        static_url_path: str | None = None,
        static_folder: str | os.PathLike[str] | None = "static",
        static_host: str | None = None,
        host_matching: bool = False,
        subdomain_matching: bool = False,
        template_folder: str | os.PathLike[str] | None = "templates",
        instance_path: str | None = None,
        instance_relative_config: bool = False,
        root_path: str | None = None,
    ):
        super().__init__(
            import_name=import_name,
            static_url_path=static_url_path,
            static_folder=static_folder,
            static_host=static_host,
            host_matching=host_matching,
            subdomain_matching=subdomain_matching,
            template_folder=template_folder,
            instance_path=instance_path,
            instance_relative_config=instance_relative_config,
            root_path=root_path,
        )

        #: Nhóm lệnh Click để đăng ký các lệnh CLI cho đối tượng
        #: này. Các lệnh có sẵn từ lệnh ``flask``
        #: sau khi ứng dụng đã được phát hiện và các blueprint đã
        #: được đăng ký.
        self.cli = cli.AppGroup()

        # Đặt tên của nhóm Click trong trường hợp ai đó muốn thêm
        # các lệnh của ứng dụng vào một công cụ CLI khác.
        self.cli.name = self.name

        # Thêm một route tĩnh sử dụng static_url_path, static_host,
        # và static_folder được cung cấp nếu có một static_folder được cấu hình.
        # Lưu ý chúng tôi làm điều này mà không kiểm tra xem static_folder có tồn tại hay không.
        # Một là, nó có thể được tạo trong khi server đang chạy (ví dụ: trong quá trình
        # phát triển). Ngoài ra, Google App Engine lưu trữ các tệp tĩnh ở đâu đó
        if self.has_static_folder:
            assert bool(static_host) == host_matching, (
                "Invalid static_host/host_matching combination"
            )
            # Sử dụng weakref để tránh tạo vòng tham chiếu giữa app
            # và hàm view (xem #3761).
            self_ref = weakref.ref(self)
            self.add_url_rule(
                f"{self.static_url_path}/<path:filename>",
                endpoint="static",
                host=static_host,
                view_func=lambda **kw: self_ref().send_static_file(**kw),  # type: ignore # noqa: B950
            )

    def get_send_file_max_age(self, filename: str | None) -> int | None:
        """Được sử dụng bởi :func:`send_file` để xác định giá trị cache ``max_age``
        cho một đường dẫn tệp nhất định nếu nó không được truyền.

        Theo mặc định, điều này trả về :data:`SEND_FILE_MAX_AGE_DEFAULT` từ
        cấu hình của :data:`~flask.current_app`. Điều này mặc định
        là ``None``, điều này bảo trình duyệt sử dụng các request có điều kiện
        thay vì cache theo thời gian, điều này thường được ưu tiên hơn.

        Lưu ý đây là bản sao của cùng một phương thức trong lớp Flask.

        .. versionchanged:: 2.0
            Cấu hình mặc định là ``None`` thay vì 12 giờ.

        .. versionadded:: 0.9
        """
        value = self.config["SEND_FILE_MAX_AGE_DEFAULT"]

        if value is None:
            return None

        if isinstance(value, timedelta):
            return int(value.total_seconds())

        return value  # type: ignore[no-any-return]

    def send_static_file(self, filename: str) -> Response:
        """Hàm view được sử dụng để phục vụ các tệp từ
        :attr:`static_folder`. Một route được tự động đăng ký cho
        view này tại :attr:`static_url_path` nếu :attr:`static_folder` được
        thiết lập.

        Lưu ý đây là bản sao của cùng một phương thức trong lớp Flask.

        .. versionadded:: 0.5

        """
        if not self.has_static_folder:
            raise RuntimeError("'static_folder' must be set to serve static_files.")

        # send_file chỉ biết gọi get_send_file_max_age trên app,
        # gọi nó ở đây để nó cũng hoạt động cho các blueprint.
        max_age = self.get_send_file_max_age(filename)
        return send_from_directory(
            t.cast(str, self.static_folder), filename, max_age=max_age
        )

    def open_resource(
        self, resource: str, mode: str = "rb", encoding: str | None = None
    ) -> t.IO[t.AnyStr]:
        """Mở một tệp tài nguyên tương đối với :attr:`root_path` để đọc.

        Ví dụ, nếu tệp ``schema.sql`` nằm cạnh tệp
        ``app.py`` nơi ứng dụng ``Flask`` được định nghĩa, nó có thể được mở
        với:

        .. code-block:: python

            with app.open_resource("schema.sql") as f:
                conn.executescript(f.read())

        :param resource: Đường dẫn đến tài nguyên tương đối với :attr:`root_path`.
        :param mode: Mở tệp ở chế độ này. Chỉ hỗ trợ đọc,
            các giá trị hợp lệ là ``"r"`` (hoặc ``"rt"``) và ``"rb"``.
        :param encoding: Mở tệp với mã hóa này khi mở ở chế độ văn bản.
            Điều này bị bỏ qua khi mở ở chế độ nhị phân.

        .. versionchanged:: 3.1
            Đã thêm tham số ``encoding``.
        """
        if mode not in {"r", "rt", "rb"}:
            raise ValueError("Resources can only be opened for reading.")

        path = os.path.join(self.root_path, resource)

        if mode == "rb":
            return open(path, mode)  # pyright: ignore

        return open(path, mode, encoding=encoding)

    def open_instance_resource(
        self, resource: str, mode: str = "rb", encoding: str | None = "utf-8"
    ) -> t.IO[t.AnyStr]:
        """Mở một tệp tài nguyên tương đối với thư mục instance của ứng dụng
        :attr:`instance_path`. Không giống như :meth:`open_resource`, các tệp trong
        thư mục instance có thể được mở để ghi.

        :param resource: Đường dẫn đến tài nguyên tương đối với :attr:`instance_path`.
        :param mode: Mở tệp ở chế độ này.
        :param encoding: Mở tệp với mã hóa này khi mở ở chế độ văn bản.
            Điều này bị bỏ qua khi mở ở chế độ nhị phân.

        .. versionchanged:: 3.1
            Đã thêm tham số ``encoding``.
        """
        path = os.path.join(self.instance_path, resource)

        if "b" in mode:
            return open(path, mode)

        return open(path, mode, encoding=encoding)

    def create_jinja_environment(self) -> Environment:
        """Tạo môi trường Jinja dựa trên :attr:`jinja_options`
        và các phương thức liên quan đến Jinja khác nhau của ứng dụng. Thay đổi
        :attr:`jinja_options` sau điều này sẽ không có hiệu lực. Cũng thêm
        các biến toàn cục và bộ lọc liên quan đến Flask vào môi trường.

        .. versionchanged:: 0.11
           ``Environment.auto_reload`` được thiết lập phù hợp với
           tùy chọn cấu hình ``TEMPLATES_AUTO_RELOAD``.

        .. versionadded:: 0.5
        """
        options = dict(self.jinja_options)

        if "autoescape" not in options:
            options["autoescape"] = self.select_jinja_autoescape

        if "auto_reload" not in options:
            auto_reload = self.config["TEMPLATES_AUTO_RELOAD"]

            if auto_reload is None:
                auto_reload = self.debug

            options["auto_reload"] = auto_reload

        rv = self.jinja_environment(self, **options)
        rv.globals.update(
            url_for=self.url_for,
            get_flashed_messages=get_flashed_messages,
            config=self.config,
            # request, session và g thường được thêm vào với
            # context processor vì lý do hiệu quả nhưng đối với các template
            # được import, chúng tôi cũng muốn các proxy ở đó.
            request=request,
            session=session,
            g=g,
        )
        rv.policies["json.dumps_function"] = self.json.dumps
        return rv

    def create_url_adapter(self, request: Request | None) -> MapAdapter | None:
        """Tạo một bộ chuyển đổi URL cho request đã cho. Bộ chuyển đổi URL
        được tạo tại một thời điểm mà ngữ cảnh request chưa được thiết lập
        nên request được truyền một cách rõ ràng.

        .. versionchanged:: 3.1
            Nếu :data:`SERVER_NAME` được thiết lập, nó không hạn chế các request chỉ
            đến domain đó, cho cả ``subdomain_matching`` và
            ``host_matching``.

        .. versionchanged:: 1.0
            :data:`SERVER_NAME` không còn ngầm kích hoạt khớp subdomain.
            Sử dụng :attr:`subdomain_matching` thay thế.

        .. versionchanged:: 0.9
           Điều này có thể được gọi bên ngoài một request khi bộ chuyển đổi URL được tạo
           cho một ngữ cảnh ứng dụng.

        .. versionadded:: 0.6
        """
        if request is not None:
            if (trusted_hosts := self.config["TRUSTED_HOSTS"]) is not None:
                request.trusted_hosts = trusted_hosts

            # Kiểm tra trusted_hosts ở đây cho đến khi bind_to_environ thực hiện.
            request.host = get_host(request.environ, request.trusted_hosts)  # pyright: ignore
            subdomain = None
            server_name = self.config["SERVER_NAME"]

            if self.url_map.host_matching:
                # Không truyền SERVER_NAME, nếu không nó sẽ được sử dụng và host thực tế
                # sẽ bị bỏ qua, điều này làm hỏng khớp host.
                server_name = None
            elif not self.subdomain_matching:
                # Werkzeug chưa triển khai khớp subdomain. Cho đến lúc đó,
                # vô hiệu hóa nó bằng cách buộc subdomain hiện tại thành mặc định, hoặc
                # chuỗi rỗng.
                subdomain = self.url_map.default_subdomain or ""

            return self.url_map.bind_to_environ(
                request.environ, server_name=server_name, subdomain=subdomain
            )

        # Cần ít nhất SERVER_NAME để khớp/xây dựng bên ngoài một request.
        if self.config["SERVER_NAME"] is not None:
            return self.url_map.bind(
                self.config["SERVER_NAME"],
                script_name=self.config["APPLICATION_ROOT"],
                url_scheme=self.config["PREFERRED_URL_SCHEME"],
            )

        return None

    def raise_routing_exception(self, request: Request) -> t.NoReturn:
        """Chặn các ngoại lệ định tuyến và có thể làm điều gì đó khác.

        Trong chế độ gỡ lỗi, chặn một chuyển hướng định tuyến và thay thế nó bằng
        một lỗi nếu phần thân sẽ bị loại bỏ.

        Với Werkzeug hiện đại, điều này không nên xảy ra, vì nó hiện sử dụng
        trạng thái 308 để bảo trình duyệt gửi lại phương thức và
        phần thân.

        .. versionchanged:: 2.1
            Không chặn các chuyển hướng 307 và 308.

        :meta private:
        :internal:
        """
        if (
            not self.debug
            or not isinstance(request.routing_exception, RequestRedirect)
            or request.routing_exception.code in {307, 308}
            or request.method in {"GET", "HEAD", "OPTIONS"}
        ):
            raise request.routing_exception  # type: ignore[misc]

        from .debughelpers import FormDataRoutingRedirect

        raise FormDataRoutingRedirect(request)

    def update_template_context(self, context: dict[str, t.Any]) -> None:
        """Cập nhật ngữ cảnh template với một số biến thường được sử dụng.
        Điều này tiêm request, session, config và g vào ngữ cảnh template
        cũng như mọi thứ mà các bộ xử lý ngữ cảnh template muốn
        tiêm vào. Lưu ý rằng kể từ Flask 0.6, các giá trị ban đầu
        trong ngữ cảnh sẽ không bị ghi đè nếu một bộ xử lý ngữ cảnh
        quyết định trả về một giá trị với cùng một khóa.

        :param context: ngữ cảnh dưới dạng từ điển được cập nhật tại chỗ
                        để thêm các biến bổ sung.
        """
        names: t.Iterable[str | None] = (None,)

        # Một template có thể được render bên ngoài một ngữ cảnh request.
        if (ctx := _cv_app.get(None)) is not None and ctx.has_request:
            names = chain(names, reversed(ctx.request.blueprints))

        # Các giá trị được truyền cho render_template được ưu tiên. Giữ một
        # bản sao để áp dụng lại sau tất cả các hàm ngữ cảnh.
        orig_ctx = context.copy()

        for name in names:
            if name in self.template_context_processors:
                for func in self.template_context_processors[name]:
                    context.update(self.ensure_sync(func)())

        context.update(orig_ctx)

    def make_shell_context(self) -> dict[str, t.Any]:
        """Trả về ngữ cảnh shell cho một shell tương tác cho ứng dụng
        này. Điều này chạy tất cả các bộ xử lý ngữ cảnh shell đã đăng ký.

        .. versionadded:: 0.11
        """
        rv = {"app": self, "g": g}
        for processor in self.shell_context_processors:
            rv.update(processor())
        return rv

    def run(
        self,
        host: str | None = None,
        port: int | None = None,
        debug: bool | None = None,
        load_dotenv: bool = True,
        **options: t.Any,
    ) -> None:
        """Chạy ứng dụng trên một server phát triển cục bộ.

        Không sử dụng ``run()`` trong môi trường sản xuất. Nó không được thiết kế để
        đáp ứng các yêu cầu về bảo mật và hiệu suất cho một server sản xuất.
        Thay vào đó, xem :doc:`/deploying/index` để biết các khuyến nghị về server WSGI.

        Nếu cờ :attr:`debug` được thiết lập, server sẽ tự động tải lại
        khi có thay đổi mã và hiển thị trình gỡ lỗi trong trường hợp xảy ra ngoại lệ.

        Nếu bạn muốn chạy ứng dụng trong chế độ gỡ lỗi, nhưng vô hiệu hóa
        việc thực thi mã trên trình gỡ lỗi tương tác, bạn có thể truyền
        ``use_evalex=False`` làm tham số. Điều này sẽ giữ màn hình traceback
        của trình gỡ lỗi hoạt động, nhưng vô hiệu hóa việc thực thi mã.

        Không khuyến khích sử dụng hàm này để phát triển với
        tự động tải lại vì điều này được hỗ trợ kém. Thay vào đó bạn nên
        sử dụng hỗ trợ ``run`` của script dòng lệnh :command:`flask`.

        .. admonition:: Hãy nhớ rằng

           Flask sẽ chặn mọi lỗi server với một trang lỗi chung
           trừ khi nó ở chế độ gỡ lỗi. Do đó, để chỉ kích hoạt
           trình gỡ lỗi tương tác mà không tải lại mã, bạn phải
           gọi :meth:`run` với ``debug=True`` và ``use_reloader=False``.
           Thiết lập ``use_debugger`` thành ``True`` mà không ở chế độ gỡ lỗi
           sẽ không bắt được bất kỳ ngoại lệ nào vì sẽ không có ngoại lệ nào để
           bắt.

        :param host: hostname để lắng nghe. Đặt thành ``'0.0.0.0'`` để
            server có sẵn bên ngoài. Mặc định là
            ``'127.0.0.1'`` hoặc host trong biến cấu hình ``SERVER_NAME``
            nếu có.
        :param port: cổng của webserver. Mặc định là ``5000`` hoặc
            cổng được định nghĩa trong biến cấu hình ``SERVER_NAME`` nếu có.
        :param debug: nếu được đưa ra, kích hoạt hoặc vô hiệu hóa chế độ gỡ lỗi. Xem
            :attr:`debug`.
        :param load_dotenv: Tải các tệp :file:`.env` và :file:`.flaskenv` gần nhất
            để thiết lập các biến môi trường. Cũng sẽ thay đổi thư mục
            làm việc sang thư mục chứa tệp đầu tiên được tìm thấy.
        :param options: các tùy chọn được chuyển tiếp đến server Werkzeug
            cơ bản. Xem :func:`werkzeug.serving.run_simple` để biết thêm
            thông tin.

        .. versionchanged:: 1.0
            Nếu được cài đặt, python-dotenv sẽ được sử dụng để tải các biến
            môi trường từ các tệp :file:`.env` và :file:`.flaskenv`.

            Biến môi trường :envvar:`FLASK_DEBUG` sẽ ghi đè :attr:`debug`.

            Chế độ luồng được kích hoạt theo mặc định.

        .. versionchanged:: 0.10
            Cổng mặc định hiện được chọn từ biến ``SERVER_NAME``.
        """
        # Bỏ qua cuộc gọi này để nó không khởi động một server khác nếu
        # lệnh 'flask run' được sử dụng.
        if os.environ.get("FLASK_RUN_FROM_CLI") == "true":
            if not is_running_from_reloader():
                click.secho(
                    " * Ignoring a call to 'app.run()' that would block"
                    " the current 'flask' CLI command.\n"
                    "   Only call 'app.run()' in an 'if __name__ =="
                    ' "__main__"\' guard.',
                    fg="red",
                )

            return

        if get_load_dotenv(load_dotenv):
            cli.load_dotenv()

            # nếu được thiết lập, biến môi trường ghi đè giá trị hiện có
            if "FLASK_DEBUG" in os.environ:
                self.debug = get_debug_flag()

        # debug được truyền cho phương thức ghi đè tất cả các nguồn khác
        if debug is not None:
            self.debug = bool(debug)

        server_name = self.config.get("SERVER_NAME")
        sn_host = sn_port = None

        if server_name:
            sn_host, _, sn_port = server_name.partition(":")

        if not host:
            if sn_host:
                host = sn_host
            else:
                host = "127.0.0.1"

        if port or port == 0:
            port = int(port)
        elif sn_port:
            port = int(sn_port)
        else:
            port = 5000

        options.setdefault("use_reloader", self.debug)
        options.setdefault("use_debugger", self.debug)
        options.setdefault("threaded", True)

        cli.show_server_banner(self.debug, self.name)

        from werkzeug.serving import run_simple

        try:
            run_simple(t.cast(str, host), port, self, **options)
        finally:
            # reset thông tin request đầu tiên nếu server phát triển
            # reset bình thường. Điều này làm cho việc khởi động lại server
            # mà không có reloader và những thứ đó từ một shell tương tác trở nên khả thi.
            self._got_first_request = False

    def test_client(self, use_cookies: bool = True, **kwargs: t.Any) -> FlaskClient:
        """Tạo một test client cho ứng dụng này. Để biết thông tin
        về unit testing hãy xem :doc:`/testing`.

        Lưu ý rằng nếu bạn đang kiểm tra các assertion hoặc ngoại lệ trong
        mã ứng dụng của bạn, bạn phải đặt ``app.testing = True`` để
        các ngoại lệ lan truyền đến test client. Nếu không, ngoại lệ
        sẽ được xử lý bởi ứng dụng (không hiển thị cho test client) và
        chỉ báo duy nhất về một AssertionError hoặc ngoại lệ khác sẽ là một
        phản hồi mã trạng thái 500 cho test client. Xem thuộc tính :attr:`testing`.
        Ví dụ::

            app.testing = True
            client = app.test_client()

        Test client có thể được sử dụng trong một khối ``with`` để hoãn việc đóng
        ngữ cảnh cho đến khi kết thúc khối ``with``. Điều này hữu ích nếu
        bạn muốn truy cập các biến cục bộ ngữ cảnh để kiểm tra::

            with app.test_client() as c:
                rv = c.get('/?vodka=42')
                assert request.args['vodka'] == '42'

        Ngoài ra, bạn có thể truyền các đối số từ khóa tùy chọn sẽ được
        truyền cho hàm tạo :attr:`test_client_class` của ứng dụng.
        Ví dụ::

            from flask.testing import FlaskClient

            class CustomClient(FlaskClient):
                def __init__(self, *args, **kwargs):
                    self._authentication = kwargs.pop("authentication")
                    super(CustomClient,self).__init__( *args, **kwargs)

            app.test_client_class = CustomClient
            client = app.test_client(authentication='Basic ....')

        Xem :class:`~flask.testing.FlaskClient` để biết thêm thông tin.

        .. versionchanged:: 0.4
           đã thêm hỗ trợ cho việc sử dụng khối ``with`` cho client.

        .. versionadded:: 0.7
           Tham số `use_cookies` đã được thêm vào cũng như khả năng
           ghi đè client được sử dụng bằng cách thiết lập
           thuộc tính :attr:`test_client_class`.

        .. versionchanged:: 0.11
           Đã thêm `**kwargs` để hỗ trợ truyền các đối số từ khóa bổ sung cho
           hàm tạo của :attr:`test_client_class`.
        """
        cls = self.test_client_class
        if cls is None:
            from .testing import FlaskClient as cls
        return cls(  # type: ignore
            self, self.response_class, use_cookies=use_cookies, **kwargs
        )

    def test_cli_runner(self, **kwargs: t.Any) -> FlaskCliRunner:
        """Tạo một trình chạy CLI để kiểm tra các lệnh CLI.
        Xem :ref:`testing-cli`.

        Trả về một thể hiện của :attr:`test_cli_runner_class`, theo mặc định
        :class:`~flask.testing.FlaskCliRunner`. Đối tượng ứng dụng Flask được
        truyền làm đối số đầu tiên.

        .. versionadded:: 1.0
        """
        cls = self.test_cli_runner_class

        if cls is None:
            from .testing import FlaskCliRunner as cls

        return cls(self, **kwargs)  # type: ignore

    def handle_http_exception(
        self, e: HTTPException
    ) -> HTTPException | ft.ResponseReturnValue:
        """Xử lý một ngoại lệ HTTP. Theo mặc định, điều này sẽ gọi các
        trình xử lý lỗi đã đăng ký và quay lại trả về
        ngoại lệ dưới dạng phản hồi.

        .. versionchanged:: 1.0.3
            ``RoutingException``, được sử dụng nội bộ cho các hành động như
             chuyển hướng dấu gạch chéo trong quá trình định tuyến, không được truyền cho các trình xử lý
             lỗi.

        .. versionchanged:: 1.0
            Các ngoại lệ được tra cứu theo mã *và* theo MRO, vì vậy
            các lớp con ``HTTPException`` có thể được xử lý bằng một trình xử lý
            bắt tất cả cho ``HTTPException`` cơ sở.

        .. versionadded:: 0.3
        """
        # Các ngoại lệ proxy không có mã lỗi. Chúng tôi muốn luôn trả về
        # chúng không thay đổi dưới dạng lỗi
        if e.code is None:
            return e

        # RoutingExceptions được sử dụng nội bộ để kích hoạt các hành động
        # định tuyến, chẳng hạn như chuyển hướng dấu gạch chéo gây ra RequestRedirect. Chúng
        # không được ném ra hoặc xử lý trong mã người dùng.
        if isinstance(e, RoutingException):
            return e

        handler = self._find_error_handler(e, request.blueprints)
        if handler is None:
            return e
        return self.ensure_sync(handler)(e)  # type: ignore[no-any-return]

    def handle_user_exception(
        self, e: Exception
    ) -> HTTPException | ft.ResponseReturnValue:
        """Phương thức này được gọi bất cứ khi nào một ngoại lệ xảy ra mà
        cần được xử lý. Một trường hợp đặc biệt là :class:`~werkzeug
        .exceptions.HTTPException` được chuyển tiếp đến
        phương thức :meth:`handle_http_exception`. Hàm này sẽ trả về
        một giá trị phản hồi hoặc ném lại ngoại lệ với cùng một
        traceback.

        .. versionchanged:: 1.0
            Các lỗi khóa được ném ra từ dữ liệu request như ``form`` hiển thị
            khóa sai trong chế độ gỡ lỗi thay vì một thông báo bad request
            chung chung.

        .. versionadded:: 0.7
        """
        if isinstance(e, BadRequestKeyError) and (
            self.debug or self.config["TRAP_BAD_REQUEST_ERRORS"]
        ):
            e.show_exception = True

        if isinstance(e, HTTPException) and not self.trap_http_exception(e):
            return self.handle_http_exception(e)

        handler = self._find_error_handler(e, request.blueprints)

        if handler is None:
            raise

        return self.ensure_sync(handler)(e)  # type: ignore[no-any-return]

    def handle_exception(self, e: Exception) -> Response:
        """Xử lý một ngoại lệ không có trình xử lý lỗi
        liên kết với nó, hoặc được ném ra từ một trình xử lý lỗi.
        Điều này luôn gây ra lỗi 500 ``InternalServerError``.

        Luôn gửi tín hiệu :data:`got_request_exception`.

        Nếu :data:`PROPAGATE_EXCEPTIONS` là ``True``, chẳng hạn như trong chế độ
        gỡ lỗi, lỗi sẽ được ném lại để trình gỡ lỗi có thể
        hiển thị nó. Nếu không, ngoại lệ ban đầu được ghi log, và
        một :exc:`~werkzeug.exceptions.InternalServerError` được trả về.

        Nếu một trình xử lý lỗi được đăng ký cho ``InternalServerError`` hoặc
        ``500``, nó sẽ được sử dụng. Để nhất quán, trình xử lý sẽ
        luôn nhận được ``InternalServerError``. Ngoại lệ ban đầu
        không được xử lý có sẵn dưới dạng ``e.original_exception``.

        .. versionchanged:: 1.1.0
            Luôn truyền thể hiện ``InternalServerError`` cho
            trình xử lý, thiết lập ``original_exception`` thành lỗi không được
            xử lý.

        .. versionchanged:: 1.1.0
            Các hàm ``after_request`` và các bước hoàn thiện khác được thực hiện
            ngay cả đối với phản hồi 500 mặc định khi không có trình xử lý.

        .. versionadded:: 0.3
        """
        exc_info = sys.exc_info()
        got_request_exception.send(self, _async_wrapper=self.ensure_sync, exception=e)
        propagate = self.config["PROPAGATE_EXCEPTIONS"]

        if propagate is None:
            propagate = self.testing or self.debug

        if propagate:
            # Ném lại nếu được gọi với một ngoại lệ đang hoạt động, nếu không
            # ném ngoại lệ được truyền vào.
            if exc_info[1] is e:
                raise

            raise e

        self.log_exception(exc_info)
        server_error: InternalServerError | ft.ResponseReturnValue
        server_error = InternalServerError(original_exception=e)
        handler = self._find_error_handler(server_error, request.blueprints)

        if handler is not None:
            server_error = self.ensure_sync(handler)(server_error)

        return self.finalize_request(server_error, from_error_handler=True)

    def log_exception(
        self,
        exc_info: (tuple[type, BaseException, TracebackType] | tuple[None, None, None]),
    ) -> None:
        """Ghi log một ngoại lệ. Điều này được gọi bởi :meth:`handle_exception`
        nếu gỡ lỗi bị vô hiệu hóa và ngay trước khi trình xử lý được gọi.
        Triển khai mặc định ghi log ngoại lệ dưới dạng lỗi trên
        :attr:`logger`.

        .. versionadded:: 0.8
        """
        self.logger.error(
            f"Exception on {request.path} [{request.method}]", exc_info=exc_info
        )

    def dispatch_request(self) -> ft.ResponseReturnValue:
        """Thực hiện việc điều phối request. Khớp URL và trả về
        giá trị trả về của view hoặc trình xử lý lỗi. Điều này không nhất thiết phải
        là một đối tượng phản hồi. Để chuyển đổi giá trị trả về thành một
        đối tượng phản hồi thích hợp, hãy gọi :func:`make_response`.

        .. versionchanged:: 0.7
           Điều này không còn thực hiện xử lý ngoại lệ, mã này đã được
           chuyển sang :meth:`full_dispatch_request` mới.
        """
        req = _cv_app.get().request

        if req.routing_exception is not None:
            self.raise_routing_exception(req)
        rule: Rule = req.url_rule  # type: ignore[assignment]
        # nếu chúng tôi cung cấp các tùy chọn tự động cho URL này và
        # request đi kèm với phương thức OPTIONS, trả lời tự động
        if (
            getattr(rule, "provide_automatic_options", False)
            and req.method == "OPTIONS"
        ):
            return self.make_default_options_response()
        # nếu không thì điều phối đến trình xử lý cho endpoint đó
        view_args: dict[str, t.Any] = req.view_args  # type: ignore[assignment]
        return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]

    def full_dispatch_request(self) -> Response:
        """Điều phối request và trên hết thực hiện tiền xử lý và hậu xử lý
        request cũng như bắt ngoại lệ HTTP và
        xử lý lỗi.

        .. versionadded:: 0.7
        """
        self._got_first_request = True

        try:
            request_started.send(self, _async_wrapper=self.ensure_sync)
            rv = self.preprocess_request()
            if rv is None:
                rv = self.dispatch_request()
        except Exception as e:
            rv = self.handle_user_exception(e)
        return self.finalize_request(rv)

    def finalize_request(
        self,
        rv: ft.ResponseReturnValue | HTTPException,
        from_error_handler: bool = False,
    ) -> Response:
        """Với giá trị trả về từ một hàm view, điều này hoàn thiện
        request bằng cách chuyển đổi nó thành một phản hồi và gọi các
        hàm hậu xử lý. Điều này được gọi cho cả điều phối request
        bình thường cũng như các trình xử lý lỗi.

        Bởi vì điều này có nghĩa là nó có thể được gọi là kết quả của một
        thất bại, một chế độ an toàn đặc biệt có sẵn có thể được kích hoạt
        với cờ `from_error_handler`. Nếu được kích hoạt, các thất bại trong
        xử lý phản hồi sẽ được ghi log và nếu không sẽ bị bỏ qua.

        :internal:
        """
        response = self.make_response(rv)
        try:
            response = self.process_response(response)
            request_finished.send(
                self, _async_wrapper=self.ensure_sync, response=response
            )
        except Exception:
            if not from_error_handler:
                raise
            self.logger.exception(
                "Request finalizing failed with an error while handling an error"
            )
        return response

    def make_default_options_response(self) -> Response:
        """Phương thức này được gọi để tạo phản hồi ``OPTIONS`` mặc định.
        Điều này có thể được thay đổi thông qua phân lớp để thay đổi hành vi
        mặc định của các phản hồi ``OPTIONS``.

        .. versionadded:: 0.7
        """
        adapter = _cv_app.get().url_adapter
        methods = adapter.allowed_methods()  # type: ignore[union-attr]
        rv = self.response_class()
        rv.allow.update(methods)
        return rv

    def ensure_sync(self, func: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:
        """Đảm bảo rằng hàm là đồng bộ cho các worker WSGI.
        Các hàm ``def`` thông thường được trả về nguyên trạng. Các hàm ``async def``
        được bao bọc để chạy và chờ phản hồi.

        Ghi đè phương thức này để thay đổi cách ứng dụng chạy các view async.

        .. versionadded:: 2.0
        """
        if iscoroutinefunction(func):
            return self.async_to_sync(func)

        return func

    def async_to_sync(
        self, func: t.Callable[..., t.Coroutine[t.Any, t.Any, t.Any]]
    ) -> t.Callable[..., t.Any]:
        """Trả về một hàm đồng bộ sẽ chạy hàm coroutine.

        .. code-block:: python

            result = app.async_to_sync(func)(*args, **kwargs)

        Ghi đè phương thức này để thay đổi cách ứng dụng chuyển đổi mã async
        để có thể gọi đồng bộ.

        .. versionadded:: 2.0
        """
        try:
            from asgiref.sync import async_to_sync as asgiref_async_to_sync
        except ImportError:
            raise RuntimeError(
                "Install Flask with the 'async' extra in order to use async views."
            ) from None

        return asgiref_async_to_sync(func)

    def url_for(
        self,
        /,
        endpoint: str,
        *,
        _anchor: str | None = None,
        _method: str | None = None,
        _scheme: str | None = None,
        _external: bool | None = None,
        **values: t.Any,
    ) -> str:
        """Tạo một URL đến endpoint đã cho với các giá trị đã cho.

        Điều này được gọi bởi :func:`flask.url_for`, và cũng có thể được gọi
        trực tiếp.

        Một *endpoint* là tên của một quy tắc URL, thường được thêm vào với
        :meth:`@app.route() <route>`, và thường cùng tên với
        hàm view. Một route được định nghĩa trong một :class:`~flask.Blueprint`
        sẽ thêm tên của blueprint được phân tách bằng dấu ``.`` vào
        endpoint.

        Trong một số trường hợp, chẳng hạn như tin nhắn email, bạn muốn URL bao gồm
        scheme và domain, như ``https://example.com/hello``. Khi
        không ở trong một request đang hoạt động, các URL sẽ là bên ngoài theo mặc định, nhưng
        điều này yêu cầu thiết lập :data:`SERVER_NAME` để Flask biết
        domain nào để sử dụng. :data:`APPLICATION_ROOT` và
        :data:`PREFERRED_URL_SCHEME` cũng nên được cấu hình khi
        cần thiết. Cấu hình này chỉ được sử dụng khi không ở trong một request đang hoạt động.

        Các hàm có thể được trang trí với :meth:`url_defaults` để sửa đổi
        các đối số từ khóa trước khi URL được xây dựng.

        Nếu việc xây dựng thất bại vì lý do nào đó, chẳng hạn như endpoint không xác định
        hoặc giá trị không chính xác, phương thức :meth:`handle_url_build_error`
        của ứng dụng được gọi. Nếu nó trả về một chuỗi, chuỗi đó được trả về,
        nếu không một :exc:`~werkzeug.routing.BuildError` được ném ra.

        :param endpoint: Tên endpoint liên kết với URL để
            tạo. Nếu nó bắt đầu bằng ``.``, tên blueprint hiện tại
            (nếu có) sẽ được sử dụng.
        :param _anchor: Nếu được đưa ra, thêm cái này dưới dạng ``#anchor`` vào URL.
        :param _method: Nếu được đưa ra, tạo URL liên kết với phương thức này
            cho endpoint.
        :param _scheme: Nếu được đưa ra, URL sẽ có scheme này nếu nó
            là bên ngoài.
        :param _external: Nếu được đưa ra, ưu tiên URL là nội bộ
            (False) hoặc yêu cầu nó là bên ngoài (True). Các URL bên ngoài
            bao gồm scheme và domain. Khi không ở trong một request đang
            hoạt động, các URL là bên ngoài theo mặc định.
        :param values: Các giá trị để sử dụng cho các phần biến của quy tắc
            URL. Các khóa không xác định được thêm vào dưới dạng đối số chuỗi truy vấn,
            như ``?a=b&c=d``.

        .. versionadded:: 2.2
            Được chuyển từ ``flask.url_for``, gọi phương thức này.
        """
        if (ctx := _cv_app.get(None)) is not None and ctx.has_request:
            url_adapter = ctx.url_adapter
            blueprint_name = ctx.request.blueprint

            # Nếu endpoint bắt đầu bằng "." và request khớp với một
            # blueprint, endpoint là tương đối với blueprint.
            if endpoint[:1] == ".":
                if blueprint_name is not None:
                    endpoint = f"{blueprint_name}{endpoint}"
                else:
                    endpoint = endpoint[1:]

            # Khi ở trong một request, tạo một URL không có scheme và
            # domain theo mặc định, trừ khi một scheme được đưa ra.
            if _external is None:
                _external = _scheme is not None
        else:
            # Nếu được gọi bởi helpers.url_for, một ngữ cảnh ứng dụng đang hoạt động,
            # sử dụng url_adapter của nó. Nếu không, app.url_for đã được gọi
            # trực tiếp, xây dựng một bộ chuyển đổi.
            if ctx is not None:
                url_adapter = ctx.url_adapter
            else:
                url_adapter = self.create_url_adapter(None)

            if url_adapter is None:
                raise RuntimeError(
                    "Unable to build URLs outside an active request"
                    " without 'SERVER_NAME' configured. Also configure"
                    " 'APPLICATION_ROOT' and 'PREFERRED_URL_SCHEME' as"
                    " needed."
                )

            # Khi bên ngoài một request, tạo một URL với scheme và
            # domain theo mặc định.
            if _external is None:
                _external = True

        # Sẽ là lỗi nếu thiết lập _scheme khi _external=False, để
        # tránh các URL không an toàn ngẫu nhiên.
        if _scheme is not None and not _external:
            raise ValueError("When specifying '_scheme', '_external' must be True.")

        self.inject_url_defaults(endpoint, values)

        try:
            rv = url_adapter.build(  # type: ignore[union-attr]
                endpoint,
                values,
                method=_method,
                url_scheme=_scheme,
                force_external=_external,
            )
        except BuildError as error:
            values.update(
                _anchor=_anchor, _method=_method, _scheme=_scheme, _external=_external
            )
            return self.handle_url_build_error(error, endpoint, values)

        if _anchor is not None:
            _anchor = _url_quote(_anchor, safe="%!#$&'()*+,/:;=?@")
            rv = f"{rv}#{_anchor}"

        return rv

    def make_response(self, rv: ft.ResponseReturnValue) -> Response:
        """Chuyển đổi giá trị trả về từ một hàm view thành một thể hiện của
        :attr:`response_class`.

        :param rv: giá trị trả về từ hàm view. Hàm view
            phải trả về một phản hồi. Trả về ``None``, hoặc view kết thúc
            mà không trả về, là không được phép. Các loại sau được phép
            cho ``view_rv``:

            ``str``
                Một đối tượng phản hồi được tạo với chuỗi được mã hóa thành UTF-8
                làm phần thân.

            ``bytes``
                Một đối tượng phản hồi được tạo với các byte làm phần thân.

            ``dict``
                Một từ điển sẽ được jsonify trước khi được trả về.

            ``list``
                Một danh sách sẽ được jsonify trước khi được trả về.

            ``generator`` hoặc ``iterator``
                Một generator trả về ``str`` hoặc ``bytes`` để được
                stream dưới dạng phản hồi.

            ``tuple``
                Hoặc ``(body, status, headers)``, ``(body, status)``, hoặc
                ``(body, headers)``, trong đó ``body`` là bất kỳ loại nào khác
                được phép ở đây, ``status`` là một chuỗi hoặc một số nguyên, và
                ``headers`` là một từ điển hoặc một danh sách các tuple ``(key, value)``.
                Nếu ``body`` là một thể hiện :attr:`response_class`,
                ``status`` ghi đè giá trị hiện có và ``headers`` được
                mở rộng.

            :attr:`response_class`
                Đối tượng được trả về không thay đổi.

            lớp :class:`~werkzeug.wrappers.Response` khác
                Đối tượng được ép kiểu thành :attr:`response_class`.

            :func:`callable`
                Hàm được gọi như một ứng dụng WSGI. Kết quả được
                sử dụng để tạo một đối tượng phản hồi.

        .. versionchanged:: 2.2
            Một generator sẽ được chuyển đổi thành một phản hồi streaming.
            Một danh sách sẽ được chuyển đổi thành một phản hồi JSON.

        .. versionchanged:: 1.1
            Một dict sẽ được chuyển đổi thành một phản hồi JSON.

        .. versionchanged:: 0.9
           Trước đây một tuple được hiểu là các đối số cho
           đối tượng phản hồi.
        """

        status: int | None = None
        headers: HeadersValue | None = None

        # giải nén tuple trả về
        if isinstance(rv, tuple):
            len_rv = len(rv)

            # một tuple 3 phần tử được giải nén trực tiếp
            if len_rv == 3:
                rv, status, headers = rv  # type: ignore[misc]
            # quyết định xem tuple 2 phần tử có status hay headers
            elif len_rv == 2:
                if isinstance(rv[1], (Headers, dict, tuple, list)):
                    rv, headers = rv  # pyright: ignore
                else:
                    rv, status = rv  # type: ignore[assignment,misc]
            # các tuple kích thước khác không được phép
            else:
                raise TypeError(
                    "The view function did not return a valid response tuple."
                    " The tuple must have the form (body, status, headers),"
                    " (body, status), or (body, headers)."
                )

        # phần thân không được là None
        if rv is None:
            raise TypeError(
                f"The view function for {request.endpoint!r} did not"
                " return a valid response. The function either returned"
                " None or ended without a return statement."
            )

        # đảm bảo phần thân là một thể hiện của lớp phản hồi
        if not isinstance(rv, self.response_class):
            if isinstance(rv, (str, bytes, bytearray)) or isinstance(rv, cabc.Iterator):
                # để lớp phản hồi thiết lập status và headers thay vì
                # chờ đợi để làm thủ công, để lớp có thể xử lý bất kỳ
                # logic đặc biệt nào
                rv = self.response_class(
                    rv,  # pyright: ignore
                    status=status,
                    headers=headers,  # type: ignore[arg-type]
                )
                status = headers = None
            elif isinstance(rv, (dict, list)):
                rv = self.json.response(rv)
            elif isinstance(rv, BaseResponse) or callable(rv):
                # đánh giá một WSGI callable, hoặc ép kiểu một lớp phản hồi
                # khác thành đúng loại
                try:
                    rv = self.response_class.force_type(
                        rv,  # type: ignore[arg-type]
                        request.environ,
                    )
                except TypeError as e:
                    raise TypeError(
                        f"{e}\nThe view function did not return a valid"
                        " response. The return type must be a string,"
                        " dict, list, tuple with headers or status,"
                        " Response instance, or WSGI callable, but it"
                        f" was a {type(rv).__name__}."
                    ).with_traceback(sys.exc_info()[2]) from None
            else:
                raise TypeError(
                    "The view function did not return a valid"
                    " response. The return type must be a string,"
                    " dict, list, tuple with headers or status,"
                    " Response instance, or WSGI callable, but it was a"
                    f" {type(rv).__name__}."
                )

        rv = t.cast(Response, rv)
        # ưu tiên status nếu nó được cung cấp
        if status is not None:
            if isinstance(status, (str, bytes, bytearray)):
                rv.status = status
            else:
                rv.status_code = status

        # mở rộng headers hiện có với headers được cung cấp
        if headers:
            rv.headers.update(headers)

        return rv

    def preprocess_request(self) -> ft.ResponseReturnValue | None:
        """Được gọi trước khi request được điều phối. Gọi
        :attr:`url_value_preprocessors` đã đăng ký với ứng dụng và
        blueprint hiện tại (nếu có). Sau đó gọi :attr:`before_request_funcs`
        đã đăng ký với ứng dụng và blueprint.

        Nếu bất kỳ trình xử lý :meth:`before_request` nào trả về giá trị khác None,
        giá trị đó được xử lý như thể nó là giá trị trả về từ view, và
        việc xử lý request tiếp theo bị dừng lại.
        """
        req = _cv_app.get().request
        names = (None, *reversed(req.blueprints))

        for name in names:
            if name in self.url_value_preprocessors:
                for url_func in self.url_value_preprocessors[name]:
                    url_func(req.endpoint, req.view_args)

        for name in names:
            if name in self.before_request_funcs:
                for before_func in self.before_request_funcs[name]:
                    rv = self.ensure_sync(before_func)()

                    if rv is not None:
                        return rv  # type: ignore[no-any-return]

        return None

    def process_response(self, response: Response) -> Response:
        """Có thể được ghi đè để sửa đổi đối tượng phản hồi
        trước khi nó được gửi đến server WSGI. Theo mặc định, điều này sẽ
        gọi tất cả các hàm được trang trí :meth:`after_request`.

        .. versionchanged:: 0.5
           Kể từ Flask 0.5 các hàm được đăng ký để thực thi sau request
           được gọi theo thứ tự ngược lại với thứ tự đăng ký.

        :param response: một đối tượng :attr:`response_class`.
        :return: một đối tượng phản hồi mới hoặc giống nhau, phải là một
                 thể hiện của :attr:`response_class`.
        """
        ctx = _cv_app.get()

        for func in ctx._after_request_functions:
            response = self.ensure_sync(func)(response)

        for name in chain(ctx.request.blueprints, (None,)):
            if name in self.after_request_funcs:
                for func in reversed(self.after_request_funcs[name]):
                    response = self.ensure_sync(func)(response)

        if not self.session_interface.is_null_session(ctx.session):
            self.session_interface.save_session(self, ctx.session, response)

        return response

    def do_teardown_request(self, exc: BaseException | None = None) -> None:
        """Được gọi sau khi request được điều phối và phản hồi được hoàn thiện,
        ngay trước khi ngữ cảnh request bị pop. Được gọi bởi
        :meth:`.AppContext.pop`.

        Điều này gọi tất cả các hàm được trang trí với :meth:`teardown_request`, và
        :meth:`Blueprint.teardown_request` nếu một blueprint xử lý request.
        Cuối cùng, tín hiệu :data:`request_tearing_down` được gửi đi.

        :param exc: Một ngoại lệ không được xử lý được ném ra trong khi điều phối request.
            Được truyền cho mỗi hàm teardown.

        .. versionchanged:: 0.9
            Đã thêm đối số ``exc``.
        """
        req = _cv_app.get().request

        for name in chain(req.blueprints, (None,)):
            if name in self.teardown_request_funcs:
                for func in reversed(self.teardown_request_funcs[name]):
                    self.ensure_sync(func)(exc)

        request_tearing_down.send(self, _async_wrapper=self.ensure_sync, exc=exc)

    def do_teardown_appcontext(self, exc: BaseException | None = None) -> None:
        """Được gọi ngay trước khi ngữ cảnh ứng dụng bị pop. Được gọi bởi
        :meth:`.AppContext.pop`.

        Điều này gọi tất cả các hàm được trang trí với :meth:`teardown_appcontext`.
        Sau đó tín hiệu :data:`appcontext_tearing_down` được gửi đi.

        :param exc: Một ngoại lệ không được xử lý được ném ra trong khi ngữ cảnh đang hoạt động.
            Được truyền cho mỗi hàm teardown.

        .. versionadded:: 0.9
        """
        for func in reversed(self.teardown_appcontext_funcs):
            self.ensure_sync(func)(exc)

        appcontext_tearing_down.send(self, _async_wrapper=self.ensure_sync, exc=exc)

    def app_context(self) -> AppContext:
        """Tạo một :class:`.AppContext`. Khi ngữ cảnh được push,
        :data:`.current_app` và :data:`.g` trở nên khả dụng.

        Một ngữ cảnh được tự động push khi xử lý mỗi request, và khi
        chạy bất kỳ lệnh CLI ``flask`` nào. Sử dụng cái này như một khối ``with`` để
        push thủ công một ngữ cảnh bên ngoài những tình huống đó, chẳng hạn như trong quá trình
        thiết lập hoặc kiểm tra.

        .. code-block:: python

            with app.app_context():
                init_db()

        Xem :doc:`/appcontext`.

        .. versionadded:: 0.9
        """
        return AppContext(self)

    def request_context(self, environ: WSGIEnvironment) -> AppContext:
        """Tạo một :class:`.AppContext` với thông tin request đại diện cho
        môi trường WSGI đã cho. Một ngữ cảnh được tự động push khi
        xử lý mỗi request. Khi ngữ cảnh được push, :data:`.request`,
        :data:`.session`, :data:`g:, và :data:`.current_app` trở nên khả dụng.

        Phương thức này không nên được sử dụng trong mã của riêng bạn. Tạo một WSGI
        environ hợp lệ không phải là tầm thường. Sử dụng :meth:`test_request_context` để
        tạo chính xác một WSGI environ và ngữ cảnh request thay thế.

        Xem :doc:`/appcontext`.

        :param environ: Một môi trường WSGI.
        """
        return AppContext.from_environ(self, environ)

    def test_request_context(self, *args: t.Any, **kwargs: t.Any) -> AppContext:
        """Tạo một :class:`.AppContext` với thông tin request được tạo từ
        các đối số đã cho. Khi ngữ cảnh được push, :data:`.request`,
        :data:`.session`, :data:`g:, và :data:`.current_app` trở nên khả dụng.

        Điều này hữu ích trong quá trình kiểm tra để chạy một hàm sử dụng dữ liệu request
        mà không cần điều phối một request đầy đủ. Sử dụng cái này như một khối ``with`` để push
        một ngữ cảnh.

        .. code-block:: python

            with app.test_request_context(...):
                generate_report()

        Xem :doc:`/appcontext`.

        Nhận các đối số giống như :class:`~werkzeug.test.EnvironBuilder` của
        Werkzeug, với một số mặc định từ
        ứng dụng. Xem tài liệu Werkzeug được liên kết để biết hầu hết các
        đối số có sẵn. Hành vi cụ thể của Flask được liệt kê ở đây.

        :param path: Đường dẫn URL đang được yêu cầu.
        :param base_url: URL cơ sở nơi ứng dụng đang được phục vụ, mà
            ``path`` là tương đối với nó. Nếu không được đưa ra, được xây dựng từ
            :data:`PREFERRED_URL_SCHEME`, ``subdomain``, :data:`SERVER_NAME`,
            và :data:`APPLICATION_ROOT`.
        :param subdomain: Tên subdomain để thêm vào trước :data:`SERVER_NAME`.
        :param url_scheme: Scheme để sử dụng thay vì
            :data:`PREFERRED_URL_SCHEME`.
        :param data: Văn bản hoặc byte phần thân request, hoặc một dict dữ liệu form.
        :param json: Nếu được đưa ra, cái này được tuần tự hóa thành JSON và được truyền dưới dạng
            ``data``. Cũng mặc định ``content_type`` thành
            ``application/json``.
        :param args: Các đối số vị trí khác được truyền cho
            :class:`~werkzeug.test.EnvironBuilder`.
        :param kwargs: Các đối số từ khóa khác được truyền cho
            :class:`~werkzeug.test.EnvironBuilder`.
        """
        from .testing import EnvironBuilder

        builder = EnvironBuilder(self, *args, **kwargs)

        try:
            environ = builder.get_environ()
        finally:
            builder.close()

        return self.request_context(environ)

    def wsgi_app(
        self, environ: WSGIEnvironment, start_response: StartResponse
    ) -> cabc.Iterable[bytes]:
        """Ứng dụng WSGI thực tế. Điều này không được triển khai trong
        :meth:`__call__` để các middleware có thể được áp dụng mà không
        làm mất tham chiếu đến đối tượng app. Thay vì làm điều này::

            app = MyMiddleware(app)

        Tốt hơn là làm điều này thay thế::

            app.wsgi_app = MyMiddleware(app.wsgi_app)

        Sau đó, bạn vẫn có đối tượng ứng dụng ban đầu xung quanh và
        có thể tiếp tục gọi các phương thức trên nó.

        .. versionchanged:: 0.7
            Các sự kiện teardown cho request và ngữ cảnh ứng dụng được gọi
            ngay cả khi xảy ra lỗi không được xử lý. Các sự kiện khác có thể không được
            gọi tùy thuộc vào thời điểm xảy ra lỗi trong quá trình điều phối.

        :param environ: Một môi trường WSGI.
        :param start_response: Một callable chấp nhận mã trạng thái,
            một danh sách các header, và một ngữ cảnh ngoại lệ tùy chọn để
            bắt đầu phản hồi.
        """
        ctx = self.request_context(environ)
        error: BaseException | None = None
        try:
            try:
                ctx.push()
                response = self.full_dispatch_request()
            except Exception as e:
                error = e
                response = self.handle_exception(e)
            except:  # noqa: B001
                error = sys.exc_info()[1]
                raise
            return response(environ, start_response)
        finally:
            if "werkzeug.debug.preserve_context" in environ:
                environ["werkzeug.debug.preserve_context"](_cv_app.get())

            if error is not None and self.should_ignore_error(error):
                error = None

            ctx.pop(error)

    def __call__(
        self, environ: WSGIEnvironment, start_response: StartResponse
    ) -> cabc.Iterable[bytes]:
        """Server WSGI gọi đối tượng ứng dụng Flask như là
        ứng dụng WSGI. Điều này gọi :meth:`wsgi_app`, có thể được
        bao bọc để áp dụng middleware.
        """
        return self.wsgi_app(environ, start_response)
