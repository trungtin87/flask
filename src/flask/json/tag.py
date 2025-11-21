"""
Tagged JSON
~~~~~~~~~~~

Một biểu diễn nhỏ gọn để tuần tự hóa không mất dữ liệu cho các loại JSON
không chuẩn. :class:`~flask.sessions.SecureCookieSessionInterface` sử dụng
điều này để tuần tự hóa dữ liệu phiên, nhưng nó có thể hữu ích ở những nơi khác.
Nó có thể được mở rộng để hỗ trợ các loại khác.

.. autoclass:: TaggedJSONSerializer
    :members:

.. autoclass:: JSONTag
    :members:

Hãy xem một ví dụ thêm hỗ trợ cho :class:`~collections.OrderedDict`.
Dict không có thứ tự trong JSON, vì vậy để xử lý điều này, chúng ta sẽ
dump các mục dưới dạng danh sách các cặp ``[key, value]``. Tạo lớp con
:class:`JSONTag` và cung cấp cho nó khóa mới ``' od'`` để xác định loại.
Bộ tuần tự hóa phiên xử lý dict trước, vì vậy hãy chèn tag mới vào đầu
thứ tự vì ``OrderedDict`` phải được xử lý trước ``dict``.

.. code-block:: python

    from flask.json.tag import JSONTag

    class TagOrderedDict(JSONTag):
        __slots__ = ('serializer',)
        key = ' od'

        def check(self, value):
            return isinstance(value, OrderedDict)

        def to_json(self, value):
            return [[k, self.serializer.tag(v)] for k, v in iteritems(value)]

        def to_python(self, value):
            return OrderedDict(value)

    app.session_interface.serializer.register(TagOrderedDict, index=0)
"""

from __future__ import annotations

import typing as t  # Import module typing để hỗ trợ gợi ý kiểu dữ liệu (type hinting)
from base64 import b64decode  # Hàm giải mã dữ liệu base64
from base64 import b64encode  # Hàm mã hóa dữ liệu sang base64
from datetime import datetime  # Lớp datetime để xử lý ngày và giờ
from uuid import UUID  # Lớp UUID để xử lý các định danh duy nhất toàn cầu

from markupsafe import Markup  # Lớp Markup để đánh dấu chuỗi an toàn cho HTML
from werkzeug.http import http_date  # Hàm định dạng ngày tháng theo chuẩn HTTP
from werkzeug.http import parse_date  # Hàm phân tích chuỗi ngày tháng HTTP

from ..json import dumps  # Hàm chuyển đổi đối tượng Python sang chuỗi JSON
from ..json import loads  # Hàm chuyển đổi chuỗi JSON sang đối tượng Python


class JSONTag:
    """Lớp cơ sở để định nghĩa các tag loại cho :class:`TaggedJSONSerializer`."""

    __slots__ = ("serializer",)  # Giới hạn các thuộc tính của instance để tiết kiệm bộ nhớ

    #: Tag để đánh dấu đối tượng được tuần tự hóa. Nếu trống, tag này
    #: chỉ được sử dụng như một bước trung gian trong quá trình gắn thẻ.
    key: str = ""

    def __init__(self, serializer: TaggedJSONSerializer) -> None:
        """Tạo một tagger cho bộ tuần tự hóa đã cho."""
        self.serializer = serializer  # Lưu tham chiếu đến bộ tuần tự hóa

    def check(self, value: t.Any) -> bool:
        """Kiểm tra xem giá trị đã cho có nên được gắn thẻ bởi tag này hay không."""
        raise NotImplementedError  # Lớp con phải triển khai phương thức này

    def to_json(self, value: t.Any) -> t.Any:
        """Chuyển đổi đối tượng Python thành một đối tượng là loại JSON hợp lệ.
        Tag sẽ được thêm vào sau."""
        raise NotImplementedError  # Lớp con phải triển khai phương thức này

    def to_python(self, value: t.Any) -> t.Any:
        """Chuyển đổi biểu diễn JSON trở lại loại chính xác. Tag sẽ
        đã được gỡ bỏ."""
        raise NotImplementedError  # Lớp con phải triển khai phương thức này

    def tag(self, value: t.Any) -> dict[str, t.Any]:
        """Chuyển đổi giá trị thành loại JSON hợp lệ và thêm cấu trúc tag
        xung quanh nó."""
        return {self.key: self.to_json(value)}  # Trả về dict với key là tag và value là dữ liệu đã chuyển đổi


