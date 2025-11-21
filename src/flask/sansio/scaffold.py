from __future__ import annotations

import importlib.util
import os
import pathlib
import sys
import typing as t
from collections import defaultdict
from functools import update_wrapper

from jinja2 import BaseLoader
from jinja2 import FileSystemLoader
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from werkzeug.utils import cached_property

from .. import typing as ft
from ..helpers import get_root_path
from ..templating import _default_template_ctx_processor

if t.TYPE_CHECKING:  # pragma: no cover
    from click import Group

# một giá trị sentinel đơn lẻ cho các giá trị mặc định của tham số
_sentinel = object()

F = t.TypeVar("F", bound=t.Callable[..., t.Any])
T_after_request = t.TypeVar("T_after_request", bound=ft.AfterRequestCallable[t.Any])
T_before_request = t.TypeVar("T_before_request", bound=ft.BeforeRequestCallable)
T_error_handler = t.TypeVar("T_error_handler", bound=ft.ErrorHandlerCallable)
T_teardown = t.TypeVar("T_teardown", bound=ft.TeardownCallable)
T_template_context_processor = t.TypeVar(
    "T_template_context_processor", bound=ft.TemplateContextProcessorCallable
)
T_url_defaults = t.TypeVar("T_url_defaults", bound=ft.URLDefaultCallable)
T_url_value_preprocessor = t.TypeVar(
    "T_url_value_preprocessor", bound=ft.URLValuePreprocessorCallable
)
T_route = t.TypeVar("T_route", bound=ft.RouteCallable)


def setupmethod(f: F) -> F:
    f_name = f.__name__

    def wrapper_func(self: Scaffold, *args: t.Any, **kwargs: t.Any) -> t.Any:
        self._check_setup_finished(f_name)
        return f(self, *args, **kwargs)

    return t.cast(F, update_wrapper(wrapper_func, f))


