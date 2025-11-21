from __future__ import annotations

import ast
import collections.abc as cabc
import importlib.metadata
import inspect
import os
import platform
import re
import sys
import traceback
import typing as t
from functools import update_wrapper
from operator import itemgetter
from types import ModuleType

import click
from click.core import ParameterSource
from werkzeug import run_simple
from werkzeug.serving import is_running_from_reloader
from werkzeug.utils import import_string

from .globals import current_app
from .helpers import get_debug_flag
from .helpers import get_load_dotenv

if t.TYPE_CHECKING:
    import ssl

    from _typeshed.wsgi import StartResponse
    from _typeshed.wsgi import WSGIApplication
    from _typeshed.wsgi import WSGIEnvironment

    from .app import Flask


class NoAppException(click.UsageError):
    """Được ném ra nếu không tìm thấy hoặc không thể tải ứng dụng."""


def find_best_app(module: ModuleType) -> Flask:
    """Với một thể hiện module, điều này cố gắng tìm ứng dụng tốt nhất có thể
    trong module hoặc ném ra một ngoại lệ.
    """
    from . import Flask

    # Tìm kiếm các tên phổ biến nhất trước.
    for attr_name in ("app", "application"):
        app = getattr(module, attr_name, None)

        if isinstance(app, Flask):
            return app

    # Nếu không, tìm đối tượng duy nhất là một thể hiện Flask.
    matches = [v for v in module.__dict__.values() if isinstance(v, Flask)]

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        raise NoAppException(
            "Đã phát hiện nhiều ứng dụng Flask trong module"
            f" '{module.__name__}'. Sử dụng '{module.__name__}:name'"
            " để chỉ định đúng ứng dụng."
        )

    # Tìm kiếm các hàm factory ứng dụng.
    for attr_name in ("create_app", "make_app"):
        app_factory = getattr(module, attr_name, None)

        if inspect.isfunction(app_factory):
            try:
                app = app_factory()

                if isinstance(app, Flask):
                    return app
            except TypeError as e:
                if not _called_with_wrong_args(app_factory):
                    raise

                raise NoAppException(
                    f"Đã phát hiện factory '{attr_name}' trong module '{module.__name__}',"
                    " nhưng không thể gọi nó mà không có đối số. Sử dụng"
                    f" '{module.__name__}:{attr_name}(args)'"
                    " để chỉ định các đối số."
                ) from e

    raise NoAppException(
        "Không tìm thấy ứng dụng Flask hoặc factory trong module"
        f" '{module.__name__}'. Sử dụng '{module.__name__}:name'"
        " để chỉ định một cái."
    )


def _called_with_wrong_args(f: t.Callable[..., Flask]) -> bool:
    """Kiểm tra xem việc gọi một hàm có ném ra ``TypeError`` hay không vì
    cuộc gọi thất bại hoặc vì một cái gì đó trong factory đã ném ra
    lỗi.

    :param f: Hàm đã được gọi.
    :return: ``True`` nếu cuộc gọi thất bại.
    """
    tb = sys.exc_info()[2]

    try:
        while tb is not None:
            if tb.tb_frame.f_code is f.__code__:
                # Trong hàm, nó đã được gọi thành công.
                return False

            tb = tb.tb_next

        # Không đến được hàm.
        return True
    finally:
        # Xóa tb để phá vỡ tham chiếu vòng.
        # https://docs.python.org/2/library/sys.html#sys.exc_info
        del tb


def find_app_by_string(module: ModuleType, app_name: str) -> Flask:
    """Kiểm tra xem chuỗi đã cho có phải là tên biến hoặc hàm không. Gọi
    một hàm để lấy thể hiện ứng dụng, hoặc trả về biến trực tiếp.
    """
    from . import Flask

    # Phân tích app_name như một biểu thức đơn để xác định xem nó có phải là một
    # tên thuộc tính hoặc lời gọi hàm hợp lệ không.
    try:
        expr = ast.parse(app_name.strip(), mode="eval").body
    except SyntaxError:
        raise NoAppException(
            f"Không thể phân tích {app_name!r} như một tên thuộc tính hoặc lời gọi hàm."
        ) from None

    if isinstance(expr, ast.Name):
        name = expr.id
        args = []
        kwargs = {}
    elif isinstance(expr, ast.Call):
        # Đảm bảo tên hàm chỉ là một tên thuộc tính.
        if not isinstance(expr.func, ast.Name):
            raise NoAppException(
                f"Tham chiếu hàm phải là một tên đơn giản: {app_name!r}."
            )

        name = expr.func.id

        # Phân tích các đối số vị trí và từ khóa dưới dạng literal.
        try:
            args = [ast.literal_eval(arg) for arg in expr.args]
            kwargs = {
                kw.arg: ast.literal_eval(kw.value)
                for kw in expr.keywords
                if kw.arg is not None
            }
        except ValueError:
            # literal_eval đưa ra thông báo lỗi khó hiểu, hiển thị một thông báo chung
            # với biểu thức đầy đủ thay thế.
            raise NoAppException(
                f"Không thể phân tích các đối số dưới dạng giá trị literal: {app_name!r}."
            ) from None
    else:
        raise NoAppException(
            f"Failed to parse {app_name!r} as an attribute name or function call."
        )

    try:
        attr = getattr(module, name)
    except AttributeError as e:
        raise NoAppException(
            f"Không thể tìm thấy thuộc tính {name!r} trong {module.__name__!r}."
        ) from e

    # Nếu thuộc tính là một hàm, gọi nó với bất kỳ args và kwargs nào
    # để lấy ứng dụng thực sự.
    if inspect.isfunction(attr):
        try:
            app = attr(*args, **kwargs)
        except TypeError as e:
            if not _called_with_wrong_args(attr):
                raise

            raise NoAppException(
                f"Factory {app_name!r} trong module"
                f" {module.__name__!r} không thể được gọi với các"
                " đối số đã chỉ định."
            ) from e
    else:
        app = attr

    if isinstance(app, Flask):
        return app

    raise NoAppException(
        "Một ứng dụng Flask hợp lệ không được lấy từ"
        f" '{module.__name__}:{app_name}'."
    )


