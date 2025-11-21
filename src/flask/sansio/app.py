from __future__ import annotations

import logging
import os
import sys
import typing as t
from datetime import timedelta
from itertools import chain

from werkzeug.exceptions import Aborter
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import BadRequestKeyError
from werkzeug.routing import BuildError
from werkzeug.routing import Map
from werkzeug.routing import Rule
from werkzeug.sansio.response import Response
from werkzeug.utils import cached_property
from werkzeug.utils import redirect as _wz_redirect

from .. import typing as ft
from ..config import Config
from ..config import ConfigAttribute
from ..ctx import _AppCtxGlobals
from ..helpers import _split_blueprint_path
from ..helpers import get_debug_flag
from ..json.provider import DefaultJSONProvider
from ..json.provider import JSONProvider
from ..logging import create_logger
from ..templating import DispatchingJinjaLoader
from ..templating import Environment
from .scaffold import _endpoint_from_view_func
from .scaffold import find_package
from .scaffold import Scaffold
from .scaffold import setupmethod

if t.TYPE_CHECKING:  # pragma: no cover
    from werkzeug.wrappers import Response as BaseResponse

    from ..testing import FlaskClient
    from ..testing import FlaskCliRunner
    from .blueprints import Blueprint

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


class App(Scaffold):
    """Đối tượng flask triển khai một ứng dụng WSGI và đóng vai trò là đối tượng
    trung tâm. Nó được truyền tên của module hoặc package của
    ứng dụng. Sau khi được tạo, nó sẽ hoạt động như một sổ đăng ký trung tâm cho
    các hàm view, quy tắc URL, cấu hình template và nhiều thứ khác.

    Tên của package được sử dụng để giải quyết các tài nguyên từ bên trong
    package hoặc thư mục chứa module tùy thuộc vào việc tham số
    package giải quyết thành một package python thực tế (một thư mục với
    tệp :file:`__init__.py` bên trong) hay một module tiêu chuẩn (chỉ là một tệp ``.py``).

    Để biết thêm thông tin về việc tải tài nguyên, xem :func:`open_resource`.

    Thông thường bạn tạo một thể hiện :class:`Flask` trong module chính của bạn hoặc
    trong tệp :file:`__init__.py` của package của bạn như thế này::

        from flask import Flask
        app = Flask(__name__)

    .. admonition:: Về Tham Số Đầu Tiên

        Ý tưởng của tham số đầu tiên là cung cấp cho Flask một ý tưởng về những gì
        thuộc về ứng dụng của bạn. Tên này được sử dụng để tìm tài nguyên
        trên hệ thống tệp, có thể được sử dụng bởi các tiện ích mở rộng để cải thiện thông tin
        gỡ lỗi và nhiều hơn nữa.

        Vì vậy, điều quan trọng là bạn cung cấp gì ở đó. Nếu bạn đang sử dụng một module
        duy nhất, `__name__` luôn là giá trị chính xác. Tuy nhiên, nếu bạn đang
        sử dụng một package, thường nên hardcode tên của
        package của bạn ở đó.

        Ví dụ: nếu ứng dụng của bạn được định nghĩa trong :file:`yourapplication/app.py`
        bạn nên tạo nó với một trong hai phiên bản dưới đây::

            app = Flask('yourapplication')
            app = Flask(__name__.split('.')[0])

        Tại sao lại như vậy? Ứng dụng sẽ hoạt động ngay cả với `__name__`, nhờ
        vào cách tài nguyên được tra cứu. Tuy nhiên, nó sẽ làm cho việc gỡ lỗi trở nên
        khó khăn hơn. Một số tiện ích mở rộng có thể đưa ra giả định dựa trên
        tên import của ứng dụng của bạn. Ví dụ: tiện ích mở rộng Flask-SQLAlchemy
        sẽ tìm kiếm mã trong ứng dụng của bạn đã kích hoạt
        một truy vấn SQL trong chế độ debug. Nếu tên import không được thiết lập
        đúng, thông tin gỡ lỗi đó sẽ bị mất. (Ví dụ: nó sẽ chỉ
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
       Tham số ``subdomain_matching`` đã được thêm vào. Khớp tên miền phụ
       cần được bật thủ công ngay bây giờ. Việc thiết lập
       :data:`SERVER_NAME` không ngầm định kích hoạt nó.

    :param import_name: tên của package ứng dụng
    :param static_url_path: có thể được sử dụng để chỉ định một đường dẫn khác cho các
                            tệp tĩnh trên web. Mặc định là tên
                            của thư mục `static_folder`.
    :param static_folder: Thư mục chứa các tệp tĩnh được phục vụ tại
        ``static_url_path``. Tương đối với ``root_path`` của ứng dụng
        hoặc một đường dẫn tuyệt đối. Mặc định là ``'static'``.
    :param static_host: host để sử dụng khi thêm route tĩnh.
        Mặc định là None. Bắt buộc khi sử dụng ``host_matching=True``
        với một ``static_folder`` được cấu hình.
    :param host_matching: đặt thuộc tính ``url_map.host_matching``.
        Mặc định là False.
    :param subdomain_matching: xem xét tên miền phụ tương đối với
        :data:`SERVER_NAME` khi khớp các route. Mặc định là False.
    :param template_folder: thư mục chứa các template nên được
                            sử dụng bởi ứng dụng. Mặc định là
                            thư mục ``'templates'`` trong đường dẫn gốc của
                            ứng dụng.
    :param instance_path: Một đường dẫn instance thay thế cho ứng dụng.
                          Theo mặc định, thư mục ``'instance'`` cạnh
                          package hoặc module được giả định là đường dẫn
                          instance.
    :param instance_relative_config: nếu được đặt thành ``True`` các tên tệp tương đối
                                     để tải cấu hình được giả định
                                     là tương đối với đường dẫn instance thay vì
                                     gốc ứng dụng.
    :param root_path: Đường dẫn đến gốc của các tệp ứng dụng.
        Điều này chỉ nên được đặt thủ công khi nó không thể được phát hiện
        tự động, chẳng hạn như đối với các namespace package.
    """

    #: Lớp của đối tượng được gán cho :attr:`aborter`, được tạo bởi
    #: :meth:`create_aborter`. Đối tượng đó được gọi bởi
    #: :func:`flask.abort` để ném ra các lỗi HTTP, và cũng có thể được
    #: gọi trực tiếp.
    #:
    #: Mặc định là :class:`werkzeug.exceptions.Aborter`.
    #:
    #: .. versionadded:: 2.2
    aborter_class = Aborter

    #: Lớp được sử dụng cho môi trường Jinja.
    #:
    #: .. versionadded:: 0.11
    jinja_environment = Environment

    #: Lớp được sử dụng cho thể hiện :data:`~flask.g`.
    #:
    #: Ví dụ về các trường hợp sử dụng cho một lớp tùy chỉnh:
    #:
    #: 1. Lưu trữ các thuộc tính tùy ý trên flask.g.
    #: 2. Thêm một thuộc tính cho các kết nối cơ sở dữ liệu lười biếng theo yêu cầu.
    #: 3. Trả về None thay vì AttributeError trên các thuộc tính không mong đợi.
    #: 4. Ném ngoại lệ nếu một thuộc tính không mong đợi được đặt, một flask.g "được kiểm soát".
    #:
    #: .. versionadded:: 0.10
    #:     Đổi tên từ ``request_globals_class`.
    app_ctx_globals_class = _AppCtxGlobals

    #: Lớp được sử dụng cho thuộc tính ``config`` của ứng dụng này.
    #: Mặc định là :class:`~flask.Config`.
    #:
    #: Ví dụ về các trường hợp sử dụng cho một lớp tùy chỉnh:
    #:
    #: 1. Giá trị mặc định cho một số tùy chọn cấu hình nhất định.
    #: 2. Truy cập vào các giá trị cấu hình thông qua các thuộc tính ngoài các khóa.
    #:
    #: .. versionadded:: 0.11
    config_class = Config

    #: Cờ testing. Đặt cờ này thành ``True`` để kích hoạt chế độ test của
    #: các tiện ích mở rộng Flask (và trong tương lai có thể cả chính Flask).
    #: Ví dụ: điều này có thể kích hoạt các trình trợ giúp test có
    #: chi phí thời gian chạy bổ sung mà không nên được bật theo mặc định.
    #:
    #: Nếu điều này được bật và PROPAGATE_EXCEPTIONS không thay đổi từ
    #: mặc định, nó sẽ được kích hoạt ngầm.
    #:
    #: Thuộc tính này cũng có thể được cấu hình từ config với khóa
    #: cấu hình ``TESTING``. Mặc định là ``False``.
    testing = ConfigAttribute[bool]("TESTING")

    #: Nếu một khóa bí mật được đặt, các thành phần mật mã có thể sử dụng khóa này để
    #: ký cookie và những thứ khác. Đặt khóa này thành một giá trị ngẫu nhiên phức tạp
    #: khi bạn muốn sử dụng cookie an toàn chẳng hạn.
    #:
    #: Thuộc tính này cũng có thể được cấu hình từ config với khóa
    #: cấu hình :data:`SECRET_KEY`. Mặc định là ``None``.
    secret_key = ConfigAttribute[str | bytes | None]("SECRET_KEY")

    #: Một :class:`~datetime.timedelta` được sử dụng để đặt ngày hết hạn
    #: của một phiên vĩnh viễn. Mặc định là 31 ngày, làm cho một
    #: phiên vĩnh viễn tồn tại trong khoảng một tháng.
    #:
    #: Thuộc tính này cũng có thể được cấu hình từ config với khóa
    #: cấu hình ``PERMANENT_SESSION_LIFETIME``. Mặc định là
    #: ``timedelta(days=31)``
    permanent_session_lifetime = ConfigAttribute[timedelta](
        "PERMANENT_SESSION_LIFETIME",
        get_converter=_make_timedelta,  # type: ignore[arg-type]
    )

    json_provider_class: type[JSONProvider] = DefaultJSONProvider
    """Một lớp con của :class:`~flask.json.provider.JSONProvider`. Một
    thể hiện được tạo và gán cho :attr:`app.json` khi tạo
    ứng dụng.

    Mặc định, :class:`~flask.json.provider.DefaultJSONProvider`, sử dụng
    thư viện :mod:`json` tích hợp sẵn của Python. Một provider khác có thể sử dụng
    một thư viện JSON khác.

    .. versionadded:: 2.2
    """

    #: Các tùy chọn được truyền cho môi trường Jinja trong
    #: :meth:`create_jinja_environment`. Thay đổi các tùy chọn này sau khi
    #: môi trường được tạo (truy cập :attr:`jinja_env`) sẽ
    #: không có hiệu lực.
    #:
    #: .. versionchanged:: 1.1.0
    #:     Đây là một ``dict`` thay vì một ``ImmutableDict`` để cho phép
    #:     cấu hình dễ dàng hơn.
    #:
    jinja_options: dict[str, t.Any] = {}

    #: Đối tượng quy tắc để sử dụng cho các quy tắc URL được tạo. Điều này được sử dụng bởi
    #: :meth:`add_url_rule`. Mặc định là :class:`werkzeug.routing.Rule`.
    #:
    #: .. versionadded:: 0.7
    url_rule_class = Rule

    #: Đối tượng bản đồ để sử dụng để lưu trữ các quy tắc URL và các tham số
    #: cấu hình định tuyến. Mặc định là :class:`werkzeug.routing.Map`.
    #:
    #: .. versionadded:: 1.1.0
    url_map_class = Map

    #: Phương thức :meth:`test_client` tạo ra một thể hiện của lớp test
    #: client này. Mặc định là :class:`~flask.testing.FlaskClient`.
    #:
    #: .. versionadded:: 0.7
    test_client_class: type[FlaskClient] | None = None

    #: Lớp con :class:`~click.testing.CliRunner`, theo mặc định là
    #: :class:`~flask.testing.FlaskCliRunner` được sử dụng bởi
    #: :meth:`test_cli_runner`. Phương thức ``__init__`` của nó nên nhận một
    #: đối tượng ứng dụng Flask làm đối số đầu tiên.
    #:
    #: .. versionadded:: 1.0
    test_cli_runner_class: type[FlaskCliRunner] | None = None

    default_config: dict[str, t.Any]
    response_class: type[Response]

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
    ) -> None:
        super().__init__(
            import_name=import_name,
            static_folder=static_folder,
            static_url_path=static_url_path,
            template_folder=template_folder,
            root_path=root_path,
        )

        if instance_path is None:
            instance_path = self.auto_find_instance_path()
        elif not os.path.isabs(instance_path):
            raise ValueError(
                "If an instance path is provided it must be absolute."
                " A relative path was given instead."
            )

        #: Giữ đường dẫn đến thư mục instance.
        #:
        #: .. versionadded:: 0.8
        self.instance_path = instance_path

        #: Từ điển cấu hình như :class:`Config`. Điều này hoạt động
        #: chính xác như một từ điển thông thường nhưng hỗ trợ các phương thức bổ sung
        #: để tải cấu hình từ các tệp.
        self.config = self.make_config(instance_relative_config)

        #: Một thể hiện của :attr:`aborter_class` được tạo bởi
        #: :meth:`make_aborter`. Điều này được gọi bởi :func:`flask.abort`
        #: để ném ra các lỗi HTTP, và cũng có thể được gọi trực tiếp.
        #:
        #: .. versionadded:: 2.2
        #:     Được chuyển từ ``flask.abort``, gọi đối tượng này.
        self.aborter = self.make_aborter()

        self.json: JSONProvider = self.json_provider_class(self)
        """Cung cấp quyền truy cập vào các phương thức JSON. Các hàm trong ``flask.json``
        sẽ gọi các phương thức trên provider này khi ngữ cảnh ứng dụng
        đang hoạt động. Được sử dụng để xử lý các yêu cầu và phản hồi JSON.

        Một thể hiện của :attr:`json_provider_class`. Có thể được tùy chỉnh bằng cách
        thay đổi thuộc tính đó trên một lớp con, hoặc bằng cách gán cho thuộc tính này
        sau đó.

        Mặc định, :class:`~flask.json.provider.DefaultJSONProvider`,
        sử dụng thư viện :mod:`json` tích hợp sẵn của Python. Một provider khác
        có thể sử dụng một thư viện JSON khác.

        .. versionadded:: 2.2
        """

        #: Một danh sách các hàm được gọi bởi
        #: :meth:`handle_url_build_error` khi :meth:`.url_for` ném ra một
        #: :exc:`~werkzeug.routing.BuildError`. Mỗi hàm được gọi
        #: với ``error``, ``endpoint`` và ``values``. Nếu một hàm
        #: trả về ``None`` hoặc ném ra một ``BuildError``, nó sẽ bị bỏ qua.
        #: Ngược lại, giá trị trả về của nó được trả về bởi ``url_for``.
        #:
        #: .. versionadded:: 0.9
        self.url_build_error_handlers: list[
            t.Callable[[Exception, str, dict[str, t.Any]], str]
        ] = []

        #: Một danh sách các hàm được gọi khi ngữ cảnh ứng dụng
        #: bị hủy. Vì ngữ cảnh ứng dụng cũng bị hủy
        #: nếu yêu cầu kết thúc, đây là nơi để lưu trữ mã ngắt kết nối
        #: khỏi cơ sở dữ liệu.
        #:
        #: .. versionadded:: 0.9
        self.teardown_appcontext_funcs: list[ft.TeardownCallable] = []

        #: Một danh sách các hàm xử lý ngữ cảnh shell nên được chạy
        #: khi một ngữ cảnh shell được tạo.
        #:
        #: .. versionadded:: 0.11
        self.shell_context_processors: list[ft.ShellContextProcessorCallable] = []

        #: Ánh xạ tên blueprint đã đăng ký với các đối tượng blueprint.
        #: Dict giữ lại thứ tự các blueprint được đăng ký.
        #: Các blueprint có thể được đăng ký nhiều lần, dict này không
        #: theo dõi tần suất chúng được đính kèm.
        #:
        #: .. versionadded:: 0.7
        self.blueprints: dict[str, Blueprint] = {}

        #: một nơi mà các tiện ích mở rộng có thể lưu trữ trạng thái cụ thể của ứng dụng. Ví dụ
        #: đây là nơi một tiện ích mở rộng có thể lưu trữ các engine cơ sở dữ liệu và
        #: những thứ tương tự.
        #:
        #: Khóa phải khớp với tên của module tiện ích mở rộng. Ví dụ trong
        #: trường hợp của một tiện ích mở rộng "Flask-Foo" trong `flask_foo`, khóa sẽ là
        #: ``'foo'``.
        #:
        #: .. versionadded:: 0.7
        self.extensions: dict[str, t.Any] = {}

        #: :class:`~werkzeug.routing.Map` cho thể hiện này. Bạn có thể sử dụng
        #: điều này để thay đổi các bộ chuyển đổi định tuyến sau khi lớp được tạo
        #: nhưng trước khi bất kỳ route nào được kết nối. Ví dụ::
        #:
        #:    from werkzeug.routing import BaseConverter
        #:
        #:    class ListConverter(BaseConverter):
        #:        def to_python(self, value):
        #:            return value.split(',')
        #:        def to_url(self, values):
        #:            return ','.join(super(ListConverter, self).to_url(value)
        #:                            for value in values)
        #:
        #:    app = Flask(__name__)
        #:    app.url_map.converters['list'] = ListConverter
        self.url_map = self.url_map_class(host_matching=host_matching)

        self.subdomain_matching = subdomain_matching

        # theo dõi nội bộ nếu ứng dụng đã xử lý ít nhất một
        # yêu cầu.
        self._got_first_request = False

    def _check_setup_finished(self, f_name: str) -> None:
        if self._got_first_request:
            raise AssertionError(
                f"The setup method '{f_name}' can no longer be called"
                " on the application. It has already handled its first"
                " request, any changes will not be applied"
                " consistently.\n"
                "Make sure all imports, decorators, functions, etc."
                " needed to set up the application are done before"
                " running it."
            )

    @cached_property
    def name(self) -> str:
        """Tên của ứng dụng. Đây thường là tên import
        với sự khác biệt là nó được đoán từ tệp chạy nếu tên
        import là main. Tên này được sử dụng làm tên hiển thị khi
        Flask cần tên của ứng dụng. Nó có thể được đặt và ghi đè
        để thay đổi giá trị.

        .. versionadded:: 0.8
        """
        if self.import_name == "__main__":
            fn: str | None = getattr(sys.modules["__main__"], "__file__", None)
            if fn is None:
                return "__main__"
            return os.path.splitext(os.path.basename(fn))[0]
        return self.import_name

    @cached_property
    def logger(self) -> logging.Logger:
        """Một :class:`~logging.Logger` Python tiêu chuẩn cho ứng dụng, với
        cùng tên như :attr:`name`.

        Trong chế độ debug, :attr:`~logging.Logger.level` của logger sẽ
        được đặt thành :data:`~logging.DEBUG`.

        Nếu không có trình xử lý nào được cấu hình, một trình xử lý mặc định sẽ được
        thêm vào. Xem :doc:`/logging` để biết thêm thông tin.

        .. versionchanged:: 1.1.0
            Logger lấy cùng tên như :attr:`name` thay vì
            hard-code ``"flask.app"``.

        .. versionchanged:: 1.0.0
            Hành vi đã được đơn giản hóa. Logger luôn được đặt tên là
            ``"flask.app"``. Mức độ chỉ được đặt trong quá trình cấu hình,
            nó không kiểm tra ``app.debug`` mỗi lần. Chỉ một định dạng được
            sử dụng, không phải các định dạng khác nhau tùy thuộc vào ``app.debug``. Không có
            trình xử lý nào bị xóa, và một trình xử lý chỉ được thêm vào nếu không có
            trình xử lý nào đã được cấu hình.

        .. versionadded:: 0.3
        """
        return create_logger(self)

    @cached_property
    def jinja_env(self) -> Environment:
        """Môi trường Jinja được sử dụng để tải các template.

        Môi trường được tạo lần đầu tiên thuộc tính này được
        truy cập. Thay đổi :attr:`jinja_options` sau đó sẽ không có
        hiệu lực.
        """
        return self.create_jinja_environment()

    def create_jinja_environment(self) -> Environment:
        raise NotImplementedError()

    def make_config(self, instance_relative: bool = False) -> Config:
        """Được sử dụng để tạo thuộc tính config bởi hàm tạo Flask.
        Tham số `instance_relative` được truyền vào từ hàm tạo
        của Flask (ở đó có tên `instance_relative_config`) và chỉ ra liệu
        cấu hình có nên tương đối với đường dẫn instance hay đường dẫn gốc
        của ứng dụng.

        .. versionadded:: 0.8
        """
        root_path = self.root_path
        if instance_relative:
            root_path = self.instance_path
        defaults = dict(self.default_config)
        defaults["DEBUG"] = get_debug_flag()
        return self.config_class(root_path, defaults)

    def make_aborter(self) -> Aborter:
        """Tạo đối tượng để gán cho :attr:`aborter`. Đối tượng đó
        được gọi bởi :func:`flask.abort` để ném ra các lỗi HTTP, và có thể
        được gọi trực tiếp.

        Mặc định, điều này tạo ra một thể hiện của :attr:`aborter_class`,
        mặc định là :class:`werkzeug.exceptions.Aborter`.

        .. versionadded:: 2.2
        """
        return self.aborter_class()

    def auto_find_instance_path(self) -> str:
        """Cố gắng định vị đường dẫn instance nếu nó không được cung cấp cho
        hàm tạo của lớp ứng dụng. Về cơ bản nó sẽ tính toán
        đường dẫn đến một thư mục có tên ``instance`` cạnh tệp chính của bạn hoặc
        package.

        .. versionadded:: 0.8
        """
        prefix, package_path = find_package(self.import_name)
        if prefix is None:
            return os.path.join(package_path, "instance")
        return os.path.join(prefix, "var", f"{self.name}-instance")

    def create_global_jinja_loader(self) -> DispatchingJinjaLoader:
        """Tạo loader cho môi trường Jinja. Có thể được sử dụng để
        ghi đè chỉ loader và giữ nguyên phần còn lại. Không khuyến khích
        ghi đè hàm này. Thay vào đó, người ta nên ghi đè
        hàm :meth:`jinja_loader`.

        Loader toàn cục phân phối giữa các loader của ứng dụng
        và các blueprint riêng lẻ.

        .. versionadded:: 0.7
        """
        return DispatchingJinjaLoader(self)

    def select_jinja_autoescape(self, filename: str) -> bool:
        """Trả về ``True`` nếu autoescaping nên được kích hoạt cho tên
        template đã cho. Nếu không có tên template nào được đưa ra, trả về `True`.

        .. versionchanged:: 2.2
            Autoescaping hiện được bật theo mặc định cho các tệp ``.svg``.

        .. versionadded:: 0.5
        """
        if filename is None:
            return True
        return filename.endswith((".html", ".htm", ".xml", ".xhtml", ".svg"))

    @property
    def debug(self) -> bool:
        """Liệu chế độ debug có được bật hay không. Khi sử dụng ``flask run`` để bắt đầu
        máy chủ phát triển, một trình gỡ lỗi tương tác sẽ được hiển thị cho các ngoại lệ
        không được xử lý, và máy chủ sẽ được tải lại khi mã thay đổi. Điều này ánh xạ tới
        khóa cấu hình :data:`DEBUG`. Nó có thể không hoạt động như mong đợi nếu được đặt muộn.

        **Không bật chế độ debug khi triển khai trong sản xuất.**

        Mặc định: ``False``
        """
        return self.config["DEBUG"]  # type: ignore[no-any-return]

    @debug.setter
    def debug(self, value: bool) -> None:
        self.config["DEBUG"] = value

        if self.config["TEMPLATES_AUTO_RELOAD"] is None:
            self.jinja_env.auto_reload = value

    @setupmethod
    def register_blueprint(self, blueprint: Blueprint, **options: t.Any) -> None:
        """Đăng ký một :class:`~flask.Blueprint` trên ứng dụng. Các đối số
        từ khóa được truyền cho phương thức này sẽ ghi đè các mặc định được đặt trên
        blueprint.

        Gọi phương thức :meth:`~flask.Blueprint.register` của blueprint sau khi
        ghi lại blueprint trong :attr:`blueprints` của ứng dụng.

        :param blueprint: Blueprint để đăng ký.
        :param url_prefix: Các route của Blueprint sẽ được thêm tiền tố này.
        :param subdomain: Các route của Blueprint sẽ khớp trên tên miền phụ này.
        :param url_defaults: Các route của Blueprint sẽ sử dụng các giá trị mặc định này cho
            các đối số view.
        :param options: Các đối số từ khóa bổ sung được truyền cho
            :class:`~flask.blueprints.BlueprintSetupState`. Chúng có thể được
            truy cập trong các callback :meth:`~flask.Blueprint.record`.

        .. versionchanged:: 2.0.1
            Tùy chọn ``name`` có thể được sử dụng để thay đổi tên (trước khi có dấu chấm)
            mà blueprint được đăng ký. Điều này cho phép cùng một
            blueprint được đăng ký nhiều lần với các tên duy nhất
            cho ``url_for``.

        .. versionadded:: 0.7
        """
        blueprint.register(self, options)

    def iter_blueprints(self) -> t.ValuesView[Blueprint]:
        """Lặp qua tất cả các blueprint theo thứ tự chúng được đăng ký.

        .. versionadded:: 0.11
        """
        return self.blueprints.values()

    @setupmethod
    def add_url_rule(
        self,
        rule: str,
        endpoint: str | None = None,
        view_func: ft.RouteCallable | None = None,
        provide_automatic_options: bool | None = None,
        **options: t.Any,
    ) -> None:
        if endpoint is None:
            endpoint = _endpoint_from_view_func(view_func)  # type: ignore
        options["endpoint"] = endpoint
        methods = options.pop("methods", None)

        # if the methods are not given and the view_func object knows its
        # methods we can use that instead.  If neither exists, we go with
        # a tuple of only ``GET`` as default.
        if methods is None:
            methods = getattr(view_func, "methods", None) or ("GET",)
        if isinstance(methods, str):
            raise TypeError(
                "Allowed methods must be a list of strings, for"
                ' example: @app.route(..., methods=["POST"])'
            )
        methods = {item.upper() for item in methods}

        # Methods that should always be added
        required_methods: set[str] = set(getattr(view_func, "required_methods", ()))

        # starting with Flask 0.8 the view_func object can disable and
        # force-enable the automatic options handling.
        if provide_automatic_options is None:
            provide_automatic_options = getattr(
                view_func, "provide_automatic_options", None
            )

        if provide_automatic_options is None:
            if "OPTIONS" not in methods and self.config["PROVIDE_AUTOMATIC_OPTIONS"]:
                provide_automatic_options = True
                required_methods.add("OPTIONS")
            else:
                provide_automatic_options = False

        # Add the required methods now.
        methods |= required_methods

        rule_obj = self.url_rule_class(rule, methods=methods, **options)
        rule_obj.provide_automatic_options = provide_automatic_options  # type: ignore[attr-defined]

        self.url_map.add(rule_obj)
        if view_func is not None:
            old_func = self.view_functions.get(endpoint)
            if old_func is not None and old_func != view_func:
                raise AssertionError(
                    "View function mapping is overwriting an existing"
                    f" endpoint function: {endpoint}"
                )
            self.view_functions[endpoint] = view_func

    @t.overload
    def template_filter(self, name: T_template_filter) -> T_template_filter: ...
    @t.overload
    def template_filter(
        self, name: str | None = None
    ) -> t.Callable[[T_template_filter], T_template_filter]: ...
    @setupmethod
    def template_filter(
        self, name: T_template_filter | str | None = None
    ) -> T_template_filter | t.Callable[[T_template_filter], T_template_filter]:
        """Trang trí một hàm để đăng ký nó như một bộ lọc Jinja tùy chỉnh. Tên
        là tùy chọn. Decorator có thể được sử dụng mà không cần dấu ngoặc đơn.

        .. code-block:: python

            @app.template_filter("reverse")
            def reverse_filter(s):
                return reversed(s)

        Phương thức :meth:`add_template_filter` có thể được sử dụng để đăng ký một
        hàm sau đó thay vì trang trí.

        :param name: Tên để đăng ký bộ lọc. Nếu không được đưa ra, sử dụng
            tên của hàm.
        """
        if callable(name):
            self.add_template_filter(name)
            return name

        def decorator(f: T_template_filter) -> T_template_filter:
            self.add_template_filter(f, name=name)
            return f

        return decorator

    @setupmethod
    def add_template_filter(
        self, f: ft.TemplateFilterCallable, name: str | None = None
    ) -> None:
        """Đăng ký một hàm để sử dụng như một bộ lọc Jinja tùy chỉnh.

        Decorator :meth:`template_filter` có thể được sử dụng để đăng ký một hàm
        bằng cách trang trí thay thế.

        :param f: Hàm để đăng ký.
        :param name: Tên để đăng ký bộ lọc. Nếu không được đưa ra, sử dụng
            tên của hàm.
        """
        self.jinja_env.filters[name or f.__name__] = f

    @t.overload
    def template_test(self, name: T_template_test) -> T_template_test: ...
    @t.overload
    def template_test(
        self, name: str | None = None
    ) -> t.Callable[[T_template_test], T_template_test]: ...
    @setupmethod
    def template_test(
        self, name: T_template_test | str | None = None
    ) -> T_template_test | t.Callable[[T_template_test], T_template_test]:
        """Trang trí một hàm để đăng ký nó như một test Jinja tùy chỉnh. Tên
        là tùy chọn. Decorator có thể được sử dụng mà không cần dấu ngoặc đơn.

        .. code-block:: python

            @app.template_test("prime")
            def is_prime_test(n):
                if n == 2:
                    return True
                for i in range(2, int(math.ceil(math.sqrt(n))) + 1):
                    if n % i == 0:
                        return False
              return True

        Phương thức :meth:`add_template_test` có thể được sử dụng để đăng ký một hàm
        sau đó thay vì trang trí.

        :param name: Tên để đăng ký bộ lọc. Nếu không được đưa ra, sử dụng
            tên của hàm.

        .. versionadded:: 0.10
        """
        if callable(name):
            self.add_template_test(name)
            return name

        def decorator(f: T_template_test) -> T_template_test:
            self.add_template_test(f, name=name)
            return f

        return decorator

    @setupmethod
    def add_template_test(
        self, f: ft.TemplateTestCallable, name: str | None = None
    ) -> None:
        """Đăng ký một hàm để sử dụng như một test Jinja tùy chỉnh.

        Decorator :meth:`template_test` có thể được sử dụng để đăng ký một hàm
        bằng cách trang trí thay thế.

        :param f: Hàm để đăng ký.
        :param name: Tên để đăng ký test. Nếu không được đưa ra, sử dụng
            tên của hàm.

        .. versionadded:: 0.10
        """
        self.jinja_env.tests[name or f.__name__] = f

    @t.overload
    def template_global(self, name: T_template_global) -> T_template_global: ...
    @t.overload
    def template_global(
        self, name: str | None = None
    ) -> t.Callable[[T_template_global], T_template_global]: ...
    @setupmethod
    def template_global(
        self, name: T_template_global | str | None = None
    ) -> T_template_global | t.Callable[[T_template_global], T_template_global]:
        """Trang trí một hàm để đăng ký nó như một global Jinja tùy chỉnh. Tên
        là tùy chọn. Decorator có thể được sử dụng mà không cần dấu ngoặc đơn.

        .. code-block:: python

            @app.template_global
            def double(n):
                return 2 * n

        Phương thức :meth:`add_template_global` có thể được sử dụng để đăng ký một
        hàm sau đó thay vì trang trí.

        :param name: Tên để đăng ký global. Nếu không được đưa ra, sử dụng
            tên của hàm.

        .. versionadded:: 0.10
        """
        if callable(name):
            self.add_template_global(name)
            return name

        def decorator(f: T_template_global) -> T_template_global:
            self.add_template_global(f, name=name)
            return f

        return decorator

    @setupmethod
    def add_template_global(
        self, f: ft.TemplateGlobalCallable, name: str | None = None
    ) -> None:
        """Đăng ký một hàm để sử dụng như một global Jinja tùy chỉnh.

        Decorator :meth:`template_global` có thể được sử dụng để đăng ký một hàm
        bằng cách trang trí thay thế.

        :param f: Hàm để đăng ký.
        :param name: Tên để đăng ký global. Nếu không được đưa ra, sử dụng
            tên của hàm.

        .. versionadded:: 0.10
        """
        self.jinja_env.globals[name or f.__name__] = f

    @setupmethod
    def teardown_appcontext(self, f: T_teardown) -> T_teardown:
        """Đăng ký một hàm để được gọi khi ngữ cảnh ứng dụng bị pop. Ngữ cảnh
        được pop vào cuối một yêu cầu, lệnh CLI, hoặc khối ``with`` thủ công.

        .. code-block:: python

            with app.app_context():
                ...

        Khi khối ``with`` thoát (hoặc ``ctx.pop()`` được gọi), các
        hàm teardown được gọi ngay trước khi ngữ cảnh ứng dụng
        trở nên không hoạt động.

        Khi một hàm teardown được gọi vì một ngoại lệ không được xử lý
        nó sẽ được truyền một đối tượng lỗi. Nếu một
        :meth:`errorhandler` được đăng ký, nó sẽ xử lý ngoại lệ
        và teardown sẽ không nhận được nó.

        Các hàm teardown phải tránh ném ngoại lệ. Nếu chúng
        thực thi mã có thể thất bại, chúng phải bao quanh mã đó bằng một
        khối ``try``/``except`` và ghi lại bất kỳ lỗi nào.

        Các giá trị trả về của các hàm teardown bị bỏ qua.

        .. versionadded:: 0.9
        """
        self.teardown_appcontext_funcs.append(f)
        return f

    @setupmethod
    def shell_context_processor(
        self, f: T_shell_context_processor
    ) -> T_shell_context_processor:
        """Đăng ký một hàm xử lý ngữ cảnh shell.

        .. versionadded:: 0.11
        """
        self.shell_context_processors.append(f)
        return f

    def _find_error_handler(
        self, e: Exception, blueprints: list[str]
    ) -> ft.ErrorHandlerCallable | None:
        """Trả về một trình xử lý lỗi đã đăng ký cho một ngoại lệ theo thứ tự này:
        trình xử lý blueprint cho một mã cụ thể, trình xử lý ứng dụng cho một mã cụ thể,
        trình xử lý blueprint cho một lớp ngoại lệ, trình xử lý ứng dụng cho một lớp
        ngoại lệ, hoặc ``None`` nếu không tìm thấy trình xử lý phù hợp.
        """
        exc_class, code = self._get_exc_class_and_code(type(e))
        names = (*blueprints, None)

        for c in (code, None) if code is not None else (None,):
            for name in names:
                handler_map = self.error_handler_spec[name][c]

                if not handler_map:
                    continue

                for cls in exc_class.__mro__:
                    handler = handler_map.get(cls)

                    if handler is not None:
                        return handler
        return None

    def trap_http_exception(self, e: Exception) -> bool:
        """Kiểm tra xem một ngoại lệ HTTP có nên bị bẫy hay không. Theo mặc định
        điều này sẽ trả về ``False`` cho tất cả các ngoại lệ ngoại trừ lỗi bad request
        key nếu ``TRAP_BAD_REQUEST_ERRORS`` được đặt thành ``True``. Nó
        cũng trả về ``True`` nếu ``TRAP_HTTP_EXCEPTIONS`` được đặt thành ``True``.

        Điều này được gọi cho tất cả các ngoại lệ HTTP được ném ra bởi một hàm view.
        Nếu nó trả về ``True`` cho bất kỳ ngoại lệ nào, trình xử lý lỗi cho ngoại lệ này
        không được gọi và nó hiển thị như một ngoại lệ thông thường trong
        traceback. Điều này hữu ích để gỡ lỗi các ngoại lệ HTTP được ném ra
        ngầm định.

        .. versionchanged:: 1.0
            Lỗi bad request không bị bẫy theo mặc định trong chế độ debug.

        .. versionadded:: 0.8
        """
        if self.config["TRAP_HTTP_EXCEPTIONS"]:
            return True

        trap_bad_request = self.config["TRAP_BAD_REQUEST_ERRORS"]

        # if unset, trap key errors in debug mode
        if (
            trap_bad_request is None
            and self.debug
            and isinstance(e, BadRequestKeyError)
        ):
            return True

        if trap_bad_request:
            return isinstance(e, BadRequest)

        return False

    def should_ignore_error(self, error: BaseException | None) -> bool:
        """Điều này được gọi để tìm ra liệu một lỗi có nên bị bỏ qua
        hay không theo như hệ thống teardown quan tâm. Nếu hàm này
        trả về ``True`` thì các trình xử lý teardown sẽ không được
        truyền lỗi.

        .. versionadded:: 0.10
        """
        return False

    def redirect(self, location: str, code: int = 302) -> BaseResponse:
        """Tạo một đối tượng phản hồi chuyển hướng.

        Điều này được gọi bởi :func:`flask.redirect`, và có thể được gọi
        trực tiếp.

        :param location: URL để chuyển hướng đến.
        :param code: Mã trạng thái cho chuyển hướng.

        .. versionadded:: 2.2
            Được chuyển từ ``flask.redirect``, gọi phương thức này.
        """
        return _wz_redirect(
            location,
            code=code,
            Response=self.response_class,  # type: ignore[arg-type]
        )

    def inject_url_defaults(self, endpoint: str, values: dict[str, t.Any]) -> None:
        """Tiêm các giá trị mặc định URL cho endpoint đã cho trực tiếp vào
        từ điển values được truyền. Điều này được sử dụng nội bộ và
        tự động được gọi khi xây dựng URL.

        .. versionadded:: 0.7
        """
        names: t.Iterable[str | None] = (None,)

        # url_for may be called outside a request context, parse the
        # passed endpoint instead of using request.blueprints.
        if "." in endpoint:
            names = chain(
                names, reversed(_split_blueprint_path(endpoint.rpartition(".")[0]))
            )

        for name in names:
            if name in self.url_default_functions:
                for func in self.url_default_functions[name]:
                    func(endpoint, values)

    def handle_url_build_error(
        self, error: BuildError, endpoint: str, values: dict[str, t.Any]
    ) -> str:
        """Được gọi bởi :meth:`.url_for` nếu một
        :exc:`~werkzeug.routing.BuildError` được ném ra. Nếu điều này trả về
        một giá trị, nó sẽ được trả về bởi ``url_for``, nếu không lỗi
        sẽ được ném lại.

        Mỗi hàm trong :attr:`url_build_error_handlers` được gọi với
        ``error``, ``endpoint`` và ``values``. Nếu một hàm trả về
        ``None`` hoặc ném ra một ``BuildError``, nó sẽ bị bỏ qua. Ngược lại,
        giá trị trả về của nó được trả về bởi ``url_for``.

        :param error: ``BuildError`` đang hoạt động đang được xử lý.
        :param endpoint: Endpoint đang được xây dựng.
        :param values: Các đối số từ khóa được truyền cho ``url_for``.
        """
        for handler in self.url_build_error_handlers:
            try:
                rv = handler(error, endpoint, values)
            except BuildError as e:
                # make error available outside except block
                error = e
            else:
                if rv is not None:
                    return rv

        # Re-raise if called with an active exception, otherwise raise
        # the passed in exception.
        if error is sys.exc_info()[1]:
            raise

        raise error
