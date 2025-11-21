from __future__ import annotations

import typing as t

from jinja2 import BaseLoader
from jinja2 import Environment as BaseEnvironment
from jinja2 import Template
from jinja2 import TemplateNotFound

from .globals import _cv_app
from .globals import current_app
from .helpers import stream_with_context
from .signals import before_render_template
from .signals import template_rendered

if t.TYPE_CHECKING:  # pragma: no cover
    from .app import Flask
    from .sansio.app import App
    from .sansio.scaffold import Scaffold


def _default_template_ctx_processor() -> dict[str, t.Any]:
    """Bộ xử lý ngữ cảnh template mặc định. Inject `request`,
    `session` và `g`.
    """
    ctx = _cv_app.get(None)
    rv: dict[str, t.Any] = {}

    if ctx is not None:
        rv["g"] = ctx.g

        if ctx.has_request:
            rv["request"] = ctx.request
            rv["session"] = ctx.session

    return rv


class Environment(BaseEnvironment):
    """Hoạt động giống như một môi trường Jinja thông thường nhưng có thêm một số
    kiến thức về cách blueprint của Flask hoạt động để nó có thể thêm
    tên của blueprint vào trước các template được tham chiếu nếu cần thiết.
    """

    def __init__(self, app: App, **options: t.Any) -> None:
        if "loader" not in options:
            options["loader"] = app.create_global_jinja_loader()
        BaseEnvironment.__init__(self, **options)
        self.app = app


class DispatchingJinjaLoader(BaseLoader):
    """Một loader tìm kiếm các template trong ứng dụng và tất cả
    các thư mục blueprint.
    """

    def __init__(self, app: App) -> None:
        self.app = app

    def get_source(
        self, environment: BaseEnvironment, template: str
    ) -> tuple[str, str | None, t.Callable[[], bool] | None]:
        if self.app.config["EXPLAIN_TEMPLATE_LOADING"]:
            return self._get_source_explained(environment, template)
        return self._get_source_fast(environment, template)

    def _get_source_explained(
        self, environment: BaseEnvironment, template: str
    ) -> tuple[str, str | None, t.Callable[[], bool] | None]:
        attempts = []
        rv: tuple[str, str | None, t.Callable[[], bool] | None] | None
        trv: None | (tuple[str, str | None, t.Callable[[], bool] | None]) = None

        for srcobj, loader in self._iter_loaders(template):
            try:
                rv = loader.get_source(environment, template)
                if trv is None:
                    trv = rv
            except TemplateNotFound:
                rv = None
            attempts.append((loader, srcobj, rv))

        from .debughelpers import explain_template_loading_attempts

        explain_template_loading_attempts(self.app, template, attempts)

        if trv is not None:
            return trv
        raise TemplateNotFound(template)

    def _get_source_fast(
        self, environment: BaseEnvironment, template: str
    ) -> tuple[str, str | None, t.Callable[[], bool] | None]:
        for _srcobj, loader in self._iter_loaders(template):
            try:
                return loader.get_source(environment, template)
            except TemplateNotFound:
                continue
        raise TemplateNotFound(template)

    def _iter_loaders(self, template: str) -> t.Iterator[tuple[Scaffold, BaseLoader]]:
        loader = self.app.jinja_loader
        if loader is not None:
            yield self.app, loader

        for blueprint in self.app.iter_blueprints():
            loader = blueprint.jinja_loader
            if loader is not None:
                yield blueprint, loader

    def list_templates(self) -> list[str]:
        result = set()
        loader = self.app.jinja_loader
        if loader is not None:
            result.update(loader.list_templates())

        for blueprint in self.app.iter_blueprints():
            loader = blueprint.jinja_loader
            if loader is not None:
                for template in loader.list_templates():
                    result.add(template)

        return list(result)


def _render(app: Flask, template: Template, context: dict[str, t.Any]) -> str:
    app.update_template_context(context)
    before_render_template.send(
        app, _async_wrapper=app.ensure_sync, template=template, context=context
    )
    rv = template.render(context)
    template_rendered.send(
        app, _async_wrapper=app.ensure_sync, template=template, context=context
    )
    return rv


def render_template(
    template_name_or_list: str | Template | list[str | Template],
    **context: t.Any,
) -> str:
    """Render một template theo tên với ngữ cảnh đã cho.

    :param template_name_or_list: Tên của template để render. Nếu
        một danh sách được đưa ra, tên đầu tiên tồn tại sẽ được render.
    :param context: Các biến để làm cho có sẵn trong template.
    """
    app = current_app._get_current_object()
    template = app.jinja_env.get_or_select_template(template_name_or_list)
    return _render(app, template, context)


def render_template_string(source: str, **context: t.Any) -> str:
    """Render một template từ chuỗi nguồn đã cho với ngữ cảnh
    đã cho.

    :param source: Mã nguồn của template để render.
    :param context: Các biến để làm cho có sẵn trong template.
    """
    app = current_app._get_current_object()
    template = app.jinja_env.from_string(source)
    return _render(app, template, context)


def _stream(
    app: Flask, template: Template, context: dict[str, t.Any]
) -> t.Iterator[str]:
    app.update_template_context(context)
    before_render_template.send(
        app, _async_wrapper=app.ensure_sync, template=template, context=context
    )

    def generate() -> t.Iterator[str]:
        yield from template.generate(context)
        template_rendered.send(
            app, _async_wrapper=app.ensure_sync, template=template, context=context
        )

    return stream_with_context(generate())


def stream_template(
    template_name_or_list: str | Template | list[str | Template],
    **context: t.Any,
) -> t.Iterator[str]:
    """Render một template theo tên với ngữ cảnh đã cho dưới dạng một luồng.
    Điều này trả về một iterator của các chuỗi, có thể được sử dụng như một
    phản hồi streaming từ một view.

    :param template_name_or_list: Tên của template để render. Nếu
        một danh sách được đưa ra, tên đầu tiên tồn tại sẽ được render.
    :param context: Các biến để làm cho có sẵn trong template.

    .. versionadded:: 2.2
    """
    app = current_app._get_current_object()
    template = app.jinja_env.get_or_select_template(template_name_or_list)
    return _stream(app, template, context)


def stream_template_string(source: str, **context: t.Any) -> t.Iterator[str]:
    """Render một template từ chuỗi nguồn đã cho với ngữ cảnh
    đã cho dưới dạng một luồng. Điều này trả về một iterator của các chuỗi, có thể
    được sử dụng như một phản hồi streaming từ một view.

    :param source: Mã nguồn của template để render.
    :param context: Các biến để làm cho có sẵn trong template.

    .. versionadded:: 2.2
    """
    app = current_app._get_current_object()
    template = app.jinja_env.from_string(source)
    return _stream(app, template, context)