def prepare_import(path: str) -> str:
    """Với một tên tệp, điều này sẽ cố gắng tính toán đường dẫn python, thêm nó
    vào đường dẫn tìm kiếm và trả về tên module thực tế được mong đợi.
    """
    path = os.path.realpath(path)

    fname, ext = os.path.splitext(path)
    if ext == ".py":
        path = fname

    if os.path.basename(path) == "__init__":
        path = os.path.dirname(path)

    module_name = []

    # di chuyển lên cho đến khi ra ngoài cấu trúc gói (không có __init__.py)
    while True:
        path, name = os.path.split(path)
        module_name.append(name)

        if not os.path.exists(os.path.join(path, "__init__.py")):
            break

    if sys.path[0] != path:
        sys.path.insert(0, path)

    return ".".join(module_name[::-1])


@t.overload
def locate_app(
    module_name: str, app_name: str | None, raise_if_not_found: t.Literal[True] = True
) -> Flask: ...


@t.overload
def locate_app(
    module_name: str, app_name: str | None, raise_if_not_found: t.Literal[False] = ...
) -> Flask | None: ...


def locate_app(
    module_name: str, app_name: str | None, raise_if_not_found: bool = True
) -> Flask | None:
    try:
        __import__(module_name)
    except ImportError:
        # Ném lại ImportError nếu nó xảy ra trong module được import.
        # Xác định điều này bằng cách kiểm tra xem trace có độ sâu > 1 hay không.
        if sys.exc_info()[2].tb_next:  # type: ignore[union-attr]
            raise NoAppException(
                f"Trong khi import {module_name!r}, một ImportError đã"
                f" được ném ra:\n\n{traceback.format_exc()}"
            ) from None
        elif raise_if_not_found:
            raise NoAppException(f"Không thể import {module_name!r}.") from None
        else:
            return None

    module = sys.modules[module_name]

    if app_name is None:
        return find_best_app(module)
    else:
        return find_app_by_string(module, app_name)


def get_version(ctx: click.Context, param: click.Parameter, value: t.Any) -> None:
    if not value or ctx.resilient_parsing:
        return

    flask_version = importlib.metadata.version("flask")
    werkzeug_version = importlib.metadata.version("werkzeug")

    click.echo(
        f"Python {platform.python_version()}\n"
        f"Flask {flask_version}\n"
        f"Werkzeug {werkzeug_version}",
        color=ctx.color,
    )
    ctx.exit()


version_option = click.Option(
    ["--version"],
    help="Hiển thị phiên bản Flask.",
    expose_value=False,
    callback=get_version,
    is_flag=True,
    is_eager=True,
)