class TagDict(JSONTag):
    """Tag cho các dict 1 mục có khóa duy nhất khớp với một tag đã đăng ký.

    Bên trong, khóa dict được thêm hậu tố `__`, và hậu tố này bị xóa
    khi giải tuần tự hóa.
    """

    __slots__ = ()
    key = " di"  # Khóa tag cho dict đặc biệt này

    def check(self, value: t.Any) -> bool:
        # Kiểm tra nếu là dict, có 1 phần tử, và key của nó trùng với một tag đã đăng ký
        return (
            isinstance(value, dict)
            and len(value) == 1
            and next(iter(value)) in self.serializer.tags
        )

    def to_json(self, value: t.Any) -> t.Any:
        key = next(iter(value))  # Lấy key duy nhất
        # Thêm hậu tố "__" vào key để tránh xung đột với tag
        return {f"{key}__": self.serializer.tag(value[key])}

    def to_python(self, value: t.Any) -> t.Any:
        key = next(iter(value))  # Lấy key duy nhất
        # Xóa hậu tố "__" để khôi phục key gốc
        return {key[:-2]: value[key]}


class PassDict(JSONTag):
    __slots__ = ()

    def check(self, value: t.Any) -> bool:
        return isinstance(value, dict)  # Kiểm tra nếu là dict thường

    def to_json(self, value: t.Any) -> t.Any:
        # Các đối tượng JSON chỉ có thể có khóa chuỗi, vì vậy đừng bận tâm gắn thẻ
        # khóa ở đây.
        # Đệ quy tag các giá trị trong dict
        return {k: self.serializer.tag(v) for k, v in value.items()}

    tag = to_json  # Sử dụng to_json làm phương thức tag (không thêm wrapper key)


class TagTuple(JSONTag):
    __slots__ = ()
    key = " t"  # Khóa tag cho tuple

    def check(self, value: t.Any) -> bool:
        return isinstance(value, tuple)  # Kiểm tra nếu là tuple

    def to_json(self, value: t.Any) -> t.Any:
        # Chuyển tuple thành list và đệ quy tag các phần tử
        return [self.serializer.tag(item) for item in value]

    def to_python(self, value: t.Any) -> t.Any:
        return tuple(value)  # Chuyển list trở lại thành tuple


class PassList(JSONTag):
    __slots__ = ()

    def check(self, value: t.Any) -> bool:
        return isinstance(value, list)  # Kiểm tra nếu là list

    def to_json(self, value: t.Any) -> t.Any:
        # Đệ quy tag các phần tử trong list
        return [self.serializer.tag(item) for item in value]

    tag = to_json  # Sử dụng to_json làm phương thức tag (không thêm wrapper key)


class TagBytes(JSONTag):
    __slots__ = ()
    key = " b"  # Khóa tag cho bytes

    def check(self, value: t.Any) -> bool:
        return isinstance(value, bytes)  # Kiểm tra nếu là bytes

    def to_json(self, value: t.Any) -> t.Any:
        # Mã hóa bytes thành chuỗi base64 (ascii) để lưu trong JSON
        return b64encode(value).decode("ascii")

    def to_python(self, value: t.Any) -> t.Any:
        return b64decode(value)  # Giải mã chuỗi base64 trở lại thành bytes


class TagMarkup(JSONTag):
    """Tuần tự hóa bất kỳ thứ gì khớp với API :class:`~markupsafe.Markup` bằng cách
    có phương thức ``__html__`` thành kết quả của phương thức đó. Luôn
    giải tuần tự hóa thành một thể hiện của :class:`~markupsafe.Markup`."""

    __slots__ = ()
    key = " m"  # Khóa tag cho Markup

    def check(self, value: t.Any) -> bool:
        # Kiểm tra xem đối tượng có phương thức __html__ không
        return callable(getattr(value, "__html__", None))

    def to_json(self, value: t.Any) -> t.Any:
        return str(value.__html__())  # Lấy chuỗi HTML an toàn

    def to_python(self, value: t.Any) -> t.Any:
        return Markup(value)  # Tái tạo đối tượng Markup


class TagUUID(JSONTag):
    __slots__ = ()
    key = " u"  # Khóa tag cho UUID

    def check(self, value: t.Any) -> bool:
        return isinstance(value, UUID)  # Kiểm tra nếu là UUID

    def to_json(self, value: t.Any) -> t.Any:
        return value.hex  # Chuyển UUID thành chuỗi hex

    def to_python(self, value: t.Any) -> t.Any:
        return UUID(value)  # Tái tạo đối tượng UUID từ chuỗi hex


class TagDateTime(JSONTag):
    __slots__ = ()
    key = " d"  # Khóa tag cho datetime

    def check(self, value: t.Any) -> bool:
        return isinstance(value, datetime)  # Kiểm tra nếu là datetime

    def to_json(self, value: t.Any) -> t.Any:
        return http_date(value)  # Chuyển datetime thành chuỗi định dạng HTTP

    def to_python(self, value: t.Any) -> t.Any:
        return parse_date(value)  # Phân tích chuỗi ngày tháng trở lại datetime