class Scaffold:
    """Hành vi chung được chia sẻ giữa :class:`~flask.Flask` và
    :class:`~flask.blueprints.Blueprint`.

    :param import_name: Tên import của module nơi đối tượng này
        được định nghĩa. Thường thì :attr:`__name__` nên được sử dụng.
    :param static_folder: Đường dẫn đến một thư mục chứa các tệp tĩnh để phục vụ.
        Nếu điều này được thiết lập, một route tĩnh sẽ được thêm vào.
    :param static_url_path: Tiền tố URL cho route tĩnh.
    :param template_folder: Đường dẫn đến một thư mục chứa các tệp template.
        để render. Nếu điều này được thiết lập, một Jinja loader sẽ được thêm vào.
    :param root_path: Đường dẫn mà các tệp tĩnh, template và tài nguyên
        tương đối với nó. Thường không được thiết lập, nó được phát hiện dựa trên
        ``import_name``.

    .. versionadded:: 2.0
    """

    cli: Group
    name: str
    _static_folder: str | None = None
    _static_url_path: str | None = None

    def __init__(
        self,
        import_name: str,
        static_folder: str | os.PathLike[str] | None = None,
        static_url_path: str | None = None,
        template_folder: str | os.PathLike[str] | None = None,
        root_path: str | None = None,
    ):
        #: Tên của package hoặc module mà đối tượng này thuộc về.
        #: Đừng thay đổi điều này khi nó đã được thiết lập bởi constructor.
        self.import_name = import_name

        self.static_folder = static_folder
        self.static_url_path = static_url_path

        #: Đường dẫn đến thư mục templates, tương đối với
        #: :attr:`root_path`, để thêm vào template loader. ``None`` nếu
        #: template không nên được thêm vào.
        self.template_folder = template_folder

        if root_path is None:
            root_path = get_root_path(self.import_name)

        #: Đường dẫn tuyệt đối đến package trên hệ thống tệp. Được sử dụng để tìm
        #: kiếm các tài nguyên chứa trong package.
        self.root_path = root_path

        #: Một từ điển ánh xạ tên endpoint đến các hàm view.
        #:
        #: Để đăng ký một hàm view, sử dụng decorator :meth:`route`.
        #:
        #: Cấu trúc dữ liệu này là nội bộ. Nó không nên được sửa đổi
        #: trực tiếp và định dạng của nó có thể thay đổi bất cứ lúc nào.
        self.view_functions: dict[str, ft.RouteCallable] = {}

        #: Một cấu trúc dữ liệu của các trình xử lý lỗi đã đăng ký, theo định dạng
        #: ``{scope: {code: {class: handler}}}``. Khóa ``scope`` là
        #: tên của một blueprint mà các trình xử lý đang hoạt động, hoặc
        #: ``None`` cho tất cả các yêu cầu. Khóa ``code`` là mã trạng thái
        #: HTTP cho ``HTTPException``, hoặc ``None`` cho
        #: các ngoại lệ khác. Từ điển trong cùng ánh xạ các lớp ngoại lệ
        #: đến các hàm xử lý.
        #:
        #: Để đăng ký một trình xử lý lỗi, sử dụng decorator :meth:`errorhandler`.
        #:
        #: Cấu trúc dữ liệu này là nội bộ. Nó không nên được sửa đổi
        #: trực tiếp và định dạng của nó có thể thay đổi bất cứ lúc nào.
        self.error_handler_spec: dict[
            ft.AppOrBlueprintKey,
            dict[int | None, dict[type[Exception], ft.ErrorHandlerCallable]],
        ] = defaultdict(lambda: defaultdict(dict))

        #: Một cấu trúc dữ liệu của các hàm để gọi khi bắt đầu
        #: mỗi yêu cầu, theo định dạng ``{scope: [functions]}``. Khóa
        #: ``scope`` là tên của một blueprint mà các hàm đang
        #: hoạt động, hoặc ``None`` cho tất cả các yêu cầu.
        #:
        #: Để đăng ký một hàm, sử dụng decorator :meth:`before_request`.
        #:
        #: Cấu trúc dữ liệu này là nội bộ. Nó không nên được sửa đổi
        #: trực tiếp và định dạng của nó có thể thay đổi bất cứ lúc nào.
        self.before_request_funcs: dict[
            ft.AppOrBlueprintKey, list[ft.BeforeRequestCallable]
        ] = defaultdict(list)

        #: Một cấu trúc dữ liệu của các hàm để gọi khi kết thúc mỗi
        #: yêu cầu, theo định dạng ``{scope: [functions]}``. Khóa
        #: ``scope`` là tên của một blueprint mà các hàm đang
        #: hoạt động, hoặc ``None`` cho tất cả các yêu cầu.
        #:
        #: Để đăng ký một hàm, sử dụng decorator :meth:`after_request`.
        #:
        #: Cấu trúc dữ liệu này là nội bộ. Nó không nên được sửa đổi
        #: trực tiếp và định dạng của nó có thể thay đổi bất cứ lúc nào.
        self.after_request_funcs: dict[
            ft.AppOrBlueprintKey, list[ft.AfterRequestCallable[t.Any]]
        ] = defaultdict(list)

        #: Một cấu trúc dữ liệu của các hàm để gọi khi kết thúc mỗi
        #: yêu cầu ngay cả khi một ngoại lệ được đưa ra, theo định dạng
        #: ``{scope: [functions]}``. Khóa ``scope`` là tên của một
        #: blueprint mà các hàm đang hoạt động, hoặc ``None`` cho tất cả
        #: các yêu cầu.
        #:
        #: Để đăng ký một hàm, sử dụng decorator :meth:`teardown_request`.
        #:
        #: Cấu trúc dữ liệu này là nội bộ. Nó không nên được sửa đổi
        #: trực tiếp và định dạng của nó có thể thay đổi bất cứ lúc nào.
        self.teardown_request_funcs: dict[
            ft.AppOrBlueprintKey, list[ft.TeardownCallable]
        ] = defaultdict(list)

        #: Một cấu trúc dữ liệu của các hàm để gọi nhằm truyền thêm các giá trị
        #: ngữ cảnh khi render template, theo định dạng
        #: ``{scope: [functions]}``. Khóa ``scope`` là tên của một
        #: blueprint mà các hàm đang hoạt động, hoặc ``None`` cho tất cả
        #: các yêu cầu.
        #:
        #: Để đăng ký một hàm, sử dụng decorator :meth:`context_processor`.
        #:
        #: Cấu trúc dữ liệu này là nội bộ. Nó không nên được sửa đổi
        #: trực tiếp và định dạng của nó có thể thay đổi bất cứ lúc nào.
        self.template_context_processors: dict[
            ft.AppOrBlueprintKey, list[ft.TemplateContextProcessorCallable]
        ] = defaultdict(list, {None: [_default_template_ctx_processor]})

        #: Một cấu trúc dữ liệu của các hàm để gọi nhằm sửa đổi các đối số
        #: từ khóa được truyền cho hàm view, theo định dạng
        #: ``{scope: [functions]}``. Khóa ``scope`` là tên của một
        #: blueprint mà các hàm đang hoạt động, hoặc ``None`` cho tất cả
        #: các yêu cầu.
        #:
        #: Để đăng ký một hàm, sử dụng decorator
        #: :meth:`url_value_preprocessor`.
        #:
        #: Cấu trúc dữ liệu này là nội bộ. Nó không nên được sửa đổi
        #: trực tiếp và định dạng của nó có thể thay đổi bất cứ lúc nào.
        self.url_value_preprocessors: dict[
            ft.AppOrBlueprintKey,
            list[ft.URLValuePreprocessorCallable],
        ] = defaultdict(list)

        #: Một cấu trúc dữ liệu của các hàm để gọi nhằm sửa đổi các đối số
        #: từ khóa khi tạo URL, theo định dạng
        #: ``{scope: [functions]}``. Khóa ``scope`` là tên của một
        #: blueprint mà các hàm đang hoạt động, hoặc ``None`` cho tất cả
        #: các yêu cầu.
        #:
        #: Để đăng ký một hàm, sử dụng decorator :meth:`url_defaults`.
        #:
        #: Cấu trúc dữ liệu này là nội bộ. Nó không nên được sửa đổi
        #: trực tiếp và định dạng của nó có thể thay đổi bất cứ lúc nào.
        self.url_default_functions: dict[
            ft.AppOrBlueprintKey, list[ft.URLDefaultCallable]
        ] = defaultdict(list)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name!r}>"

    def _check_setup_finished(self, f_name: str) -> None:
        raise NotImplementedError

    @property
    def static_folder(self) -> str | None:
        """Đường dẫn tuyệt đối đến thư mục tĩnh đã được cấu hình. ``None``
        nếu không có thư mục tĩnh nào được thiết lập.
        """
        if self._static_folder is not None:
            return os.path.join(self.root_path, self._static_folder)
        else:
            return None

    @static_folder.setter
    def static_folder(self, value: str | os.PathLike[str] | None) -> None:
        if value is not None:
            value = os.fspath(value).rstrip(r"\/")

        self._static_folder = value

    @property
    def has_static_folder(self) -> bool:
        """``True`` nếu :attr:`static_folder` được thiết lập.

        .. versionadded:: 0.5
        """
        return self.static_folder is not None

    @property
    def static_url_path(self) -> str | None:
        """Tiền tố URL mà route tĩnh sẽ có thể truy cập được từ đó.

        Nếu nó không được cấu hình trong quá trình init, nó được suy ra từ
        :attr:`static_folder`.
        """
        if self._static_url_path is not None:
            return self._static_url_path

        if self.static_folder is not None:
            basename = os.path.basename(self.static_folder)
            return f"/{basename}".rstrip("/")

        return None

    @static_url_path.setter
    def static_url_path(self, value: str | None) -> None:
        if value is not None:
            value = value.rstrip("/")

        self._static_url_path = value

    @cached_property
    def jinja_loader(self) -> BaseLoader | None:
        """Jinja loader cho các template của đối tượng này. Theo mặc định, đây
        là một lớp :class:`jinja2.loaders.FileSystemLoader` đến
        :attr:`template_folder` nếu nó được thiết lập.

        .. versionadded:: 0.5
        """
        if self.template_folder is not None:
            return FileSystemLoader(os.path.join(self.root_path, self.template_folder))
        else:
            return None

    def _method_route(
        self,
        method: str,
        rule: str,
        options: dict[str, t.Any],
    ) -> t.Callable[[T_route], T_route]:
        if "methods" in options:
            raise TypeError("Use the 'route' decorator to use the 'methods' argument.")

        return self.route(rule, methods=[method], **options)

    @setupmethod
    def get(self, rule: str, **options: t.Any) -> t.Callable[[T_route], T_route]:
        """Lối tắt cho :meth:`route` với ``methods=["GET"]``.

        .. versionadded:: 2.0
        """
        return self._method_route("GET", rule, options)

    @setupmethod
    def post(self, rule: str, **options: t.Any) -> t.Callable[[T_route], T_route]:
        """Lối tắt cho :meth:`route` với ``methods=["POST"]``.

        .. versionadded:: 2.0
        """
        return self._method_route("POST", rule, options)

    @setupmethod
    def put(self, rule: str, **options: t.Any) -> t.Callable[[T_route], T_route]:
        """Lối tắt cho :meth:`route` với ``methods=["PUT"]``.

        .. versionadded:: 2.0
        """
        return self._method_route("PUT", rule, options)

    @setupmethod
    def delete(self, rule: str, **options: t.Any) -> t.Callable[[T_route], T_route]:
        """Lối tắt cho :meth:`route` với ``methods=["DELETE"]``.

        .. versionadded:: 2.0
        """
        return self._method_route("DELETE", rule, options)

    @setupmethod
    def patch(self, rule: str, **options: t.Any) -> t.Callable[[T_route], T_route]:
        """Lối tắt cho :meth:`route` với ``methods=["PATCH"]``.

        .. versionadded:: 2.0
        """
        return self._method_route("PATCH", rule, options)

    @setupmethod
    def route(self, rule: str, **options: t.Any) -> t.Callable[[T_route], T_route]:
        """Trang trí một hàm view để đăng ký nó với quy tắc URL và tùy chọn
        đã cho. Gọi :meth:`add_url_rule`, có nhiều chi tiết hơn về việc
        triển khai.

        .. code-block:: python

            @app.route("/")
            def index():
                return "Hello, World!"

        Xem :ref:`url-route-registrations`.

        Tên endpoint cho route mặc định là tên của hàm view nếu tham số
        ``endpoint`` không được truyền.

        Tham số ``methods`` mặc định là ``["GET"]``. ``HEAD`` và
        ``OPTIONS`` được thêm tự động.

        :param rule: Chuỗi quy tắc URL.
        :param options: Các tùy chọn bổ sung được truyền cho đối tượng
            :class:`~werkzeug.routing.Rule`.
        """

        def decorator(f: T_route) -> T_route:
            endpoint = options.pop("endpoint", None)
            self.add_url_rule(rule, endpoint, f, **options)
            return f

        return decorator

    @setupmethod
    def add_url_rule(
        self,
        rule: str,
        endpoint: str | None = None,
        view_func: ft.RouteCallable | None = None,
        provide_automatic_options: bool | None = None,
        **options: t.Any,
    ) -> None:
        """Đăng ký một quy tắc để định tuyến các yêu cầu đến và xây dựng
        URL. Decorator :meth:`route` là một lối tắt để gọi điều này
        với đối số ``view_func``. Những điều này là tương đương:

        .. code-block:: python

            @app.route("/")
            def index():
                ...

        .. code-block:: python

            def index():
                ...

            app.add_url_rule("/", view_func=index)

        Xem :ref:`url-route-registrations`.

        Tên endpoint cho route mặc định là tên của hàm view nếu tham số
        ``endpoint`` không được truyền. Một lỗi sẽ được đưa ra nếu một hàm
        đã được đăng ký cho endpoint.

        Tham số ``methods`` mặc định là ``["GET"]``. ``HEAD`` luôn được
        thêm tự động, và ``OPTIONS`` được thêm tự động theo mặc định.

        ``view_func`` không nhất thiết phải được truyền, nhưng nếu quy tắc
        nên tham gia vào việc định tuyến, tên endpoint phải được liên kết
        với một hàm view tại một thời điểm nào đó với decorator
        :meth:`endpoint`.

        .. code-block:: python

            app.add_url_rule("/", endpoint="index")

            @app.endpoint("index")
            def index():
                ...

        Nếu ``view_func`` có thuộc tính ``required_methods``, những phương thức
        đó sẽ được thêm vào các phương thức được truyền và tự động. Nếu nó
        có thuộc tính ``provide_automatic_methods``, nó được sử dụng làm
        mặc định nếu tham số không được truyền.

        :param rule: Chuỗi quy tắc URL.
        :param endpoint: Tên endpoint để liên kết với quy tắc và hàm view.
            Được sử dụng khi định tuyến và xây dựng URL. Mặc định là
            ``view_func.__name__``.
        :param view_func: Hàm view để liên kết với tên endpoint.
        :param provide_automatic_options: Thêm phương thức ``OPTIONS`` và
            phản hồi các yêu cầu ``OPTIONS`` tự động.
        :param options: Các tùy chọn bổ sung được truyền cho đối tượng
            :class:`~werkzeug.routing.Rule`.
        """
        raise NotImplementedError

    @setupmethod
    def endpoint(self, endpoint: str) -> t.Callable[[F], F]:
        """Trang trí một hàm view để đăng ký nó cho endpoint đã cho.
        Được sử dụng nếu một quy tắc được thêm vào mà không có ``view_func`` với
        :meth:`add_url_rule`.

        .. code-block:: python

            app.add_url_rule("/ex", endpoint="example")

            @app.endpoint("example")
            def example():
                ...

        :param endpoint: Tên endpoint để liên kết với hàm view.
        """

        def decorator(f: F) -> F:
            self.view_functions[endpoint] = f
            return f

        return decorator

    @setupmethod
    def before_request(self, f: T_before_request) -> T_before_request:
        """Đăng ký một hàm để chạy trước mỗi yêu cầu.

        Ví dụ, điều này có thể được sử dụng để mở kết nối cơ sở dữ liệu, hoặc
        để tải người dùng đã đăng nhập từ session.

        .. code-block:: python

            @app.before_request
            def load_user():
                if "user_id" in session:
                    g.user = db.session.get(session["user_id"])

        Hàm sẽ được gọi mà không có bất kỳ đối số nào. Nếu nó trả về
        một giá trị không phải là ``None``, giá trị đó được xử lý như thể nó là
        giá trị trả về từ view, và việc xử lý yêu cầu tiếp theo bị dừng lại.

        Điều này có sẵn trên cả đối tượng app và blueprint. Khi được sử dụng trên một app, điều này
        thực thi trước mỗi yêu cầu. Khi được sử dụng trên một blueprint, điều này thực thi trước
        mỗi yêu cầu mà blueprint xử lý. Để đăng ký với một blueprint và
        thực thi trước mỗi yêu cầu, sử dụng :meth:`.Blueprint.before_app_request`.
        """
        self.before_request_funcs.setdefault(None, []).append(f)
        return f

    @setupmethod
    def after_request(self, f: T_after_request) -> T_after_request:
        """Đăng ký một hàm để chạy sau mỗi yêu cầu tới đối tượng này.

        Hàm được gọi với đối tượng phản hồi, và phải trả về
        một đối tượng phản hồi. Điều này cho phép các hàm sửa đổi hoặc
        thay thế phản hồi trước khi nó được gửi đi.

        Nếu một hàm đưa ra một ngoại lệ, bất kỳ hàm ``after_request``
        còn lại nào sẽ không được gọi. Do đó, điều này không nên được sử dụng
        cho các hành động bắt buộc phải thực thi, chẳng hạn như để đóng tài nguyên.
        Sử dụng :meth:`teardown_request` cho việc đó.

        Điều này có sẵn trên cả đối tượng app và blueprint. Khi được sử dụng trên một app, điều này
        thực thi sau mỗi yêu cầu. Khi được sử dụng trên một blueprint, điều này thực thi sau
        mỗi yêu cầu mà blueprint xử lý. Để đăng ký với một blueprint và
        thực thi sau mỗi yêu cầu, sử dụng :meth:`.Blueprint.after_app_request`.
        """
        self.after_request_funcs.setdefault(None, []).append(f)
        return f

    @setupmethod
    def teardown_request(self, f: T_teardown) -> T_teardown:
        """Đăng ký một hàm để được gọi khi ngữ cảnh yêu cầu bị pop.
        Thường thì, điều này xảy ra ở cuối mỗi yêu cầu, nhưng
        các ngữ cảnh có thể được push thủ công trong quá trình kiểm thử.

        .. code-block:: python

            with app.test_request_context():
                ...

        Khi khối ``with`` thoát (hoặc ``ctx.pop()`` được gọi), các hàm
        teardown được gọi ngay trước khi ngữ cảnh yêu cầu trở nên không hoạt động.

        Khi một hàm teardown được gọi vì một ngoại lệ không được xử lý,
        nó sẽ được truyền một đối tượng lỗi. Nếu một :meth:`errorhandler`
        được đăng ký, nó sẽ xử lý ngoại lệ và teardown sẽ không nhận được nó.

        Các hàm teardown phải tránh đưa ra các ngoại lệ. Nếu chúng
        thực thi mã có thể thất bại, chúng phải bao quanh mã đó bằng một
        khối ``try``/``except`` và ghi lại bất kỳ lỗi nào.

        Các giá trị trả về của các hàm teardown bị bỏ qua.

        Điều này có sẵn trên cả đối tượng app và blueprint. Khi được sử dụng trên một app, điều này
        thực thi sau mỗi yêu cầu. Khi được sử dụng trên một blueprint, điều này thực thi sau
        mỗi yêu cầu mà blueprint xử lý. Để đăng ký với một blueprint và
        thực thi sau mỗi yêu cầu, sử dụng :meth:`.Blueprint.teardown_app_request`.
        """
        self.teardown_request_funcs.setdefault(None, []).append(f)
        return f

    @setupmethod
    def context_processor(
        self,
        f: T_template_context_processor,
    ) -> T_template_context_processor:
        """Đăng ký một hàm xử lý ngữ cảnh template. Các hàm này chạy trước khi
        render một template. Các khóa của dict trả về được thêm vào như các biến
        có sẵn trong template.

        Điều này có sẵn trên cả đối tượng app và blueprint. Khi được sử dụng trên một app, điều này
        được gọi cho mỗi template được render. Khi được sử dụng trên một blueprint, điều này được gọi
        cho các template được render từ các view của blueprint. Để đăng ký với một blueprint
        và ảnh hưởng đến mọi template, sử dụng :meth:`.Blueprint.app_context_processor`.
        """
        self.template_context_processors[None].append(f)
        return f

    @setupmethod
    def url_value_preprocessor(
        self,
        f: T_url_value_preprocessor,
    ) -> T_url_value_preprocessor:
        """Đăng ký một hàm tiền xử lý giá trị URL cho tất cả các hàm view
        trong ứng dụng. Các hàm này sẽ được gọi trước các hàm
        :meth:`before_request`.

        Hàm có thể sửa đổi các giá trị được bắt từ url khớp trước khi
        chúng được truyền cho view. Ví dụ, điều này có thể được sử dụng để pop một
        giá trị mã ngôn ngữ chung và đặt nó vào ``g`` thay vì truyền nó cho
        mọi view.

        Hàm được truyền tên endpoint và dict các giá trị. Giá trị trả về
        bị bỏ qua.

        Điều này có sẵn trên cả đối tượng app và blueprint. Khi được sử dụng trên một app, điều này
        được gọi cho mỗi yêu cầu. Khi được sử dụng trên một blueprint, điều này được gọi cho
        các yêu cầu mà blueprint xử lý. Để đăng ký với một blueprint và ảnh hưởng đến
        mọi yêu cầu, sử dụng :meth:`.Blueprint.app_url_value_preprocessor`.
        """
        self.url_value_preprocessors[None].append(f)
        return f

    @setupmethod
    def url_defaults(self, f: T_url_defaults) -> T_url_defaults:
        """Hàm callback cho các giá trị mặc định URL cho tất cả các hàm view của
        ứng dụng. Nó được gọi với endpoint và các giá trị và nên
        cập nhật các giá trị được truyền tại chỗ.

        Điều này có sẵn trên cả đối tượng app và blueprint. Khi được sử dụng trên một app, điều này
        được gọi cho mỗi yêu cầu. Khi được sử dụng trên một blueprint, điều này được gọi cho
        các yêu cầu mà blueprint xử lý. Để đăng ký với một blueprint và ảnh hưởng đến
        mọi yêu cầu, sử dụng :meth:`.Blueprint.app_url_defaults`.
        """
        self.url_default_functions[None].append(f)
        return f

    @setupmethod
    def errorhandler(
        self, code_or_exception: type[Exception] | int
    ) -> t.Callable[[T_error_handler], T_error_handler]:
        """Đăng ký một hàm để xử lý lỗi theo mã hoặc lớp ngoại lệ.

        Một decorator được sử dụng để đăng ký một hàm với một
        mã lỗi đã cho. Ví dụ::

            @app.errorhandler(404)
            def page_not_found(error):
                return 'This page does not exist', 404

        Bạn cũng có thể đăng ký các trình xử lý cho các ngoại lệ tùy ý::

            @app.errorhandler(DatabaseError)
            def special_exception_handler(error):
                return 'Database connection failed', 500

        Điều này có sẵn trên cả đối tượng app và blueprint. Khi được sử dụng trên một app, điều này
        có thể xử lý lỗi từ mọi yêu cầu. Khi được sử dụng trên một blueprint, điều này có thể xử lý
        lỗi từ các yêu cầu mà blueprint xử lý. Để đăng ký với một blueprint
        và ảnh hưởng đến mọi yêu cầu, sử dụng :meth:`.Blueprint.app_errorhandler`.

        .. versionadded:: 0.7
            Sử dụng :meth:`register_error_handler` thay vì sửa đổi
            :attr:`error_handler_spec` trực tiếp, cho các trình xử lý lỗi toàn ứng dụng.

        .. versionadded:: 0.7
           Người ta cũng có thể đăng ký thêm các loại ngoại lệ tùy chỉnh
           không nhất thiết phải là lớp con của lớp
           :class:`~werkzeug.exceptions.HTTPException`.

        :param code_or_exception: mã dưới dạng số nguyên cho trình xử lý, hoặc
                                  một ngoại lệ tùy ý
        """

        def decorator(f: T_error_handler) -> T_error_handler:
            self.register_error_handler(code_or_exception, f)
            return f

        return decorator

    @setupmethod
    def register_error_handler(
        self,
        code_or_exception: type[Exception] | int,
        f: ft.ErrorHandlerCallable,
    ) -> None:
        """Hàm đính kèm lỗi thay thế cho decorator :meth:`errorhandler`
        dễ sử dụng hơn cho việc sử dụng không phải decorator.

        .. versionadded:: 0.7
        """
        exc_class, code = self._get_exc_class_and_code(code_or_exception)
        self.error_handler_spec[None][code][exc_class] = f

    @staticmethod
    def _get_exc_class_and_code(
        exc_class_or_code: type[Exception] | int,
    ) -> tuple[type[Exception], int | None]:
        """Lấy lớp ngoại lệ đang được xử lý. Đối với các mã trạng thái HTTP
        hoặc các lớp con ``HTTPException``, trả về cả ngoại lệ và
        mã trạng thái.

        :param exc_class_or_code: Bất kỳ lớp ngoại lệ nào, hoặc một mã trạng thái HTTP
            dưới dạng số nguyên.
        """
        exc_class: type[Exception]

        if isinstance(exc_class_or_code, int):
            try:
                exc_class = default_exceptions[exc_class_or_code]
            except KeyError:
                raise ValueError(
                    f"'{exc_class_or_code}' is not a recognized HTTP"
                    " error code. Use a subclass of HTTPException with"
                    " that code instead."
                ) from None
        else:
            exc_class = exc_class_or_code

        if isinstance(exc_class, Exception):
            raise TypeError(
                f"{exc_class!r} is an instance, not a class. Handlers"
                " can only be registered for Exception classes or HTTP"
                " error codes."
            )

        if not issubclass(exc_class, Exception):
            raise ValueError(
                f"'{exc_class.__name__}' is not a subclass of Exception."
                " Handlers can only be registered for Exception classes"
                " or HTTP error codes."
            )

        if issubclass(exc_class, HTTPException):
            return exc_class, exc_class.code
        else:
            return exc_class, None