class ScriptInfo:
    """Đối tượng trợ giúp để xử lý các ứng dụng Flask. Điều này thường không
    cần thiết để giao tiếp vì nó được sử dụng nội bộ trong việc điều phối
    đến click. Trong các phiên bản tương lai của Flask, đối tượng này rất có thể sẽ đóng
    vai trò lớn hơn. Thông thường nó được tạo tự động bởi
    :class:`FlaskGroup` nhưng bạn cũng có thể tạo thủ công và truyền nó
    tiếp theo như đối tượng click.

    .. versionchanged:: 3.1
        Đã thêm tham số và thuộc tính ``load_dotenv_defaults``.
    """

    def __init__(
        self,
        app_import_path: str | None = None,
        create_app: t.Callable[..., Flask] | None = None,
        set_debug_flag: bool = True,
        load_dotenv_defaults: bool = True,
    ) -> None:
        #: Tùy chọn đường dẫn import cho ứng dụng Flask.
        self.app_import_path = app_import_path
        #: Tùy chọn một hàm được truyền thông tin script để tạo
        #: thể hiện của ứng dụng.
        self.create_app = create_app
        #: Một từ điển với dữ liệu tùy ý có thể được liên kết với
        #: thông tin script này.
        self.data: dict[t.Any, t.Any] = {}
        self.set_debug_flag = set_debug_flag

        self.load_dotenv_defaults = get_load_dotenv(load_dotenv_defaults)
        """Liệu các tệp ``.flaskenv`` và ``.env`` mặc định có nên được tải hay không.

        ``ScriptInfo`` không tải bất cứ thứ gì, đây là để tham khảo khi thực hiện
        việc tải ở nơi khác trong quá trình xử lý.

        .. versionadded:: 3.1
        """

        self._loaded_app: Flask | None = None

    def load_app(self) -> Flask:
        """Tải ứng dụng Flask (nếu chưa được tải) và trả về nó. Gọi
        điều này nhiều lần sẽ chỉ dẫn đến ứng dụng đã tải
        được trả về.
        """
        if self._loaded_app is not None:
            return self._loaded_app
        app: Flask | None = None
        if self.create_app is not None:
            app = self.create_app()
        else:
            if self.app_import_path:
                path, name = (
                    re.split(r":(?![\\/])", self.app_import_path, maxsplit=1) + [None]
                )[:2]
                import_name = prepare_import(path)
                app = locate_app(import_name, name)
            else:
                for path in ("wsgi.py", "app.py"):
                    import_name = prepare_import(path)
                    app = locate_app(import_name, None, raise_if_not_found=False)

                    if app is not None:
                        break

        if app is None:
            raise NoAppException(
                "Không thể định vị ứng dụng Flask. Sử dụng tùy chọn"
                " 'flask --app', biến môi trường 'FLASK_APP'"
                ", hoặc tệp 'wsgi.py' hoặc 'app.py' trong"
                " thư mục hiện tại."
            )

        if self.set_debug_flag:
            # Cập nhật cờ debug của ứng dụng thông qua descriptor để
            # các giá trị khác cũng được điền lại.
            app.debug = get_debug_flag()

        self._loaded_app = app
        return app


pass_script_info = click.make_pass_decorator(ScriptInfo, ensure=True)

F = t.TypeVar("F", bound=t.Callable[..., t.Any])


def with_appcontext(f: F) -> F:
    """Bao bọc một callback để đảm bảo nó được thực thi với
    ngữ cảnh ứng dụng của script.

    Các lệnh tùy chỉnh (và các tùy chọn của chúng) được đăng ký dưới ``app.cli`` hoặc
    ``blueprint.cli`` sẽ luôn có sẵn ngữ cảnh ứng dụng, decorator này
    không bắt buộc trong trường hợp đó.

    .. versionchanged:: 2.2
        Ngữ cảnh ứng dụng hoạt động cho các lệnh con cũng như
        callback được trang trí. Ngữ cảnh ứng dụng luôn có sẵn cho
        các callback lệnh và tham số ``app.cli``.
    """

    @click.pass_context
    def decorator(ctx: click.Context, /, *args: t.Any, **kwargs: t.Any) -> t.Any:
        if not current_app:
            app = ctx.ensure_object(ScriptInfo).load_app()
            ctx.with_resource(app.app_context())

        return ctx.invoke(f, *args, **kwargs)

    return update_wrapper(decorator, f)  # type: ignore[return-value]


class AppGroup(click.Group):
    """Điều này hoạt động tương tự như một :class:`~click.Group` click thông thường nhưng nó
    thay đổi hành vi của decorator :meth:`command` để nó
    tự động bao bọc các hàm trong :func:`with_appcontext`.

    Không nhầm lẫn với :class:`FlaskGroup`.
    """

    def command(  # type: ignore[override]
        self, *args: t.Any, **kwargs: t.Any
    ) -> t.Callable[[t.Callable[..., t.Any]], click.Command]:
        """Điều này hoạt động chính xác như phương thức cùng tên trên một
        :class:`click.Group` thông thường nhưng nó bao bọc các callback trong :func:`with_appcontext`
        trừ khi nó bị vô hiệu hóa bằng cách truyền ``with_appcontext=False``.
        """
        wrap_for_ctx = kwargs.pop("with_appcontext", True)

        def decorator(f: t.Callable[..., t.Any]) -> click.Command:
            if wrap_for_ctx:
                f = with_appcontext(f)
            return super(AppGroup, self).command(*args, **kwargs)(f)  # type: ignore[no-any-return]

        return decorator

    def group(  # type: ignore[override]
        self, *args: t.Any, **kwargs: t.Any
    ) -> t.Callable[[t.Callable[..., t.Any]], click.Group]:
        """Điều này hoạt động chính xác như phương thức cùng tên trên một
        :class:`click.Group` thông thường nhưng nó mặc định lớp nhóm thành
        :class:`AppGroup`.
        """
        kwargs.setdefault("cls", AppGroup)
        return super().group(*args, **kwargs)  # type: ignore[no-any-return]


