from __future__ import annotations

import errno
import json
import os
import types
import typing as t

from werkzeug.utils import import_string

if t.TYPE_CHECKING:
    import typing_extensions as te

    from .sansio.app import App


T = t.TypeVar("T")


class ConfigAttribute(t.Generic[T]):
    """Làm cho một thuộc tính chuyển tiếp đến config"""

    def __init__(
        self, name: str, get_converter: t.Callable[[t.Any], T] | None = None
    ) -> None:
        self.__name__ = name
        self.get_converter = get_converter

    @t.overload
    def __get__(self, obj: None, owner: None) -> te.Self: ...

    @t.overload
    def __get__(self, obj: App, owner: type[App]) -> T: ...

    def __get__(self, obj: App | None, owner: type[App] | None = None) -> T | te.Self:
        if obj is None:
            return self

        rv = obj.config[self.__name__]

        if self.get_converter is not None:
            rv = self.get_converter(rv)

        return rv  # type: ignore[no-any-return]

    def __set__(self, obj: App, value: t.Any) -> None:
        obj.config[self.__name__] = value


class Config(dict):  # type: ignore[type-arg]
    """Hoạt động chính xác như một dict nhưng cung cấp các cách để điền nó từ các tệp
    hoặc các từ điển đặc biệt. Có hai mẫu phổ biến để điền
    config.

    Hoặc bạn có thể điền config từ một tệp config::

        app.config.from_pyfile('yourconfig.cfg')

    Hoặc thay vào đó bạn có thể định nghĩa các tùy chọn cấu hình trong
    module gọi :meth:`from_object` hoặc cung cấp một đường dẫn import đến
    một module nên được tải. Cũng có thể bảo nó
    sử dụng cùng một module và với điều đó cung cấp các giá trị cấu hình
    ngay trước khi gọi::

        DEBUG = True
        SECRET_KEY = 'development key'
        app.config.from_object(__name__)

    Trong cả hai trường hợp (tải từ bất kỳ tệp Python nào hoặc tải từ các module),
    chỉ các khóa viết hoa mới được thêm vào config. Điều này làm cho việc sử dụng
    các giá trị viết thường trong tệp config cho các giá trị tạm thời không được thêm
    vào config hoặc để định nghĩa các khóa config trong cùng một tệp thực hiện
    ứng dụng trở nên khả thi.

    Có lẽ cách thú vị nhất để tải các cấu hình là từ một
    biến môi trường trỏ đến một tệp::

        app.config.from_envvar('YOURAPPLICATION_SETTINGS')

    Trong trường hợp này trước khi khởi chạy ứng dụng bạn phải thiết lập biến
    môi trường này thành tệp bạn muốn sử dụng. Trên Linux và OS X
    sử dụng câu lệnh export::

        export YOURAPPLICATION_SETTINGS='/path/to/config/file'

    Trên windows sử dụng `set` thay thế.

    :param root_path: đường dẫn mà các tệp được đọc tương đối từ đó. Khi
                      đối tượng config được tạo bởi ứng dụng, đây là
                      :attr:`~flask.Flask.root_path` của ứng dụng.
    :param defaults: một từ điển tùy chọn của các giá trị mặc định
    """

    def __init__(
        self,
        root_path: str | os.PathLike[str],
        defaults: dict[str, t.Any] | None = None,
    ) -> None:
        super().__init__(defaults or {})
        self.root_path = root_path

    def from_envvar(self, variable_name: str, silent: bool = False) -> bool:
        """Tải một cấu hình từ một biến môi trường trỏ đến
        một tệp cấu hình. Đây về cơ bản chỉ là một lối tắt với các thông báo
        lỗi đẹp hơn cho dòng mã này::

            app.config.from_pyfile(os.environ['YOURAPPLICATION_SETTINGS'])

        :param variable_name: tên của biến môi trường
        :param silent: đặt thành ``True`` nếu bạn muốn thất bại im lặng cho các tệp
                       bị thiếu.
        :return: ``True`` nếu tệp được tải thành công.
        """
        rv = os.environ.get(variable_name)
        if not rv:
            if silent:
                return False
            raise RuntimeError(
                f"Biến môi trường {variable_name!r} không được thiết lập"
                " và do đó cấu hình không thể được tải. Thiết lập"
                " biến này và làm cho nó trỏ đến một tệp"
                " cấu hình"
            )
        return self.from_pyfile(rv, silent=silent)

    def from_prefixed_env(
        self, prefix: str = "FLASK", *, loads: t.Callable[[str], t.Any] = json.loads
    ) -> bool:
        """Tải bất kỳ biến môi trường nào bắt đầu bằng ``FLASK_``,
        bỏ tiền tố khỏi khóa env cho khóa config. Các giá trị
        được truyền qua một hàm tải để cố gắng chuyển đổi chúng
        thành các loại cụ thể hơn là chuỗi.

        Các khóa được tải theo thứ tự :func:`sorted`.

        Hàm tải mặc định cố gắng phân tích các giá trị như bất kỳ
        loại JSON hợp lệ nào, bao gồm dict và list.

        Các mục cụ thể trong các dict lồng nhau có thể được thiết lập bằng cách phân tách các
        khóa bằng dấu gạch dưới kép (``__``). Nếu một khóa trung gian
        không tồn tại, nó sẽ được khởi tạo thành một dict trống.

        :param prefix: Tải các biến môi trường bắt đầu bằng tiền tố này,
            được phân tách bằng một dấu gạch dưới (``_``).
        :param loads: Truyền mỗi giá trị chuỗi cho hàm này và sử dụng
            giá trị trả về làm giá trị config. Nếu bất kỳ lỗi nào được
            ném ra, nó sẽ bị bỏ qua và giá trị vẫn là một chuỗi. Mặc định
            là :func:`json.loads`.

        .. versionadded:: 2.1
        """
        prefix = f"{prefix}_"

        for key in sorted(os.environ):
            if not key.startswith(prefix):
                continue

            value = os.environ[key]
            key = key.removeprefix(prefix)

            try:
                value = loads(value)
            except Exception:
                # Giữ giá trị là một chuỗi nếu tải thất bại.
                pass

            if "__" not in key:
                # Một khóa không lồng nhau, thiết lập trực tiếp.
                self[key] = value
                continue

            # Duyệt qua các từ điển lồng nhau với các khóa được phân tách bằng "__".
            current = self
            *parts, tail = key.split("__")

            for part in parts:
                # Nếu một dict trung gian không tồn tại, tạo nó.
                if part not in current:
                    current[part] = {}

                current = current[part]

            current[tail] = value

        return True

    def from_pyfile(
        self, filename: str | os.PathLike[str], silent: bool = False
    ) -> bool:
        """Cập nhật các giá trị trong config từ một tệp Python. Hàm này
        hoạt động như thể tệp đã được import làm module với
        hàm :meth:`from_object`.

        :param filename: tên tệp của config. Đây có thể là một
                         tên tệp tuyệt đối hoặc một tên tệp tương đối với
                         đường dẫn gốc.
        :param silent: đặt thành ``True`` nếu bạn muốn thất bại im lặng cho các tệp
                       bị thiếu.
        :return: ``True`` nếu tệp được tải thành công.

        .. versionadded:: 0.7
           tham số `silent`.
        """
        filename = os.path.join(self.root_path, filename)
        d = types.ModuleType("config")
        d.__file__ = filename
        try:
            with open(filename, mode="rb") as config_file:
                exec(compile(config_file.read(), filename, "exec"), d.__dict__)
        except OSError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR, errno.ENOTDIR):
                return False
            e.strerror = f"Không thể tải tệp cấu hình ({e.strerror})"
            raise
        self.from_object(d)
        return True

    def from_object(self, obj: object | str) -> None:
        """Cập nhật các giá trị từ đối tượng đã cho. Một đối tượng có thể thuộc một
        trong hai loại sau:

        -   một chuỗi: trong trường hợp này đối tượng với tên đó sẽ được import
        -   một tham chiếu đối tượng thực tế: đối tượng đó được sử dụng trực tiếp

        Các đối tượng thường là các module hoặc lớp. :meth:`from_object`
        chỉ tải các thuộc tính viết hoa của module/lớp. Một đối tượng ``dict``
        sẽ không hoạt động với :meth:`from_object` vì các khóa của một
        ``dict`` không phải là thuộc tính của lớp ``dict``.

        Ví dụ về cấu hình dựa trên module::

            app.config.from_object('yourapplication.default_config')
            from yourapplication import default_config
            app.config.from_object(default_config)

        Không có gì được thực hiện đối với đối tượng trước khi tải. Nếu đối tượng là một
        lớp và có các thuộc tính ``@property``, nó cần được
        khởi tạo trước khi được truyền cho phương thức này.

        Bạn không nên sử dụng hàm này để tải cấu hình thực tế mà
        thay vào đó là các mặc định cấu hình. Cấu hình thực tế nên được tải
        với :meth:`from_pyfile` và lý tưởng nhất là từ một vị trí không nằm trong
        gói vì gói có thể được cài đặt trên toàn hệ thống.

        Xem :ref:`config-dev-prod` cho một ví dụ về cấu hình dựa trên lớp
        sử dụng :meth:`from_object`.

        :param obj: một tên import hoặc đối tượng
        """
        if isinstance(obj, str):
            obj = import_string(obj)
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def from_file(
        self,
        filename: str | os.PathLike[str],
        load: t.Callable[[t.IO[t.Any]], t.Mapping[str, t.Any]],
        silent: bool = False,
        text: bool = True,
    ) -> bool:
        """Cập nhật các giá trị trong config từ một tệp được tải
        sử dụng tham số ``load``. Dữ liệu đã tải được truyền cho
        phương thức :meth:`from_mapping`.

        .. code-block:: python

            import json
            app.config.from_file("config.json", load=json.load)

            import tomllib
            app.config.from_file("config.toml", load=tomllib.load, text=False)

        :param filename: Đường dẫn đến tệp dữ liệu. Đây có thể là một
            đường dẫn tuyệt đối hoặc tương đối với đường dẫn gốc config.
        :param load: Một callable nhận một file handle và trả về một
            mapping của dữ liệu đã tải từ tệp.
        :type load: ``Callable[[Reader], Mapping]`` nơi ``Reader``
            thực hiện một phương thức ``read``.
        :param silent: Bỏ qua tệp nếu nó không tồn tại.
        :param text: Mở tệp trong chế độ văn bản hoặc nhị phân.
        :return: ``True`` nếu tệp được tải thành công.

        .. versionchanged:: 2.3
            Tham số ``text`` đã được thêm vào.

        .. versionadded:: 2.0
        """
        filename = os.path.join(self.root_path, filename)

        try:
            with open(filename, "r" if text else "rb") as f:
                obj = load(f)
        except OSError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False

            e.strerror = f"Không thể tải tệp cấu hình ({e.strerror})"
            raise

        return self.from_mapping(obj)

    def from_mapping(
        self, mapping: t.Mapping[str, t.Any] | None = None, **kwargs: t.Any
    ) -> bool:
        """Cập nhật config giống như :meth:`update` bỏ qua các mục với
        các khóa không viết hoa.

        :return: Luôn trả về ``True``.

        .. versionadded:: 0.11
        """
        mappings: dict[str, t.Any] = {}
        if mapping is not None:
            mappings.update(mapping)
        mappings.update(kwargs)
        for key, value in mappings.items():
            if key.isupper():
                self[key] = value
        return True

    def get_namespace(
        self, namespace: str, lowercase: bool = True, trim_namespace: bool = True
    ) -> dict[str, t.Any]:
        """Trả về một từ điển chứa một tập hợp con các tùy chọn cấu hình
        khớp với namespace/prefix đã chỉ định. Ví dụ sử dụng::

            app.config['IMAGE_STORE_TYPE'] = 'fs'
            app.config['IMAGE_STORE_PATH'] = '/var/app/images'
            app.config['IMAGE_STORE_BASE_URL'] = 'http://img.website.com'
            image_store_config = app.config.get_namespace('IMAGE_STORE_')

        Từ điển kết quả `image_store_config` sẽ trông giống như::

            {
                'type': 'fs',
                'path': '/var/app/images',
                'base_url': 'http://img.website.com'
            }

        Điều này thường hữu ích khi các tùy chọn cấu hình ánh xạ trực tiếp đến
        các đối số từ khóa trong các hàm hoặc hàm tạo lớp.

        :param namespace: một namespace cấu hình
        :param lowercase: một cờ chỉ ra nếu các khóa của từ điển kết quả
                          nên được viết thường
        :param trim_namespace: một cờ chỉ ra nếu các khóa của từ điển kết quả
                          không nên bao gồm namespace

        .. versionadded:: 0.11
        """
        rv = {}
        for k, v in self.items():
            if not k.startswith(namespace):
                continue
            if trim_namespace:
                key = k[len(namespace) :]
            else:
                key = k
            if lowercase:
                key = key.lower()
            rv[key] = v
        return rv

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {dict.__repr__(self)}>"