def _endpoint_from_view_func(view_func: ft.RouteCallable) -> str:
    """Trình trợ giúp nội bộ trả về endpoint mặc định cho một hàm
    đã cho. Điều này luôn là tên hàm.
    """
    assert view_func is not None, "expected view func if endpoint is not provided."
    return view_func.__name__


def _find_package_path(import_name: str) -> str:
    """Tìm đường dẫn chứa package hoặc module."""
    root_mod_name, _, _ = import_name.partition(".")

    try:
        root_spec = importlib.util.find_spec(root_mod_name)

        if root_spec is None:
            raise ValueError("not found")
    except (ImportError, ValueError):
        # ImportError: the machinery told us it does not exist
        # ValueError:
        #    - the module name was invalid
        #    - the module name is __main__
        #    - we raised `ValueError` due to `root_spec` being `None`
        return os.getcwd()

    if root_spec.submodule_search_locations:
        if root_spec.origin is None or root_spec.origin == "namespace":
            # namespace package
            package_spec = importlib.util.find_spec(import_name)

            if package_spec is not None and package_spec.submodule_search_locations:
                # Pick the path in the namespace that contains the submodule.
                package_path = pathlib.Path(
                    os.path.commonpath(package_spec.submodule_search_locations)
                )
                search_location = next(
                    location
                    for location in root_spec.submodule_search_locations
                    if package_path.is_relative_to(location)
                )
            else:
                # Pick the first path.
                search_location = root_spec.submodule_search_locations[0]

            return os.path.dirname(search_location)
        else:
            # package with __init__.py
            return os.path.dirname(os.path.dirname(root_spec.origin))
    else:
        # module
        return os.path.dirname(root_spec.origin)  # type: ignore[type-var, return-value]