def _set_app(ctx: click.Context, param: click.Option, value: str | None) -> str | None:
    if value is None:
        return None

    info = ctx.ensure_object(ScriptInfo)
    info.app_import_path = value
    return value


# Tùy chọn này là eager để ứng dụng sẽ có sẵn nếu --help được đưa ra.
# --help cũng là eager, vì vậy --app phải ở trước nó trong danh sách param.
# no_args_is_help bỏ qua xử lý eager, vì vậy tùy chọn này phải được
# xử lý thủ công trong trường hợp đó để đảm bảo FLASK_APP được nhận. đó để đảm bảo FLASK_APP được nhận.
_app_option = click.Option(
    ["-A", "--app"],
    metavar="IMPORT",
    help=(
        "Ứng dụng Flask hoặc hàm factory để tải, dưới dạng 'module:name'."
        " Module có thể là một import có dấu chấm hoặc đường dẫn tệp. Name không bắt buộc nếu nó là"
        " 'app', 'application', 'create_app', hoặc 'make_app', và có thể là 'name(args)' để"
        " truyền đối số."
    ),
    is_eager=True,
    expose_value=False,
    callback=_set_app,
)


def _set_debug(ctx: click.Context, param: click.Option, value: bool) -> bool | None:
    # Nếu cờ không được cung cấp, nó sẽ mặc định là False. Đừng sử dụng
    # cái đó, hãy để debug được thiết lập bởi env trong trường hợp đó.
    source = ctx.get_parameter_source(param.name)  # type: ignore[arg-type]

    if source is not None and source in (
        ParameterSource.DEFAULT,
        ParameterSource.DEFAULT_MAP,
    ):
        return None

    # Thiết lập với biến môi trường thay vì ScriptInfo.load để nó có thể được
    # truy cập sớm trong quá trình hàm factory.
    os.environ["FLASK_DEBUG"] = "1" if value else "0"
    return value


_debug_option = click.Option(
    ["--debug/--no-debug"],
    help="Thiết lập chế độ debug.",
    expose_value=False,
    callback=_set_debug,
)


def _env_file_callback(
    ctx: click.Context, param: click.Option, value: str | None
) -> str | None:
    try:
        import dotenv  # noqa: F401
    except ImportError:
        # Chỉ hiển thị lỗi nếu một giá trị được truyền, nếu không chúng ta vẫn muốn
        # gọi load_dotenv và hiển thị thông báo mà không thoát.
        if value is not None:
            raise click.BadParameter(
                "python-dotenv phải được cài đặt để tải tệp env.",
                ctx=ctx,
                param=param,
            ) from None

    # Tải nếu một giá trị được truyền, hoặc chúng ta muốn tải các tệp mặc định, hoặc cả hai.
    if value is not None or ctx.obj.load_dotenv_defaults:
        load_dotenv(value, load_defaults=ctx.obj.load_dotenv_defaults)

    return value


# Tùy chọn này là eager để các biến môi trường được tải sớm nhất có thể để
# được sử dụng bởi các tùy chọn khác.
_env_file_option = click.Option(
    ["-e", "--env-file"],
    type=click.Path(exists=True, dir_okay=False),
    help=(
        "Tải các biến môi trường từ tệp này, ưu tiên hơn"
        " những cái được thiết lập bởi '.env' và '.flaskenv'. Các biến được thiết lập trực tiếp trong"
        " môi trường có quyền ưu tiên cao nhất. python-dotenv phải được cài đặt."
    ),
    is_eager=True,
    expose_value=False,
    callback=_env_file_callback,
)


