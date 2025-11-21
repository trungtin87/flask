from __future__ import annotations

import typing as t

from jinja2.loaders import BaseLoader
from werkzeug.routing import RequestRedirect

from .blueprints import Blueprint
from .globals import _cv_app
from .sansio.app import App

if t.TYPE_CHECKING:
    from .sansio.scaffold import Scaffold
    from .wrappers import Request


class UnexpectedUnicodeError(AssertionError, UnicodeError):
    """Được ném ra ở những nơi chúng ta muốn báo cáo lỗi tốt hơn cho
    dữ liệu unicode hoặc nhị phân không mong muốn.
    """


class DebugFilesKeyError(KeyError, AssertionError):
    """Được ném ra từ request.files trong quá trình debug. Ý tưởng là nó có thể
    cung cấp một thông báo lỗi tốt hơn chỉ là một KeyError/BadRequest chung chung.
    """

    def __init__(self, request: Request, key: str) -> None:
        form_matches = request.form.getlist(key)
        buf = [
            f"Bạn đã cố gắng truy cập tệp {key!r} trong từ điển request.files"
            " nhưng nó không tồn tại. Mimetype cho"
            f" request là {request.mimetype!r} thay vì"
            " 'multipart/form-data' có nghĩa là không có nội dung tệp nào"
            " được truyền đi. Để sửa lỗi này bạn nên cung cấp"
            ' enctype="multipart/form-data" trong form của bạn.'
        ]
        if form_matches:
            names = ", ".join(repr(x) for x in form_matches)
            buf.append(
                "\n\nThay vào đó trình duyệt đã truyền một số tên tệp. "
                f"Cái này đã được gửi: {names}"
            )
        self.msg = "".join(buf)

    def __str__(self) -> str:
        return self.msg


class FormDataRoutingRedirect(AssertionError):
    """Ngoại lệ này được ném ra trong chế độ debug nếu một chuyển hướng routing
    sẽ khiến trình duyệt bỏ phương thức hoặc body. Điều này xảy ra
    khi phương thức không phải là GET, HEAD hoặc OPTIONS và mã trạng thái không phải là
    307 hoặc 308.
    """

    def __init__(self, request: Request) -> None:
        exc = request.routing_exception
        assert isinstance(exc, RequestRedirect)
        buf = [
            f"Một request đã được gửi đến '{request.url}', nhưng routing đã phát hành"
            f" một chuyển hướng đến URL chính tắc '{exc.new_url}'."
        ]

        if f"{request.base_url}/" == exc.new_url.partition("?")[0]:
            buf.append(
                " URL được định nghĩa với một dấu gạch chéo ở cuối. Flask"
                " sẽ chuyển hướng đến URL với một dấu gạch chéo ở cuối nếu nó"
                " được truy cập mà không có nó."
            )

        buf.append(
                " Gửi các request đến URL chính tắc, hoặc sử dụng 307 hoặc 308 cho"
                " các chuyển hướng routing. Nếu không, các trình duyệt sẽ bỏ dữ liệu"
                " form.\n\n"
                "Ngoại lệ này chỉ được ném ra trong chế độ debug."
            )
        super().__init__("".join(buf))


def attach_enctype_error_multidict(request: Request) -> None:
    """Vá ``request.files.__getitem__`` để ném ra một lỗi mô tả
    về ``enctype=multipart/form-data``.

    :param request: Request để vá.
    :meta private:
    """
    oldcls = request.files.__class__

    class newcls(oldcls):  # type: ignore[valid-type, misc]
        def __getitem__(self, key: str) -> t.Any:
            try:
                return super().__getitem__(key)
            except KeyError as e:
                if key not in request.form:
                    raise

                raise DebugFilesKeyError(request, key).with_traceback(
                    e.__traceback__
                ) from None

    newcls.__name__ = oldcls.__name__
    newcls.__module__ = oldcls.__module__
    request.files.__class__ = newcls


def _dump_loader_info(loader: BaseLoader) -> t.Iterator[str]:
    yield f"class: {type(loader).__module__}.{type(loader).__name__}"
    for key, value in sorted(loader.__dict__.items()):
        if key.startswith("_"):
            continue
        if isinstance(value, (tuple, list)):
            if not all(isinstance(x, str) for x in value):
                continue
            yield f"{key}:"
            for item in value:
                yield f"  - {item}"
            continue
        elif not isinstance(value, (str, int, float, bool)):
            continue
        yield f"{key}: {value!r}"


def explain_template_loading_attempts(
    app: App,
    template: str,
    attempts: list[
        tuple[
            BaseLoader,
            Scaffold,
            tuple[str, str | None, t.Callable[[], bool] | None] | None,
        ]
    ],
) -> None:
    """Điều này sẽ giúp các nhà phát triển hiểu cái gì đã thất bại"""
    info = [f"Đang định vị template {template!r}:"]
    total_found = 0
    blueprint = None

    if (ctx := _cv_app.get(None)) is not None and ctx.has_request:
        blueprint = ctx.request.blueprint

    for idx, (loader, srcobj, triple) in enumerate(attempts):
        if isinstance(srcobj, App):
            src_info = f"ứng dụng {srcobj.import_name!r}"
        elif isinstance(srcobj, Blueprint):
            src_info = f"blueprint {srcobj.name!r} ({srcobj.import_name})"
        else:
            src_info = repr(srcobj)

        info.append(f"{idx + 1:5}: đang thử loader của {src_info}")

        for line in _dump_loader_info(loader):
            info.append(f"       {line}")

        if triple is None:
            detail = "không khớp"
        else:
            detail = f"đã tìm thấy ({triple[1] or '<string>'!r})"
            total_found += 1
        info.append(f"       -> {detail}")

    seems_fishy = False
    if total_found == 0:
        info.append("Lỗi: không thể tìm thấy template.")
        seems_fishy = True
    elif total_found > 1:
        info.append("Cảnh báo: nhiều loader trả về một kết quả khớp cho template.")
        seems_fishy = True

    if blueprint is not None and seems_fishy:
        info.append(
            "  Template đã được tra cứu từ một endpoint thuộc về"
            f" blueprint {blueprint!r}."
        )
        info.append("  Có lẽ bạn đã không đặt một template trong đúng thư mục?")
        info.append("  Xem https://flask.palletsprojects.com/blueprints/#templates")

    app.logger.info("\n".join(info))