def find_package(import_name: str) -> tuple[str | None, str]:
    """Tìm tiền tố mà một package được cài đặt dưới đó, và đường dẫn
    mà nó sẽ được import từ đó.

    Tiền tố là thư mục chứa phân cấp thư mục tiêu chuẩn
    (lib, bin, v.v.). Nếu package không được cài đặt vào
    hệ thống (:attr:`sys.prefix`) hoặc một virtualenv (``site-packages``),
    ``None`` được trả về.

    Đường dẫn là mục nhập trong :attr:`sys.path` chứa package
    để import. Nếu package không được cài đặt, giả định rằng
    package đã được import từ thư mục làm việc hiện tại.
    """
    package_path = _find_package_path(import_name)
    py_prefix = os.path.abspath(sys.prefix)

    # installed to the system
    if pathlib.PurePath(package_path).is_relative_to(py_prefix):
        return py_prefix, package_path

    site_parent, site_folder = os.path.split(package_path)

    # installed to a virtualenv
    if site_folder.lower() == "site-packages":
        parent, folder = os.path.split(site_parent)

        # Windows (prefix/lib/site-packages)
        if folder.lower() == "lib":
            return parent, package_path

        # Unix (prefix/lib/pythonX.Y/site-packages)
        if os.path.basename(parent).lower() == "lib":
            return os.path.dirname(parent), package_path

        # something else (prefix/site-packages)
        return site_parent, package_path

    # not installed
    return None, package_path