class FlaskGroup(AppGroup):
    """Lớp con đặc biệt của nhóm :class:`AppGroup` hỗ trợ
    tải thêm các lệnh từ ứng dụng Flask đã cấu hình. Thông thường một
    nhà phát triển không phải giao tiếp với lớp này nhưng có
    một số trường hợp sử dụng rất nâng cao mà việc tạo một
    thể hiện của lớp này là hợp lý. xem :ref:`custom-scripts`.

    :param add_default_commands: nếu là True thì các lệnh run và
        shell mặc định sẽ được thêm vào.
    :param add_version_option: thêm tùy chọn ``--version``.
    :param create_app: một callback tùy chọn được truyền thông tin script và
        trả về ứng dụng đã tải.
    :param load_dotenv: Tải các tệp :file:`.env` và :file:`.flaskenv`
        gần nhất để thiết lập các biến môi trường. Cũng sẽ thay đổi thư mục
        làm việc sang thư mục chứa tệp đầu tiên được tìm thấy.
    :param set_debug_flag: Thiết lập cờ debug của ứng dụng.

    .. versionchanged:: 3.1
        ``-e path`` được ưu tiên hơn các tệp ``.env`` và ``.flaskenv`` mặc định.

    .. versionchanged:: 2.2
        Đã thêm các tùy chọn ``-A/--app``, ``--debug/--no-debug``, ``-e/--env-file``.

    .. versionchanged:: 2.2
        Một ngữ cảnh ứng dụng được push khi chạy các lệnh ``app.cli``, vì vậy
        ``@with_appcontext`` không còn bắt buộc cho các lệnh đó.

    .. versionchanged:: 1.0
        Nếu được cài đặt, python-dotenv sẽ được sử dụng để tải các biến môi trường
        từ các tệp :file:`.env` và :file:`.flaskenv`.
    """

    def __init__(
        self,
        add_default_commands: bool = True,
        create_app: t.Callable[..., Flask] | None = None,
        add_version_option: bool = True,
        load_dotenv: bool = True,
        set_debug_flag: bool = True,
        **extra: t.Any,
    ) -> None:
        params: list[click.Parameter] = list(extra.pop("params", None) or ())
        # Việc xử lý được thực hiện với các callback tùy chọn thay vì một callback
        # nhóm. Điều này cho phép người dùng tạo một callback nhóm tùy chỉnh
        # mà không làm mất hành vi. --env-file phải đến trước để
        # nó được đánh giá sớm trước --app.
        params.extend((_env_file_option, _app_option, _debug_option))

        if add_version_option:
            params.append(version_option)

        if "context_settings" not in extra:
            extra["context_settings"] = {}

        extra["context_settings"].setdefault("auto_envvar_prefix", "FLASK")

        super().__init__(params=params, **extra)

        self.create_app = create_app
        self.load_dotenv = load_dotenv
        self.set_debug_flag = set_debug_flag

        if add_default_commands:
            self.add_command(run_command)
            self.add_command(shell_command)
            self.add_command(routes_command)

        self._loaded_plugin_commands = False

    def _load_plugin_commands(self) -> None:
        if self._loaded_plugin_commands:
            return

        for ep in importlib.metadata.entry_points(group="flask.commands"):
            self.add_command(ep.load(), ep.name)

        self._loaded_plugin_commands = True

    def get_command(self, ctx: click.Context, name: str) -> click.Command | None:
        self._load_plugin_commands()
        # Tra cứu các lệnh tích hợp và plugin, những lệnh này nên
        # có sẵn ngay cả khi ứng dụng không tải được.
        rv = super().get_command(ctx, name)

        if rv is not None:
            return rv

        info = ctx.ensure_object(ScriptInfo)

        # Tra cứu các lệnh được cung cấp bởi ứng dụng, hiển thị lỗi và
        # tiếp tục nếu ứng dụng không thể tải được.
        try:
            app = info.load_app()
        except NoAppException as e:
            click.secho(f"Error: {e.format_message()}\n", err=True, fg="red")
            return None

        # Push một ngữ cảnh ứng dụng cho ứng dụng đã tải trừ khi nó đã
        # hoạt động theo cách nào đó. Điều này làm cho ngữ cảnh có sẵn cho
        # các callback tham số và lệnh mà không cần @with_appcontext.
        if not current_app or current_app._get_current_object() is not app:
            ctx.with_resource(app.app_context())

        return app.cli.get_command(ctx, name)

    def list_commands(self, ctx: click.Context) -> list[str]:
        self._load_plugin_commands()
        # Bắt đầu với các lệnh tích hợp và plugin.
        rv = set(super().list_commands(ctx))
        info = ctx.ensure_object(ScriptInfo)

        # Thêm các lệnh được cung cấp bởi ứng dụng, hiển thị lỗi và
        # tiếp tục nếu ứng dụng không thể tải được.
        try:
            rv.update(info.load_app().cli.list_commands(ctx))
        except NoAppException as e:
            # Khi một ứng dụng không thể tải được, hiển thị thông báo lỗi
            # mà không có traceback.
            click.secho(f"Error: {e.format_message()}\n", err=True, fg="red")
        except Exception:
            # Khi bất kỳ lỗi nào khác xảy ra trong quá trình tải, hiển thị
            # traceback đầy đủ.
            click.secho(f"{traceback.format_exc()}\n", err=True, fg="red")

        return sorted(rv)

    def make_context(
        self,
        info_name: str | None,
        args: list[str],
        parent: click.Context | None = None,
        **extra: t.Any,
    ) -> click.Context:
        # Thiết lập cờ để báo cho app.run trở thành no-op. Nếu app.run
        # không nằm trong guard __name__ == __main__, nó sẽ khởi động server
        # khi import, chặn bất kỳ lệnh nào đang được gọi.
        os.environ["FLASK_RUN_FROM_CLI"] = "true"

        if "obj" not in extra and "obj" not in self.context_settings:
            extra["obj"] = ScriptInfo(
                create_app=self.create_app,
                set_debug_flag=self.set_debug_flag,
                load_dotenv_defaults=self.load_dotenv,
            )

        return super().make_context(info_name, args, parent=parent, **extra)

    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        if (not args and self.no_args_is_help) or (
            len(args) == 1 and args[0] in self.get_help_option_names(ctx)
        ):
            # Cố gắng tải --env-file và --app sớm trong trường hợp chúng
            # được đưa ra dưới dạng biến môi trường. Nếu không no_args_is_help sẽ không
            # thấy các lệnh từ app.cli.
            _env_file_option.handle_parse_result(ctx, {}, [])
            _app_option.handle_parse_result(ctx, {}, [])

        return super().parse_args(ctx, args)