class TaggedJSONSerializer:
    """Bộ tuần tự hóa sử dụng hệ thống tag để biểu diễn nhỏ gọn các đối tượng
    không phải là loại JSON. Được truyền dưới dạng bộ tuần tự hóa trung gian tới
    :class:`itsdangerous.Serializer`.

    Các loại bổ sung sau được hỗ trợ:

    * :class:`dict`
    * :class:`tuple`
    * :class:`bytes`
    * :class:`~markupsafe.Markup`
    * :class:`~uuid.UUID`
    * :class:`~datetime.datetime`
    """

    __slots__ = ("tags", "order")  # Giới hạn thuộc tính

    #: Các lớp tag để liên kết khi tạo bộ tuần tự hóa. Các tag khác có thể
    #: được thêm sau bằng cách sử dụng :meth:`~register`.
    default_tags = [
        TagDict,
        PassDict,
        TagTuple,
        PassList,
        TagBytes,
        TagMarkup,
        TagUUID,
        TagDateTime,
    ]

    def __init__(self) -> None:
        self.tags: dict[str, JSONTag] = {}  # Dict lưu trữ các tag đã đăng ký theo key
        self.order: list[JSONTag] = []  # List lưu trữ thứ tự ưu tiên của các tag

        for cls in self.default_tags:
            self.register(cls)  # Đăng ký các tag mặc định

    def register(
        self,
        tag_class: type[JSONTag],
        force: bool = False,
        index: int | None = None,
    ) -> None:
        """Đăng ký một tag mới với bộ tuần tự hóa này.

        :param tag_class: lớp tag để đăng ký. Sẽ được khởi tạo với
            thể hiện bộ tuần tự hóa này.
        :param force: ghi đè một tag hiện có. Nếu sai (mặc định), một
            :exc:`KeyError` sẽ được ném ra.
        :param index: chỉ mục để chèn tag mới vào thứ tự tag. Hữu ích khi
            tag mới là một trường hợp đặc biệt của một tag hiện có. Nếu ``None``
            (mặc định), tag được thêm vào cuối thứ tự.

        :raise KeyError: nếu khóa tag đã được đăng ký và ``force``
            không đúng.
        """
        tag = tag_class(self)  # Khởi tạo instance của tag
        key = tag.key  # Lấy key của tag

        if key:
            if not force and key in self.tags:
                raise KeyError(f"Tag '{key}' đã được đăng ký.")  # Lỗi nếu tag đã tồn tại và không force

            self.tags[key] = tag  # Lưu tag vào dict

        if index is None:
            self.order.append(tag)  # Thêm vào cuối danh sách
        else:
            self.order.insert(index, tag)  # Chèn vào vị trí chỉ định

    def tag(self, value: t.Any) -> t.Any:
        """Chuyển đổi một giá trị thành biểu diễn được gắn thẻ nếu cần thiết."""
        for tag in self.order:
            if tag.check(value):  # Kiểm tra xem tag có xử lý được giá trị này không
                return tag.tag(value)  # Thực hiện tag

        return value  # Trả về nguyên vẹn nếu không có tag nào xử lý

    def untag(self, value: dict[str, t.Any]) -> t.Any:
        """Chuyển đổi biểu diễn được gắn thẻ trở lại loại ban đầu."""
        if len(value) != 1:
            return value  # Nếu dict không có đúng 1 phần tử thì không phải là tag

        key = next(iter(value))  # Lấy key duy nhất

        if key not in self.tags:
            return value  # Nếu key không phải là tag đã đăng ký

        return self.tags[key].to_python(value[key])  # Giải mã giá trị bằng tag tương ứng

    def _untag_scan(self, value: t.Any) -> t.Any:
        if isinstance(value, dict):
            # untag từng mục đệ quy
            value = {k: self._untag_scan(v) for k, v in value.items()}
            # untag chính dict đó
            value = self.untag(value)
        elif isinstance(value, list):
            # untag từng mục đệ quy
            value = [self._untag_scan(item) for item in value]

        return value

    def dumps(self, value: t.Any) -> str:
        """Gắn thẻ giá trị và dump nó thành chuỗi JSON nhỏ gọn."""
        return dumps(self.tag(value), separators=(",", ":"))  # Sử dụng json.dumps với separators gọn nhất

    def loads(self, value: str) -> t.Any:
        """Tải dữ liệu từ chuỗi JSON và giải tuần tự hóa bất kỳ đối tượng được gắn thẻ nào."""
        return self._untag_scan(loads(value))  # Sử dụng json.loads và sau đó quét để untag
