from __future__ import annotations

import os
import typing as t
from collections import defaultdict
from functools import update_wrapper

from .. import typing as ft
from .scaffold import _endpoint_from_view_func
from .scaffold import _sentinel
from .scaffold import Scaffold
from .scaffold import setupmethod

if t.TYPE_CHECKING:  # pragma: no cover
    from .app import App

DeferredSetupFunction = t.Callable[["BlueprintSetupState"], None]
T_after_request = t.TypeVar("T_after_request", bound=ft.AfterRequestCallable[t.Any])
T_before_request = t.TypeVar("T_before_request", bound=ft.BeforeRequestCallable)
T_error_handler = t.TypeVar("T_error_handler", bound=ft.ErrorHandlerCallable)
T_teardown = t.TypeVar("T_teardown", bound=ft.TeardownCallable)
T_template_context_processor = t.TypeVar(
    "T_template_context_processor", bound=ft.TemplateContextProcessorCallable
)
T_template_filter = t.TypeVar("T_template_filter", bound=ft.TemplateFilterCallable)
T_template_global = t.TypeVar("T_template_global", bound=ft.TemplateGlobalCallable)
T_template_test = t.TypeVar("T_template_test", bound=ft.TemplateTestCallable)
T_url_defaults = t.TypeVar("T_url_defaults", bound=ft.URLDefaultCallable)
T_url_value_preprocessor = t.TypeVar(
    "T_url_value_preprocessor", bound=ft.URLValuePreprocessorCallable
)


class BlueprintSetupState:
    """Đối tượng giữ tạm thời để đăng ký một blueprint với
    ứng dụng. Một thể hiện của lớp này được tạo bởi phương thức
    :meth:`~flask.Blueprint.make_setup_state` và sau đó được truyền
    đến tất cả các hàm callback đăng ký.
    """

    def __init__(
        self,
        blueprint: Blueprint,
        app: App,
        options: t.Any,
        first_registration: bool,
    ) -> None:
        #: tham chiếu đến ứng dụng hiện tại
        self.app = app

        #: tham chiếu đến blueprint đã tạo trạng thái thiết lập này.
        self.blueprint = blueprint

        #: một từ điển với tất cả các tùy chọn đã được truyền cho
        #: phương thức :meth:`~flask.Flask.register_blueprint`.
        self.options = options

        #: vì các blueprint có thể được đăng ký nhiều lần với
        #: ứng dụng và không phải mọi thứ đều muốn được đăng ký
        #: nhiều lần trên đó, thuộc tính này có thể được sử dụng để tìm ra
        #: liệu blueprint đã được đăng ký trong quá khứ hay chưa.
        self.first_registration = first_registration

        subdomain = self.options.get("subdomain")
        if subdomain is None:
            subdomain = self.blueprint.subdomain

        #: Tên miền phụ mà blueprint nên hoạt động, ``None``
        #: nếu không.
        self.subdomain = subdomain

        url_prefix = self.options.get("url_prefix")
        if url_prefix is None:
            url_prefix = self.blueprint.url_prefix
        #: Tiền tố nên được sử dụng cho tất cả các URL được định nghĩa trên
        #: blueprint.
        self.url_prefix = url_prefix

        self.name = self.options.get("name", blueprint.name)
        self.name_prefix = self.options.get("name_prefix", "")

        #: Một từ điển với các giá trị mặc định URL được thêm vào mỗi và mọi
        #: URL đã được định nghĩa với blueprint.
        self.url_defaults = dict(self.blueprint.url_values_defaults)
        self.url_defaults.update(self.options.get("url_defaults", ()))

    def add_url_rule(
        self,
        rule: str,
        endpoint: str | None = None,
        view_func: ft.RouteCallable | None = None,
        **options: t.Any,
    ) -> None:
        """Một phương thức trợ giúp để đăng ký một quy tắc (và tùy chọn một hàm view)
        với ứng dụng. Endpoint được tự động thêm tiền tố với tên của
        blueprint.
        """
        if self.url_prefix is not None:
            if rule:
                rule = "/".join((self.url_prefix.rstrip("/"), rule.lstrip("/")))
            else:
                rule = self.url_prefix
        options.setdefault("subdomain", self.subdomain)
        if endpoint is None:
            endpoint = _endpoint_from_view_func(view_func)  # type: ignore
        defaults = self.url_defaults
        if "defaults" in options:
            defaults = dict(defaults, **options.pop("defaults"))

        self.app.add_url_rule(
            rule,
            f"{self.name_prefix}.{self.name}.{endpoint}".lstrip("."),
            view_func,
            defaults=defaults,
            **options,
        )