def _path_is_ancestor(path: str, other: str) -> bool:
    """Lấy ``other`` và loại bỏ độ dài của ``path`` khỏi nó. Sau đó nối nó
    với ``path``. Nếu nó là giá trị ban đầu, ``path`` là tổ tiên của
    ``other``."""
    return os.path.join(path, other[len(path) :].lstrip(os.sep)) == other


def load_dotenv(
    path: str | os.PathLike[str] | None = None, load_defaults: bool = True
) -> bool:
    """Tải các tệp "dotenv" để thiết lập các biến môi trường. Một đường dẫn nhất định được ưu tiên
    hơn ``.env``, cái mà được ưu tiên hơn ``.flaskenv``. Sau khi
    tải và kết hợp các tệp này, các giá trị chỉ được thiết lập nếu khóa chưa
    được thiết lập trong ``os.environ``.

    Đây là một no-op nếu `python-dotenv`_ không được cài đặt.

    .. _python-dotenv: https://github.com/theskumar/python-dotenv#readme

    :param path: Tải tệp tại vị trí này.
    :param load_defaults: Tìm kiếm và tải các tệp ``.flaskenv`` và
        ``.env`` mặc định.
    :return: ``True`` nếu ít nhất một biến môi trường đã được tải.

    .. versionchanged:: 3.1
        Đã thêm tham số ``load_defaults``. Một đường dẫn nhất định được ưu tiên
        hơn các tệp mặc định.

    .. versionchanged:: 2.0
        Thư mục hiện tại không bị thay đổi sang vị trí của
        tệp đã tải.

    .. versionchanged:: 2.0
        Khi tải các tệp env, thiết lập mã hóa mặc định thành UTF-8.

    .. versionchanged:: 1.1.0
        Trả về ``False`` khi python-dotenv không được cài đặt, hoặc khi
        đường dẫn đã cho không phải là một tệp.

    .. versionadded:: 1.0
    """
    try:
        import dotenv
    except ImportError:
        if path or os.path.isfile(".env") or os.path.isfile(".flaskenv"):
            click.secho(
                " * Tip: There are .env files present. Install python-dotenv"
                " to use them.",
                fg="yellow",
                err=True,
            )

        return False

    data: dict[str, str | None] = {}

    if load_defaults:
        for default_name in (".flaskenv", ".env"):
            if not (default_path := dotenv.find_dotenv(default_name, usecwd=True)):
                continue

            data |= dotenv.dotenv_values(default_path, encoding="utf-8")

    if path is not None and os.path.isfile(path):
        data |= dotenv.dotenv_values(path, encoding="utf-8")

    for key, value in data.items():
        if key in os.environ or value is None:
            continue

        os.environ[key] = value

    return bool(data)  # True if at least one env var was loaded.


def show_server_banner(debug: bool, app_import_path: str | None) -> None:
    """Hiển thị thêm các thông báo khởi động lần đầu tiên server được chạy,
    bỏ qua reloader.
    """
    if is_running_from_reloader():
        return

    if app_import_path is not None:
        click.echo(f" * Serving Flask app '{app_import_path}'")

    if debug is not None:
        click.echo(f" * Debug mode: {'on' if debug else 'off'}")


class CertParamType(click.ParamType):
    """Loại tùy chọn Click cho tùy chọn ``--cert``. Cho phép hoặc một
    tệp hiện có, chuỗi ``'adhoc'``, hoặc một import cho một
    đối tượng :class:`~ssl.SSLContext`.
    """

    name = "path"

    def __init__(self) -> None:
        self.path_type = click.Path(exists=True, dir_okay=False, resolve_path=True)

    def convert(
        self, value: t.Any, param: click.Parameter | None, ctx: click.Context | None
    ) -> t.Any:
        try:
            import ssl
        except ImportError:
            raise click.BadParameter(
                'Using "--cert" requires Python to be compiled with SSL support.',
                ctx,
                param,
            ) from None

        try:
            return self.path_type(value, param, ctx)
        except click.BadParameter:
            value = click.STRING(value, param, ctx).lower()

            if value == "adhoc":
                try:
                    import cryptography  # noqa: F401
                except ImportError:
                    raise click.BadParameter(
                        "Using ad-hoc certificates requires the cryptography library.",
                        ctx,
                        param,
                    ) from None

                return value

            obj = import_string(value, silent=True)

            if isinstance(obj, ssl.SSLContext):
                return obj

            raise


