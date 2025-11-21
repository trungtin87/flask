from __future__ import annotations

import typing as t

from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Request as RequestBase
from werkzeug.wrappers import Response as ResponseBase

from . import json
from .globals import current_app
from .helpers import _split_blueprint_path

if t.TYPE_CHECKING:  # pragma: no cover
    from werkzeug.routing import Rule


class Request(RequestBase):
    """Đối tượng request được sử dụng theo mặc định trong Flask. Ghi nhớ
    endpoint đã khớp và các đối số view.

    Nó là cái kết thúc như là :class:`~flask.request`. Nếu bạn muốn thay thế
    đối tượng request được sử dụng, bạn có thể phân lớp cái này và thiết lập
    :attr:`~flask.Flask.request_class` thành lớp con của bạn.

    Đối tượng request là một lớp con của :class:`~werkzeug.wrappers.Request` và
    cung cấp tất cả các thuộc tính mà Werkzeug định nghĩa cộng với một vài thuộc tính cụ thể
    của Flask.
    """

    json_module: t.Any = json

    #: Quy tắc URL nội bộ đã khớp với request. Điều này có thể
    #: hữu ích để kiểm tra những phương thức nào được phép cho URL từ
    #: một handler before/after (``request.url_rule.methods``) v.v.
    #: Mặc dù nếu phương thức của request không hợp lệ cho quy tắc URL,
    #: danh sách hợp lệ có sẵn trong ``routing_exception.valid_methods``
    #: thay thế (một thuộc tính của ngoại lệ Werkzeug
    #: :exc:`~werkzeug.exceptions.MethodNotAllowed`)
    #: bởi vì request chưa bao giờ được ràng buộc nội bộ.
    #:
    #: .. versionadded:: 0.6
    url_rule: Rule | None = None

    #: Một dict các đối số view đã khớp với request. Nếu một ngoại lệ
    #: xảy ra khi khớp, cái này sẽ là ``None``.
    view_args: dict[str, t.Any] | None = None

    #: Nếu khớp URL thất bại, đây là ngoại lệ sẽ được
    #: ném ra / đã được ném ra như một phần của xử lý request. Đây
    #: thường là một ngoại lệ :exc:`~werkzeug.exceptions.NotFound` hoặc
    #: một cái gì đó tương tự.
    routing_exception: HTTPException | None = None

    _max_content_length: int | None = None
    _max_form_memory_size: int | None = None
    _max_form_parts: int | None = None

    @property
    def max_content_length(self) -> int | None:
        """Số byte tối đa sẽ được đọc trong request này. Nếu
        giới hạn này bị vượt quá, một lỗi 413 :exc:`~werkzeug.exceptions.RequestEntityTooLarge`
        được ném ra. Nếu nó được thiết lập thành ``None``, không có giới hạn nào được thực thi ở cấp độ
        ứng dụng Flask. Tuy nhiên, nếu nó là ``None`` và request không có
        header ``Content-Length`` và máy chủ WSGI không chỉ ra rằng
        nó chấm dứt luồng, thì không có dữ liệu nào được đọc để tránh một luồng
        vô hạn.

        Mỗi request mặc định theo cấu hình :data:`MAX_CONTENT_LENGTH`, cái mà
        mặc định là ``None``. Nó có thể được thiết lập trên một ``request`` cụ thể để áp dụng
        giới hạn cho view cụ thể đó. Điều này nên được thiết lập một cách thích hợp dựa trên
        nhu cầu cụ thể của ứng dụng hoặc view.

        .. versionchanged:: 3.1
            Cái này có thể được thiết lập theo mỗi request.

        .. versionchanged:: 0.6
            Cái này có thể cấu hình thông qua cấu hình Flask.
        """
        if self._max_content_length is not None:
            return self._max_content_length

        if not current_app:
            return super().max_content_length

        return current_app.config["MAX_CONTENT_LENGTH"]  # type: ignore[no-any-return]

    @max_content_length.setter
    def max_content_length(self, value: int | None) -> None:
        self._max_content_length = value

    @property
    def max_form_memory_size(self) -> int | None:
        """Kích thước tối đa tính bằng byte mà bất kỳ trường form không phải tệp nào có thể có trong một
        body ``multipart/form-data``. Nếu giới hạn này bị vượt quá, một lỗi 413
        :exc:`~werkzeug.exceptions.RequestEntityTooLarge` được ném ra. Nếu nó
        được thiết lập thành ``None``, không có giới hạn nào được thực thi ở cấp độ ứng dụng Flask.

        Mỗi request mặc định theo cấu hình :data:`MAX_FORM_MEMORY_SIZE`, cái mà
        mặc định là ``500_000``. Nó có thể được thiết lập trên một ``request`` cụ thể để
        áp dụng giới hạn cho view cụ thể đó. Điều này nên được thiết lập một cách thích hợp
        dựa trên nhu cầu cụ thể của ứng dụng hoặc view.

        .. versionchanged:: 3.1
            Cái này có thể cấu hình thông qua cấu hình Flask.
        """
        if self._max_form_memory_size is not None:
            return self._max_form_memory_size

        if not current_app:
            return super().max_form_memory_size

        return current_app.config["MAX_FORM_MEMORY_SIZE"]  # type: ignore[no-any-return]

    @max_form_memory_size.setter
    def max_form_memory_size(self, value: int | None) -> None:
        self._max_form_memory_size = value

    @property  # type: ignore[override]
    def max_form_parts(self) -> int | None:
        """Số lượng trường tối đa có thể có trong một
        body ``multipart/form-data``. Nếu giới hạn này bị vượt quá, một lỗi 413
        :exc:`~werkzeug.exceptions.RequestEntityTooLarge` được ném ra. Nếu nó
        được thiết lập thành ``None``, không có giới hạn nào được thực thi ở cấp độ ứng dụng Flask.

        Mỗi request mặc định theo cấu hình :data:`MAX_FORM_PARTS`, cái mà
        mặc định là ``1_000``. Nó có thể được thiết lập trên một ``request`` cụ thể để áp dụng
        giới hạn cho view cụ thể đó. Điều này nên được thiết lập một cách thích hợp dựa trên
        nhu cầu cụ thể của ứng dụng hoặc view.

        .. versionchanged:: 3.1
            Cái này có thể cấu hình thông qua cấu hình Flask.
        """
        if self._max_form_parts is not None:
            return self._max_form_parts

        if not current_app:
            return super().max_form_parts

        return current_app.config["MAX_FORM_PARTS"]  # type: ignore[no-any-return]

    @max_form_parts.setter
    def max_form_parts(self, value: int | None) -> None:
        self._max_form_parts = value

    @property
    def endpoint(self) -> str | None:
        """Endpoint đã khớp với URL request.

        Cái này sẽ là ``None`` nếu khớp thất bại hoặc chưa được
        thực hiện.

        Cái này kết hợp với :attr:`view_args` có thể được sử dụng để
        tái tạo cùng một URL hoặc một URL đã sửa đổi.
        """
        if self.url_rule is not None:
            return self.url_rule.endpoint  # type: ignore[no-any-return]

        return None

    @property
    def blueprint(self) -> str | None:
        """Tên đã đăng ký của blueprint hiện tại.

        Cái này sẽ là ``None`` nếu endpoint không phải là một phần của một
        blueprint, hoặc nếu khớp URL thất bại hoặc chưa được thực hiện.

        Cái này không nhất thiết phải khớp với tên mà blueprint được
        tạo ra. Nó có thể đã được lồng nhau, hoặc được đăng ký với một
        tên khác.
        """
        endpoint = self.endpoint

        if endpoint is not None and "." in endpoint:
            return endpoint.rpartition(".")[0]

        return None

    @property
    def blueprints(self) -> list[str]:
        """Các tên đã đăng ký của blueprint hiện tại lên trên qua
        các blueprint cha.

        Cái này sẽ là một danh sách trống nếu không có blueprint hiện tại, hoặc
        nếu khớp URL thất bại.

        .. versionadded:: 2.0.1
        """
        name = self.blueprint

        if name is None:
            return []

        return _split_blueprint_path(name)

    def _load_form_data(self) -> None:
        super()._load_form_data()

        # Trong chế độ debug chúng tôi đang thay thế multidict files bằng một
        # lớp con ad-hoc ném ra một lỗi khác cho các lỗi khóa.
        if (
            current_app
            and current_app.debug
            and self.mimetype != "multipart/form-data"
            and not self.files
        ):
            from .debughelpers import attach_enctype_error_multidict

            attach_enctype_error_multidict(self)

    def on_json_loading_failed(self, e: ValueError | None) -> t.Any:
        try:
            return super().on_json_loading_failed(e)
        except BadRequest as ebr:
            if current_app and current_app.debug:
                raise

            raise BadRequest() from ebr


