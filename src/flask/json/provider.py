from __future__ import annotations

import dataclasses
import decimal
import json
import typing as t
import uuid
import weakref
from datetime import date

from werkzeug.http import http_date

if t.TYPE_CHECKING:  # pragma: no cover
    from werkzeug.sansio.response import Response

    from ..sansio.app import App


class JSONProvider:
    """Một tập hợp các hoạt động JSON tiêu chuẩn cho một ứng dụng. Các lớp con
    của lớp này có thể được sử dụng để tùy chỉnh hành vi JSON hoặc sử dụng các
    thư viện JSON khác nhau.

    Để triển khai một provider cho một thư viện cụ thể, hãy tạo lớp con của lớp cơ sở
    này và triển khai ít nhất :meth:`dumps` và :meth:`loads`. Tất cả
    các phương thức khác đều có triển khai mặc định.

    Để sử dụng một provider khác, hoặc tạo lớp con ``Flask`` và đặt
    :attr:`~flask.Flask.json_provider_class` thành một lớp provider, hoặc đặt
    :attr:`app.json <flask.Flask.json>` thành một thể hiện của lớp đó.

    :param app: Một thể hiện của ứng dụng. Điều này sẽ được lưu trữ dưới dạng
        :class:`weakref.proxy` trên thuộc tính :attr:`_app`.

    .. versionadded:: 2.2
    """

    def __init__(self, app: App) -> None:
        self._app: App = weakref.proxy(app)

    def dumps(self, obj: t.Any, **kwargs: t.Any) -> str:
        """Tuần tự hóa dữ liệu thành JSON.

        :param obj: Dữ liệu để tuần tự hóa.
        :param kwargs: Có thể được truyền cho thư viện JSON bên dưới.
        """
        raise NotImplementedError

    def dump(self, obj: t.Any, fp: t.IO[str], **kwargs: t.Any) -> None:
        """Tuần tự hóa dữ liệu thành JSON và ghi vào một tệp.

        :param obj: Dữ liệu để tuần tự hóa.
        :param fp: Một tệp được mở để ghi văn bản. Nên sử dụng mã hóa UTF-8
            để là JSON hợp lệ.
        :param kwargs: Có thể được truyền cho thư viện JSON bên dưới.
        """
        fp.write(self.dumps(obj, **kwargs))

    def loads(self, s: str | bytes, **kwargs: t.Any) -> t.Any:
        """Giải tuần tự hóa dữ liệu thành JSON.

        :param s: Văn bản hoặc byte UTF-8.
        :param kwargs: Có thể được truyền cho thư viện JSON bên dưới.
        """
        raise NotImplementedError

    def load(self, fp: t.IO[t.AnyStr], **kwargs: t.Any) -> t.Any:
        """Giải tuần tự hóa dữ liệu thành JSON đọc từ một tệp.

        :param fp: Một tệp được mở để đọc văn bản hoặc byte UTF-8.
        :param kwargs: Có thể được truyền cho thư viện JSON bên dưới.
        """
        return self.loads(fp.read(), **kwargs)

    def _prepare_response_obj(
        self, args: tuple[t.Any, ...], kwargs: dict[str, t.Any]
    ) -> t.Any:
        if args and kwargs:
            raise TypeError("app.json.response() takes either args or kwargs, not both")

        if not args and not kwargs:
            return None

        if len(args) == 1:
            return args[0]

        return args or kwargs

    def response(self, *args: t.Any, **kwargs: t.Any) -> Response:
        """Tuần tự hóa các đối số đã cho thành JSON, và trả về một
        đối tượng :class:`~flask.Response` với mimetype ``application/json``.

        Hàm :func:`~flask.json.jsonify` gọi phương thức này cho
        ứng dụng hiện tại.

        Hoặc đối số vị trí hoặc đối số từ khóa có thể được đưa ra, không phải cả hai.
        Nếu không có đối số nào được đưa ra, ``None`` được tuần tự hóa.

        :param args: Một giá trị duy nhất để tuần tự hóa, hoặc nhiều giá trị để
            xử lý như một danh sách để tuần tự hóa.
        :param kwargs: Xử lý như một dict để tuần tự hóa.
        """
        obj = self._prepare_response_obj(args, kwargs)
        return self._app.response_class(self.dumps(obj), mimetype="application/json")


def _default(o: t.Any) -> t.Any:
    if isinstance(o, date):
        return http_date(o)

    if isinstance(o, (decimal.Decimal, uuid.UUID)):
        return str(o)

    if dataclasses and dataclasses.is_dataclass(o):
        return dataclasses.asdict(o)  # type: ignore[arg-type]

    if hasattr(o, "__html__"):
        return str(o.__html__())

    raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")