def _validate_key(ctx: click.Context, param: click.Parameter, value: t.Any) -> t.Any:
    """Tùy chọn ``--key`` phải được chỉ định khi ``--cert`` là một tệp.
    Sửa đổi tham số ``cert`` thành một cặp ``(cert, key)`` nếu cần.
    """
    cert = ctx.params.get("cert")
    is_adhoc = cert == "adhoc"

    try:
        import ssl
    except ImportError:
        is_context = False
    else:
        is_context = isinstance(cert, ssl.SSLContext)

    if value is not None:
        if is_adhoc:
            raise click.BadParameter(
                'When "--cert" is "adhoc", "--key" is not used.', ctx, param
            )

        if is_context:
            raise click.BadParameter(
                'When "--cert" is an SSLContext object, "--key" is not used.',
                ctx,
                param,
            )

        if not cert:
            raise click.BadParameter('"--cert" must also be specified.', ctx, param)

        ctx.params["cert"] = cert, value

    else:
        if cert and not (is_adhoc or is_context):
            raise click.BadParameter('Required when using "--cert".', ctx, param)

    return value


class SeparatedPathType(click.Path):
    """Loại tùy chọn Click chấp nhận một danh sách các giá trị được phân tách bằng
    dấu phân cách đường dẫn của OS (``:``, ``;`` trên Windows). Mỗi giá trị được
    xác thực như một loại :class:`click.Path`.
    """

    def convert(
        self, value: t.Any, param: click.Parameter | None, ctx: click.Context | None
    ) -> t.Any:
        items = self.split_envvar_value(value)
        # can't call no-arg super() inside list comprehension until Python 3.12
        super_convert = super().convert
        return [super_convert(item, param, ctx) for item in items]


@click.command("run", short_help="Chạy một server phát triển.")
@click.option("--host", "-h", default="127.0.0.1", help="Giao diện để liên kết.")
@click.option("--port", "-p", default=5000, help="Cổng để liên kết.")
@click.option(
    "--cert",
    type=CertParamType(),
    help="Chỉ định một tệp chứng chỉ để sử dụng HTTPS.",
    is_eager=True,
)
@click.option(
    "--key",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    callback=_validate_key,
    expose_value=False,
    help="Tệp khóa để sử dụng khi chỉ định một chứng chỉ.",
)
@click.option(
    "--reload/--no-reload",
    default=None,
    help="Bật hoặc tắt reloader. Theo mặc định reloader "
    "hoạt động nếu debug được bật.",
)
@click.option(
    "--debugger/--no-debugger",
    default=None,
    help="Bật hoặc tắt debugger. Theo mặc định debugger "
    "hoạt động nếu debug được bật.",
)
@click.option(
    "--with-threads/--without-threads",
    default=True,
    help="Bật hoặc tắt đa luồng.",
)
@click.option(
    "--extra-files",
    default=None,
    type=SeparatedPathType(),
    help=(
        "Các tệp bổ sung kích hoạt reload khi thay đổi. Nhiều đường dẫn"
        f" được phân tách bằng {os.path.pathsep!r}."
    ),
)
@click.option(
    "--exclude-patterns",
    default=None,
    type=SeparatedPathType(),
    help=(
        "Các tệp khớp với các mẫu fnmatch này sẽ không kích hoạt reload"
        " khi thay đổi. Nhiều mẫu được phân tách bằng"
        f" {os.path.pathsep!r}."
    ),
)
@pass_script_info
def run_command(
    info: ScriptInfo,
    host: str,
    port: int,
    reload: bool,
    debugger: bool,
    with_threads: bool,
    cert: ssl.SSLContext | tuple[str, str | None] | t.Literal["adhoc"] | None,
    extra_files: list[str] | None,
    exclude_patterns: list[str] | None,
) -> None:
    """Chạy một server phát triển cục bộ.

    Server này chỉ dành cho mục đích phát triển. Nó không cung cấp
    sự ổn định, bảo mật, hoặc hiệu suất của các server WSGI sản xuất.

    Reloader và debugger được bật theo mặc định với tùy chọn '--debug'.
    """
    try:
        app: WSGIApplication = info.load_app()  # pyright: ignore
    except Exception as e:
        if is_running_from_reloader():
            # Khi reload, in ra lỗi ngay lập tức, nhưng ném
            # nó sau đó để debugger hoặc server có thể xử lý nó.
            traceback.print_exc()
            err = e

            def app(
                environ: WSGIEnvironment, start_response: StartResponse
            ) -> cabc.Iterable[bytes]:
                raise err from None

        else:
            # Khi không reload, ném lỗi ngay lập tức để
            # lệnh thất bại.
            raise e from None

    debug = get_debug_flag()

    if reload is None:
        reload = debug

    if debugger is None:
        debugger = debug

    show_server_banner(debug, info.app_import_path)

    run_simple(
        host,
        port,
        app,
        use_reloader=reload,
        use_debugger=debugger,
        threaded=with_threads,
        ssl_context=cert,
        extra_files=extra_files,
        exclude_patterns=exclude_patterns,
    )