class Response(ResponseBase):
    """Đối tượng phản hồi được sử dụng theo mặc định trong Flask. Hoạt động giống như
    đối tượng phản hồi từ Werkzeug nhưng được thiết lập để có mimetype HTML theo
    mặc định. Khá thường xuyên bạn không phải tự tạo đối tượng này vì
    :meth:`~flask.Flask.make_response` sẽ lo việc đó cho bạn.

    Nếu bạn muốn thay thế đối tượng phản hồi được sử dụng, bạn có thể phân lớp cái này và
    thiết lập :attr:`~flask.Flask.response_class` thành lớp con của bạn.

    .. versionchanged:: 1.0
        Hỗ trợ JSON được thêm vào phản hồi, giống như request. Điều này hữu ích
        khi kiểm thử để lấy dữ liệu phản hồi của test client dưới dạng JSON.

    .. versionchanged:: 1.0

        Đã thêm :attr:`max_cookie_size`.
    """

    default_mimetype: str | None = "text/html"

    json_module = json

    autocorrect_location_header = False

    @property
    def max_cookie_size(self) -> int:  # type: ignore
        """View chỉ đọc của khóa cấu hình :data:`MAX_COOKIE_SIZE`.

        Xem :attr:`~werkzeug.wrappers.Response.max_cookie_size` trong
        tài liệu của Werkzeug.
        """
        if current_app:
            return current_app.config["MAX_COOKIE_SIZE"]  # type: ignore[no-any-return]

        # trả về mặc định của Werkzeug khi không ở trong một ngữ cảnh ứng dụng
        return super().max_cookie_size