class DefaultJSONProvider(JSONProvider):
    """Cung cấp các hoạt động JSON sử dụng thư viện :mod:`json` tích hợp sẵn
    của Python. Tuần tự hóa các loại dữ liệu bổ sung sau:

    -   :class:`datetime.datetime` và :class:`datetime.date` được
        tuần tự hóa thành chuỗi :rfc:`822`. Điều này giống với định dạng
        ngày HTTP.
    -   :class:`uuid.UUID` được tuần tự hóa thành một chuỗi.
    -   :class:`dataclasses.dataclass` được truyền cho
        :func:`dataclasses.asdict`.
    -   :class:`~markupsafe.Markup` (hoặc bất kỳ đối tượng nào có phương thức ``__html__``)
        sẽ gọi phương thức ``__html__`` để lấy một chuỗi.
    """

    default: t.Callable[[t.Any], t.Any] = staticmethod(_default)
    """Áp dụng hàm này cho bất kỳ đối tượng nào mà :meth:`json.dumps` không
    biết cách tuần tự hóa. Nó sẽ trả về một loại JSON hợp lệ hoặc
    nêu ra một ``TypeError``.
    """

    ensure_ascii = True
    """Thay thế các ký tự không phải ASCII bằng các chuỗi thoát. Điều này có thể
    tương thích hơn với một số client, nhưng có thể bị vô hiệu hóa để có hiệu suất
    và kích thước tốt hơn.
    """

    sort_keys = True
    """Sắp xếp các khóa trong bất kỳ dict nào được tuần tự hóa. Điều này có thể hữu ích cho
    một số tình huống lưu trữ đệm, nhưng có thể bị vô hiệu hóa để có hiệu suất tốt hơn.
    Khi được bật, tất cả các khóa phải là chuỗi, chúng không được chuyển đổi
    trước khi sắp xếp.
    """

    compact: bool | None = None
    """Nếu ``True``, hoặc ``None`` ngoài chế độ debug, đầu ra :meth:`response`
    sẽ không thêm thụt đầu dòng, dòng mới hoặc khoảng trắng. Nếu ``False``,
    hoặc ``None`` trong chế độ debug, nó sẽ sử dụng một biểu diễn không gọn.
    """

    mimetype = "application/json"
    """Mimetype được đặt trong :meth:`response`."""

    def dumps(self, obj: t.Any, **kwargs: t.Any) -> str:
        """Tuần tự hóa dữ liệu thành JSON thành một chuỗi.

        Các đối số từ khóa được truyền cho :func:`json.dumps`. Đặt một số
        mặc định tham số từ các thuộc tính :attr:`default`,
        :attr:`ensure_ascii`, và :attr:`sort_keys`.

        :param obj: Dữ liệu để tuần tự hóa.
        :param kwargs: Được truyền cho :func:`json.dumps`.
        """
        kwargs.setdefault("default", self.default)
        kwargs.setdefault("ensure_ascii", self.ensure_ascii)
        kwargs.setdefault("sort_keys", self.sort_keys)
        return json.dumps(obj, **kwargs)

    def loads(self, s: str | bytes, **kwargs: t.Any) -> t.Any:
        """Giải tuần tự hóa dữ liệu thành JSON từ một chuỗi hoặc byte.

        :param s: Văn bản hoặc byte UTF-8.
        :param kwargs: Được truyền cho :func:`json.loads`.
        """
        return json.loads(s, **kwargs)

    def response(self, *args: t.Any, **kwargs: t.Any) -> Response:
        """Tuần tự hóa các đối số đã cho thành JSON, và trả về một
        đối tượng :class:`~flask.Response` với nó. Mimetype phản hồi
        sẽ là "application/json" và có thể được thay đổi bằng
        :attr:`mimetype`.

        Nếu :attr:`compact` là ``False`` hoặc chế độ debug được bật,
        đầu ra sẽ được định dạng để dễ đọc hơn.

        Hoặc đối số vị trí hoặc đối số từ khóa có thể được đưa ra, không phải cả hai.
        Nếu không có đối số nào được đưa ra, ``None`` được tuần tự hóa.

        :param args: Một giá trị duy nhất để tuần tự hóa, hoặc nhiều giá trị để
            xử lý như một danh sách để tuần tự hóa.
        :param kwargs: Xử lý như một dict để tuần tự hóa.
        """
        obj = self._prepare_response_obj(args, kwargs)
        dump_args: dict[str, t.Any] = {}

        if (self.compact is None and self._app.debug) or self.compact is False:
            dump_args.setdefault("indent", 2)
        else:
            dump_args.setdefault("separators", (",", ":"))

        return self._app.response_class(
            f"{self.dumps(obj, **dump_args)}\n", mimetype=self.mimetype
        )