run_command.params.insert(0, _debug_option)


@click.command("shell", short_help="Chạy một shell trong ngữ cảnh ứng dụng.")
@with_appcontext
def shell_command() -> None:
    """Chạy một Python shell tương tác trong ngữ cảnh của một
    ứng dụng Flask đã cho. Ứng dụng sẽ điền vào namespace mặc định
    của shell này theo cấu hình của nó.

    Điều này hữu ích để thực thi các đoạn mã quản lý nhỏ
    mà không cần phải cấu hình thủ công ứng dụng.
    """
    import code

    banner = (
        f"Python {sys.version} on {sys.platform}\n"
        f"App: {current_app.import_name}\n"
        f"Instance: {current_app.instance_path}"
    )
    ctx: dict[str, t.Any] = {}

    # Hỗ trợ script khởi động trình thông dịch Python thông thường nếu ai đó
    # đang sử dụng nó.
    startup = os.environ.get("PYTHONSTARTUP")
    if startup and os.path.isfile(startup):
        with open(startup) as f:
            eval(compile(f.read(), startup, "exec"), ctx)

    ctx.update(current_app.make_shell_context())

    # Site, customize, hoặc startup script có thể thiết lập một hook để gọi khi
    # vào chế độ tương tác. Cái mặc định thiết lập readline với
    # tab và hoàn thành lịch sử.
    interactive_hook = getattr(sys, "__interactivehook__", None)

    if interactive_hook is not None:
        try:
            import readline
            from rlcompleter import Completer
        except ImportError:
            pass
        else:
            # rlcompleter sử dụng __main__.__dict__ theo mặc định, cái mà là
            # flask.__main__. Sử dụng ngữ cảnh shell thay thế.
            readline.set_completer(Completer(ctx).complete)

        interactive_hook()

    code.interact(banner=banner, local=ctx)


@click.command("routes", short_help="Hiển thị các route cho ứng dụng.")
@click.option(
    "--sort",
    "-s",
    type=click.Choice(("endpoint", "methods", "domain", "rule", "match")),
    default="endpoint",
    help=(
        "Phương thức để sắp xếp các route theo. 'match' là thứ tự mà Flask sẽ khớp các route"
        " khi điều phối một request."
    ),
)
@click.option("--all-methods", is_flag=True, help="Hiển thị các phương thức HEAD và OPTIONS.")
@with_appcontext
def routes_command(sort: str, all_methods: bool) -> None:
    """Hiển thị tất cả các route đã đăng ký với các endpoint và phương thức."""
    rules = list(current_app.url_map.iter_rules())

    if not rules:
        click.echo("Không có route nào được đăng ký.")
        return

    ignored_methods = set() if all_methods else {"HEAD", "OPTIONS"}
    host_matching = current_app.url_map.host_matching
    has_domain = any(rule.host if host_matching else rule.subdomain for rule in rules)
    rows = []

    for rule in rules:
        row = [
            rule.endpoint,
            ", ".join(sorted((rule.methods or set()) - ignored_methods)),
        ]

        if has_domain:
            row.append((rule.host if host_matching else rule.subdomain) or "")

        row.append(rule.rule)
        rows.append(row)

    headers = ["Endpoint", "Methods"]
    sorts = ["endpoint", "methods"]

    if has_domain:
        headers.append("Host" if host_matching else "Subdomain")
        sorts.append("domain")

    headers.append("Rule")
    sorts.append("rule")

    try:
        rows.sort(key=itemgetter(sorts.index(sort)))
    except ValueError:
        pass

    rows.insert(0, headers)
    widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
    rows.insert(1, ["-" * w for w in widths])
    template = "  ".join(f"{{{i}:<{w}}}" for i, w in enumerate(widths))

    for row in rows:
        click.echo(template.format(*row))


cli = FlaskGroup(
    name="flask",
    help="""\
Một script tiện ích chung cho các ứng dụng Flask.

Một ứng dụng để tải phải được đưa ra với tùy chọn '--app',
biến môi trường 'FLASK_APP', hoặc với một tệp 'wsgi.py' hoặc 'app.py'
trong thư mục hiện tại.
""",
)


def main() -> None:
    cli.main()


if __name__ == "__main__":
    main()