class Blueprint(Scaffold):
    """Đại diện cho một blueprint, một tập hợp các route và các hàm
    liên quan đến ứng dụng khác có thể được đăng ký trên một ứng dụng thực
    sau này.

    Một blueprint là một đối tượng cho phép định nghĩa các hàm ứng dụng
    mà không yêu cầu một đối tượng ứng dụng trước. Nó sử dụng các
    decorator giống như :class:`~flask.Flask`, nhưng hoãn nhu cầu về một
    ứng dụng bằng cách ghi lại chúng để đăng ký sau.

    Trang trí một hàm với một blueprint tạo ra một hàm bị hoãn
    được gọi với :class:`~flask.blueprints.BlueprintSetupState`
    khi blueprint được đăng ký trên một ứng dụng.

    Xem :doc:`/blueprints` để biết thêm thông tin.

    :param name: Tên của blueprint. Sẽ được thêm vào trước mỗi
        tên endpoint.
    :param import_name: Tên của package blueprint, thường là
        ``__name__``. Điều này giúp định vị ``root_path`` cho
        blueprint.
    :param static_folder: Một thư mục với các tệp tĩnh nên được
        phục vụ bởi route tĩnh của blueprint. Đường dẫn tương đối với
        đường dẫn gốc của blueprint. Các tệp tĩnh của blueprint bị vô hiệu hóa
        theo mặc định.
    :param static_url_path: Url để phục vụ các tệp tĩnh từ đó.
        Mặc định là ``static_folder``. Nếu blueprint không có
        ``url_prefix``, route tĩnh của ứng dụng sẽ được ưu tiên,
        và các tệp tĩnh của blueprint sẽ không thể truy cập được.
    :param template_folder: Một thư mục với các template nên được thêm
        vào đường dẫn tìm kiếm template của ứng dụng. Đường dẫn tương đối với
        đường dẫn gốc của blueprint. Các template của blueprint bị vô hiệu hóa theo
        mặc định. Các template của blueprint có độ ưu tiên thấp hơn so với những cái
        trong thư mục templates của ứng dụng.
    :param url_prefix: Một đường dẫn để thêm vào trước tất cả các URL của blueprint,
        để làm cho chúng khác biệt với phần còn lại của các route của ứng dụng.
    :param subdomain: Một tên miền phụ mà các route của blueprint sẽ khớp theo
        mặc định.
    :param url_defaults: Một dict các giá trị mặc định mà các route của blueprint
        sẽ nhận được theo mặc định.
    :param root_path: Theo mặc định, blueprint sẽ tự động đặt
        điều này dựa trên ``import_name``. Trong một số tình huống nhất định, việc
        phát hiện tự động này có thể thất bại, vì vậy đường dẫn có thể được chỉ định
        thủ công thay thế.

    .. versionchanged:: 1.1.0
        Blueprints có một nhóm ``cli`` để đăng ký các lệnh CLI lồng nhau.
        Tham số ``cli_group`` kiểm soát tên của nhóm dưới
        lệnh ``flask``.

    .. versionadded:: 0.7
    """

    _got_registered_once = False

    def __init__(
        self,
        name: str,
        import_name: str,
        static_folder: str | os.PathLike[str] | None = None,
        static_url_path: str | None = None,
        template_folder: str | os.PathLike[str] | None = None,
        url_prefix: str | None = None,
        subdomain: str | None = None,
        url_defaults: dict[str, t.Any] | None = None,
        root_path: str | None = None,
        cli_group: str | None = _sentinel,  # type: ignore[assignment]
    ):
        super().__init__(
            import_name=import_name,
            static_folder=static_folder,
            static_url_path=static_url_path,
            template_folder=template_folder,
            root_path=root_path,
        )

        if not name:
            raise ValueError("'name' may not be empty.")

        if "." in name:
            raise ValueError("'name' may not contain a dot '.' character.")

        self.name = name
        self.url_prefix = url_prefix
        self.subdomain = subdomain
        self.deferred_functions: list[DeferredSetupFunction] = []

        if url_defaults is None:
            url_defaults = {}

        self.url_values_defaults = url_defaults
        self.cli_group = cli_group
        self._blueprints: list[tuple[Blueprint, dict[str, t.Any]]] = []

    def _check_setup_finished(self, f_name: str) -> None:
        if self._got_registered_once:
            raise AssertionError(
                f"The setup method '{f_name}' can no longer be called on the blueprint"
                f" '{self.name}'. It has already been registered at least once, any"
                " changes will not be applied consistently.\n"
                "Make sure all imports, decorators, functions, etc. needed to set up"
                " the blueprint are done before registering it."
            )

    @setupmethod
    def record(self, func: DeferredSetupFunction) -> None:
        """Đăng ký một hàm được gọi khi blueprint được
        đăng ký trên ứng dụng. Hàm này được gọi với
        trạng thái làm đối số như được trả về bởi phương thức :meth:`make_setup_state`.
        """
        self.deferred_functions.append(func)

    @setupmethod
    def record_once(self, func: DeferredSetupFunction) -> None:
        """Hoạt động giống như :meth:`record` nhưng bọc hàm trong một hàm khác
        sẽ đảm bảo hàm chỉ được gọi một lần. Nếu blueprint
        được đăng ký lần thứ hai trên ứng dụng, hàm
        được truyền sẽ không được gọi.
        """

        def wrapper(state: BlueprintSetupState) -> None:
            if state.first_registration:
                func(state)

        self.record(update_wrapper(wrapper, func))

    def make_setup_state(
        self, app: App, options: dict[str, t.Any], first_registration: bool = False
    ) -> BlueprintSetupState:
        """Tạo một thể hiện của đối tượng :meth:`~flask.blueprints.BlueprintSetupState`
        sau đó được truyền đến các hàm callback đăng ký.
        Các lớp con có thể ghi đè điều này để trả về một lớp con của trạng thái thiết lập.
        """
        return BlueprintSetupState(self, app, options, first_registration)

    @setupmethod
    def register_blueprint(self, blueprint: Blueprint, **options: t.Any) -> None:
        """Đăng ký một :class:`~flask.Blueprint` trên blueprint này. Các đối số
        từ khóa được truyền cho phương thức này sẽ ghi đè các mặc định được đặt
        trên blueprint.

        .. versionchanged:: 2.0.1
            Tùy chọn ``name`` có thể được sử dụng để thay đổi tên (trước khi có dấu chấm)
            mà blueprint được đăng ký. Điều này cho phép cùng một
            blueprint được đăng ký nhiều lần với các tên duy nhất
            cho ``url_for``.

        .. versionadded:: 2.0
        """
        if blueprint is self:
            raise ValueError("Cannot register a blueprint on itself")
        self._blueprints.append((blueprint, options))

    def register(self, app: App, options: dict[str, t.Any]) -> None:
        """Được gọi bởi :meth:`Flask.register_blueprint` để đăng ký tất cả
        các view và callback đã đăng ký trên blueprint với
        ứng dụng. Tạo một :class:`.BlueprintSetupState` và gọi
        mỗi callback :meth:`record` với nó.

        :param app: Ứng dụng mà blueprint này đang được đăng ký
            cùng.
        :param options: Các đối số từ khóa được chuyển tiếp từ
            :meth:`~Flask.register_blueprint`.

        .. versionchanged:: 2.3
            Các blueprint lồng nhau hiện áp dụng chính xác các tên miền phụ.

        .. versionchanged:: 2.1
            Đăng ký cùng một blueprint với cùng tên nhiều lần
            là một lỗi.

        .. versionchanged:: 2.0.1
            Các blueprint lồng nhau được đăng ký với tên có dấu chấm của chúng.
            Điều này cho phép các blueprint khác nhau có cùng tên được
            lồng nhau tại các vị trí khác nhau.

        .. versionchanged:: 2.0.1
            Tùy chọn ``name`` có thể được sử dụng để thay đổi tên (trước khi có dấu chấm)
            mà blueprint được đăng ký. Điều này cho phép cùng một
            blueprint được đăng ký nhiều lần với các tên duy nhất
            cho ``url_for``.
        """
        name_prefix = options.get("name_prefix", "")
        self_name = options.get("name", self.name)
        name = f"{name_prefix}.{self_name}".lstrip(".")

        if name in app.blueprints:
            bp_desc = "this" if app.blueprints[name] is self else "a different"
            existing_at = f" '{name}'" if self_name != name else ""

            raise ValueError(
                f"The name '{self_name}' is already registered for"
                f" {bp_desc} blueprint{existing_at}. Use 'name=' to"
                f" provide a unique name."
            )

        first_bp_registration = not any(bp is self for bp in app.blueprints.values())
        first_name_registration = name not in app.blueprints

        app.blueprints[name] = self
        self._got_registered_once = True
        state = self.make_setup_state(app, options, first_bp_registration)

        if self.has_static_folder:
            state.add_url_rule(
                f"{self.static_url_path}/<path:filename>",
                view_func=self.send_static_file,  # type: ignore[attr-defined]
                endpoint="static",
            )

        # Merge blueprint data into parent.
        if first_bp_registration or first_name_registration:
            self._merge_blueprint_funcs(app, name)

        for deferred in self.deferred_functions:
            deferred(state)

        cli_resolved_group = options.get("cli_group", self.cli_group)

        if self.cli.commands:
            if cli_resolved_group is None:
                app.cli.commands.update(self.cli.commands)
            elif cli_resolved_group is _sentinel:
                self.cli.name = name
                app.cli.add_command(self.cli)
            else:
                self.cli.name = cli_resolved_group
                app.cli.add_command(self.cli)

        for blueprint, bp_options in self._blueprints:
            bp_options = bp_options.copy()
            bp_url_prefix = bp_options.get("url_prefix")
            bp_subdomain = bp_options.get("subdomain")

            if bp_subdomain is None:
                bp_subdomain = blueprint.subdomain

            if state.subdomain is not None and bp_subdomain is not None:
                bp_options["subdomain"] = bp_subdomain + "." + state.subdomain
            elif bp_subdomain is not None:
                bp_options["subdomain"] = bp_subdomain
            elif state.subdomain is not None:
                bp_options["subdomain"] = state.subdomain

            if bp_url_prefix is None:
                bp_url_prefix = blueprint.url_prefix

            if state.url_prefix is not None and bp_url_prefix is not None:
                bp_options["url_prefix"] = (
                    state.url_prefix.rstrip("/") + "/" + bp_url_prefix.lstrip("/")
                )
            elif bp_url_prefix is not None:
                bp_options["url_prefix"] = bp_url_prefix
            elif state.url_prefix is not None:
                bp_options["url_prefix"] = state.url_prefix

            bp_options["name_prefix"] = name
            blueprint.register(app, bp_options)

    def _merge_blueprint_funcs(self, app: App, name: str) -> None:
        def extend(
            bp_dict: dict[ft.AppOrBlueprintKey, list[t.Any]],
            parent_dict: dict[ft.AppOrBlueprintKey, list[t.Any]],
        ) -> None:
            for key, values in bp_dict.items():
                key = name if key is None else f"{name}.{key}"
                parent_dict[key].extend(values)

        for key, value in self.error_handler_spec.items():
            key = name if key is None else f"{name}.{key}"
            value = defaultdict(
                dict,
                {
                    code: {exc_class: func for exc_class, func in code_values.items()}
                    for code, code_values in value.items()
                },
            )
            app.error_handler_spec[key] = value

        for endpoint, func in self.view_functions.items():
            app.view_functions[endpoint] = func

        extend(self.before_request_funcs, app.before_request_funcs)
        extend(self.after_request_funcs, app.after_request_funcs)
        extend(
            self.teardown_request_funcs,
            app.teardown_request_funcs,
        )
        extend(self.url_default_functions, app.url_default_functions)
        extend(self.url_value_preprocessors, app.url_value_preprocessors)
        extend(self.template_context_processors, app.template_context_processors)

    @setupmethod
    def add_url_rule(
        self,
        rule: str,
        endpoint: str | None = None,
        view_func: ft.RouteCallable | None = None,
        provide_automatic_options: bool | None = None,
        **options: t.Any,
    ) -> None:
        """Đăng ký một quy tắc URL với blueprint. Xem :meth:`.Flask.add_url_rule` để biết
        tài liệu đầy đủ.

        Quy tắc URL được thêm tiền tố với tiền tố URL của blueprint. Tên endpoint,
        được sử dụng với :func:`url_for`, được thêm tiền tố với tên của blueprint.
        """
        if endpoint and "." in endpoint:
            raise ValueError("'endpoint' may not contain a dot '.' character.")

        if view_func and hasattr(view_func, "__name__") and "." in view_func.__name__:
            raise ValueError("'view_func' name may not contain a dot '.' character.")

        self.record(
            lambda s: s.add_url_rule(
                rule,
                endpoint,
                view_func,
                provide_automatic_options=provide_automatic_options,
                **options,
            )
        )

    @t.overload
    def app_template_filter(self, name: T_template_filter) -> T_template_filter: ...
    @t.overload
    def app_template_filter(
        self, name: str | None = None
    ) -> t.Callable[[T_template_filter], T_template_filter]: ...
    @setupmethod
    def app_template_filter(
        self, name: T_template_filter | str | None = None
    ) -> T_template_filter | t.Callable[[T_template_filter], T_template_filter]:
        """Trang trí một hàm để đăng ký nó như một bộ lọc Jinja tùy chỉnh. Tên
        là tùy chọn. Decorator có thể được sử dụng mà không cần dấu ngoặc đơn.

        Phương thức :meth:`add_app_template_filter` có thể được sử dụng để đăng ký một
        hàm sau đó thay vì trang trí.

        Bộ lọc có sẵn trong tất cả các template, không chỉ những template dưới
        blueprint này. Tương đương với :meth:`.Flask.template_filter`.

        :param name: Tên để đăng ký bộ lọc. Nếu không được đưa ra, sử dụng
            tên của hàm.
        """
        if callable(name):
            self.add_app_template_filter(name)
            return name

        def decorator(f: T_template_filter) -> T_template_filter:
            self.add_app_template_filter(f, name=name)
            return f

        return decorator

    @setupmethod
    def add_app_template_filter(
        self, f: ft.TemplateFilterCallable, name: str | None = None
    ) -> None:
        """Đăng ký một hàm để sử dụng như một bộ lọc Jinja tùy chỉnh.

        Decorator :meth:`app_template_filter` có thể được sử dụng để đăng ký một
        hàm bằng cách trang trí thay thế.

        Bộ lọc có sẵn trong tất cả các template, không chỉ những template dưới
        blueprint này. Tương đương với :meth:`.Flask.add_template_filter`.

        :param f: Hàm để đăng ký.
        :param name: Tên để đăng ký bộ lọc. Nếu không được đưa ra, sử dụng
            tên của hàm.
        """

        def register_template_filter(state: BlueprintSetupState) -> None:
            state.app.add_template_filter(f, name=name)

        self.record_once(register_template_filter)

    @t.overload
    def app_template_test(self, name: T_template_test) -> T_template_test: ...
    @t.overload
    def app_template_test(
        self, name: str | None = None
    ) -> t.Callable[[T_template_test], T_template_test]: ...
    @setupmethod
    def app_template_test(
        self, name: T_template_test | str | None = None
    ) -> T_template_test | t.Callable[[T_template_test], T_template_test]:
        """Trang trí một hàm để đăng ký nó như một test Jinja tùy chỉnh. Tên
        là tùy chọn. Decorator có thể được sử dụng mà không cần dấu ngoặc đơn.

        Phương thức :meth:`add_app_template_test` có thể được sử dụng để đăng ký một
        hàm sau đó thay vì trang trí.

        Test có sẵn trong tất cả các template, không chỉ những template dưới
        blueprint này. Tương đương với :meth:`.Flask.template_test`.

        :param name: Tên để đăng ký bộ lọc. Nếu không được đưa ra, sử dụng
            tên của hàm.

        .. versionadded:: 0.10
        """
        if callable(name):
            self.add_app_template_test(name)
            return name

        def decorator(f: T_template_test) -> T_template_test:
            self.add_app_template_test(f, name=name)
            return f

        return decorator

    @setupmethod
    def add_app_template_test(
        self, f: ft.TemplateTestCallable, name: str | None = None
    ) -> None:
        """Đăng ký một hàm để sử dụng như một test Jinja tùy chỉnh.

        Decorator :meth:`app_template_test` có thể được sử dụng để đăng ký một
        hàm bằng cách trang trí thay thế.

        Test có sẵn trong tất cả các template, không chỉ những template dưới
        blueprint này. Tương đương với :meth:`.Flask.add_template_test`.

        :param f: Hàm để đăng ký.
        :param name: Tên để đăng ký test. Nếu không được đưa ra, sử dụng
            tên của hàm.

        .. versionadded:: 0.10
        """

        def register_template_test(state: BlueprintSetupState) -> None:
            state.app.add_template_test(f, name=name)

        self.record_once(register_template_test)

    @t.overload
    def app_template_global(self, name: T_template_global) -> T_template_global: ...
    @t.overload
    def app_template_global(
        self, name: str | None = None
    ) -> t.Callable[[T_template_global], T_template_global]: ...
    @setupmethod
    def app_template_global(
        self, name: T_template_global | str | None = None
    ) -> T_template_global | t.Callable[[T_template_global], T_template_global]:
        """Trang trí một hàm để đăng ký nó như một global Jinja tùy chỉnh. Tên
        là tùy chọn. Decorator có thể được sử dụng mà không cần dấu ngoặc đơn.

        Phương thức :meth:`add_app_template_global` có thể được sử dụng để đăng ký một
        hàm sau đó thay vì trang trí.

        Global có sẵn trong tất cả các template, không chỉ những template dưới
        blueprint này. Tương đương với :meth:`.Flask.template_global`.

        :param name: Tên để đăng ký global. Nếu không được đưa ra, sử dụng
            tên của hàm.

        .. versionadded:: 0.10
        """
        if callable(name):
            self.add_app_template_global(name)
            return name

        def decorator(f: T_template_global) -> T_template_global:
            self.add_app_template_global(f, name=name)
            return f

        return decorator

    @setupmethod
    def add_app_template_global(
        self, f: ft.TemplateGlobalCallable, name: str | None = None
    ) -> None:
        """Đăng ký một hàm để sử dụng như một global Jinja tùy chỉnh.

        Decorator :meth:`app_template_global` có thể được sử dụng để đăng ký một hàm
        bằng cách trang trí thay thế.

        Global có sẵn trong tất cả các template, không chỉ những template dưới
        blueprint này. Tương đương với :meth:`.Flask.add_template_global`.

        :param f: Hàm để đăng ký.
        :param name: Tên để đăng ký global. Nếu không được đưa ra, sử dụng
            tên của hàm.

        .. versionadded:: 0.10
        """

        def register_template_global(state: BlueprintSetupState) -> None:
            state.app.add_template_global(f, name=name)

        self.record_once(register_template_global)

    @setupmethod
    def before_app_request(self, f: T_before_request) -> T_before_request:
        """Giống như :meth:`before_request`, nhưng trước mỗi yêu cầu, không chỉ những yêu cầu được xử lý
        bởi blueprint. Tương đương với :meth:`.Flask.before_request`.
        """
        self.record_once(
            lambda s: s.app.before_request_funcs.setdefault(None, []).append(f)
        )
        return f

    @setupmethod
    def after_app_request(self, f: T_after_request) -> T_after_request:
        """Giống như :meth:`after_request`, nhưng sau mỗi yêu cầu, không chỉ những yêu cầu được xử lý
        bởi blueprint. Tương đương với :meth:`.Flask.after_request`.
        """
        self.record_once(
            lambda s: s.app.after_request_funcs.setdefault(None, []).append(f)
        )
        return f

    @setupmethod
    def teardown_app_request(self, f: T_teardown) -> T_teardown:
        """Giống như :meth:`teardown_request`, nhưng sau mỗi yêu cầu, không chỉ những yêu cầu
        được xử lý bởi blueprint. Tương đương với :meth:`.Flask.teardown_request`.
        """
        self.record_once(
            lambda s: s.app.teardown_request_funcs.setdefault(None, []).append(f)
        )
        return f

    @setupmethod
    def app_context_processor(
        self, f: T_template_context_processor
    ) -> T_template_context_processor:
        """Giống như :meth:`context_processor`, nhưng cho các template được render bởi mọi view, không
        chỉ bởi blueprint. Tương đương với :meth:`.Flask.context_processor`.
        """
        self.record_once(
            lambda s: s.app.template_context_processors.setdefault(None, []).append(f)
        )
        return f

    @setupmethod
    def app_errorhandler(
        self, code: type[Exception] | int
    ) -> t.Callable[[T_error_handler], T_error_handler]:
        """Giống như :meth:`errorhandler`, nhưng cho mỗi yêu cầu, không chỉ những yêu cầu được xử lý bởi
        blueprint. Tương đương với :meth:`.Flask.errorhandler`.
        """

        def decorator(f: T_error_handler) -> T_error_handler:
            def from_blueprint(state: BlueprintSetupState) -> None:
                state.app.errorhandler(code)(f)

            self.record_once(from_blueprint)
            return f

        return decorator

    @setupmethod
    def app_url_value_preprocessor(
        self, f: T_url_value_preprocessor
    ) -> T_url_value_preprocessor:
        """Giống như :meth:`url_value_preprocessor`, nhưng cho mỗi yêu cầu, không chỉ những yêu cầu
        được xử lý bởi blueprint. Tương đương với :meth:`.Flask.url_value_preprocessor`.
        """
        self.record_once(
            lambda s: s.app.url_value_preprocessors.setdefault(None, []).append(f)
        )
        return f

    @setupmethod
    def app_url_defaults(self, f: T_url_defaults) -> T_url_defaults:
        """Giống như :meth:`url_defaults`, nhưng cho mỗi yêu cầu, không chỉ những yêu cầu được xử lý bởi
        blueprint. Tương đương với :meth:`.Flask.url_defaults`.
        """
        self.record_once(
            lambda s: s.app.url_default_functions.setdefault(None, []).append(f)
        )
        return f
