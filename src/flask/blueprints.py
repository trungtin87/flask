from __future__ import annotations

import os
import typing as t
from datetime import timedelta

from .cli import AppGroup
from .globals import current_app
from .helpers import send_from_directory
from .sansio.blueprints import Blueprint as SansioBlueprint
from .sansio.blueprints import BlueprintSetupState as BlueprintSetupState  # noqa
from .sansio.scaffold import _sentinel

if t.TYPE_CHECKING:  # pragma: no cover
    from .wrappers import Response


class Blueprint(SansioBlueprint):
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
        cli_group: str | None = _sentinel,  # type: ignore
    ) -> None:
        super().__init__(
            name,
            import_name,
            static_folder,
            static_url_path,
            template_folder,
            url_prefix,
            subdomain,
            url_defaults,
            root_path,
            cli_group,
        )

        #: Nhóm lệnh Click để đăng ký các lệnh CLI cho đối tượng
        #: này. Các lệnh có sẵn từ lệnh ``flask``
        #: sau khi ứng dụng đã được phát hiện và các blueprint đã
        #: được đăng ký.
        self.cli = AppGroup()

        # Đặt tên của nhóm Click trong trường hợp ai đó muốn thêm
        # các lệnh của ứng dụng vào một công cụ CLI khác.
        self.cli.name = self.name

    def get_send_file_max_age(self, filename: str | None) -> int | None:
        """Được sử dụng bởi :func:`send_file` để xác định giá trị cache ``max_age``
        cho một đường dẫn tệp nhất định nếu nó không được truyền.

        Theo mặc định, điều này trả về :data:`SEND_FILE_MAX_AGE_DEFAULT` từ
        cấu hình của :data:`~flask.current_app`. Điều này mặc định
        là ``None``, báo cho trình duyệt sử dụng các request có điều kiện
        thay vì cache theo thời gian, điều này thường thích hợp hơn.

        Lưu ý điều này là một bản sao của cùng một phương thức trong lớp
        Flask.

        .. versionchanged:: 2.0
            Cấu hình mặc định là ``None`` thay vì 12 giờ.

        .. versionadded:: 0.9
        """
        value = current_app.config["SEND_FILE_MAX_AGE_DEFAULT"]

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

        Lưu ý điều này là một bản sao của cùng một phương thức trong lớp
        Flask.

        .. versionadded:: 0.5

        """
        if not self.has_static_folder:
            raise RuntimeError("'static_folder' must be set to serve static_files.")

        # send_file chỉ biết gọi get_send_file_max_age trên ứng dụng,
        # gọi nó ở đây để nó cũng hoạt động cho các blueprint.
        max_age = self.get_send_file_max_age(filename)
        return send_from_directory(
            t.cast(str, self.static_folder), filename, max_age=max_age
        )

    def open_resource(
        self, resource: str, mode: str = "rb", encoding: str | None = "utf-8"
    ) -> t.IO[t.AnyStr]:
        """Mở một tệp tài nguyên tương đối với :attr:`root_path` để đọc.
        Tương đương tương đối với blueprint của phương thức :meth:`~.Flask.open_resource`
        của ứng dụng.

        :param resource: Đường dẫn đến tài nguyên tương đối với :attr:`root_path`.
        :param mode: Mở tệp trong chế độ này. Chỉ hỗ trợ đọc,
            các giá trị hợp lệ là ``"r"`` (hoặc ``"rt"``) và ``"rb"``.
        :param encoding: Mở tệp với mã hóa này khi mở trong chế độ
            văn bản. Điều này bị bỏ qua khi mở trong chế độ nhị phân.

        .. versionchanged:: 3.1
            Đã thêm tham số ``encoding``.
        """
        if mode not in {"r", "rt", "rb"}:
            raise ValueError("Resources can only be opened for reading.")

        path = os.path.join(self.root_path, resource)

        if mode == "rb":
            return open(path, mode)  # pyright: ignore

        return open(path, mode, encoding=encoding)
