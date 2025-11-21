from __future__ import annotations

import collections.abc as c
import hashlib
import typing as t
from collections.abc import MutableMapping
from datetime import datetime
from datetime import timezone

from itsdangerous import BadSignature
from itsdangerous import URLSafeTimedSerializer
from werkzeug.datastructures import CallbackDict

from .json.tag import TaggedJSONSerializer

if t.TYPE_CHECKING:  # pragma: no cover
    import typing_extensions as te

    from .app import Flask
    from .wrappers import Request
    from .wrappers import Response


class SessionMixin(MutableMapping[str, t.Any]):
    """Mở rộng một từ điển cơ bản với các thuộc tính session."""

    @property
    def permanent(self) -> bool:
        """Điều này phản ánh khóa ``'_permanent'`` trong dict."""
        return self.get("_permanent", False)

    @permanent.setter
    def permanent(self, value: bool) -> None:
        self["_permanent"] = bool(value)

    #: Một số triển khai có thể phát hiện xem một session có phải là mới
    #: được tạo hay không, nhưng điều đó không được đảm bảo. Sử dụng cẩn thận. Mixin
    # mặc định được hard-code là ``False``.
    new = False

    #: Một số triển khai có thể phát hiện các thay đổi đối với session và thiết lập
    #: điều này khi điều đó xảy ra. Mixin mặc định được hard code thành
    #: ``True``.
    modified = True

    #: Một số triển khai có thể phát hiện khi dữ liệu session được đọc hoặc
    #: ghi và thiết lập điều này khi điều đó xảy ra. Mixin mặc định được hard
    #: code thành ``True``.
    accessed = True


class SecureCookieSession(CallbackDict[str, t.Any], SessionMixin):
    """Lớp cơ sở cho các session dựa trên cookie đã ký.

    Backend session này sẽ thiết lập các thuộc tính :attr:`modified` và
    :attr:`accessed`. Nó không thể theo dõi một cách đáng tin cậy xem một
    session có phải là mới (so với trống) hay không, vì vậy :attr:`new` vẫn được hard code thành
    ``False``.
    """

    #: Khi dữ liệu bị thay đổi, cái này được đặt thành ``True``. Chỉ từ điển
    #: session chính nó được theo dõi; nếu session chứa dữ liệu có thể thay đổi
    #: (ví dụ một dict lồng nhau) thì cái này phải được đặt thành
    #: ``True`` thủ công khi sửa đổi dữ liệu đó. Cookie session
    #: sẽ chỉ được ghi vào phản hồi nếu cái này là ``True``.
    modified = False

    #: Khi dữ liệu được đọc hoặc ghi, cái này được đặt thành ``True``. Được sử dụng bởi
    # :class:`.SecureCookieSessionInterface` để thêm một header ``Vary: Cookie``,
    #: cho phép các proxy caching cache các trang khác nhau cho
    #: những người dùng khác nhau.
    accessed = False

    def __init__(
        self,
        initial: c.Mapping[str, t.Any] | c.Iterable[tuple[str, t.Any]] | None = None,
    ) -> None:
        def on_update(self: te.Self) -> None:
            self.modified = True
            self.accessed = True

        super().__init__(initial, on_update)

    def __getitem__(self, key: str) -> t.Any:
        self.accessed = True
        return super().__getitem__(key)

    def get(self, key: str, default: t.Any = None) -> t.Any:
        self.accessed = True
        return super().get(key, default)

    def setdefault(self, key: str, default: t.Any = None) -> t.Any:
        self.accessed = True
        return super().setdefault(key, default)


class NullSession(SecureCookieSession):
    """Lớp được sử dụng để tạo ra các thông báo lỗi đẹp hơn nếu các session không
    có sẵn. Sẽ vẫn cho phép truy cập chỉ đọc vào session trống
    nhưng thất bại khi thiết lập.
    """

    def _fail(self, *args: t.Any, **kwargs: t.Any) -> t.NoReturn:
        raise RuntimeError(
            "Session không có sẵn vì không có secret "
            "key nào được thiết lập. Thiết lập secret_key trên "
            "ứng dụng thành một cái gì đó duy nhất và bí mật."
        )

    __setitem__ = __delitem__ = clear = pop = popitem = update = setdefault = _fail  # noqa: B950
    del _fail


class SessionInterface:
    """Giao diện cơ bản bạn phải triển khai để thay thế
    giao diện session mặc định sử dụng triển khai securecookie của
    werkzeug. Các phương thức duy nhất bạn phải triển khai là
    :meth:`open_session` và :meth:`save_session`, những cái khác có
    các giá trị mặc định hữu ích mà bạn không cần phải thay đổi.

    Đối tượng session được trả về bởi phương thức :meth:`open_session` phải
    cung cấp một giao diện giống từ điển cộng với các thuộc tính và phương thức
    từ :class:`SessionMixin`. Chúng tôi khuyên bạn chỉ nên phân lớp một dict
    và thêm mixin đó::

        class Session(dict, SessionMixin):
            pass

    Nếu :meth:`open_session` trả về ``None`` Flask sẽ gọi vào
    :meth:`make_null_session` để tạo một session hoạt động như thay thế
    nếu hỗ trợ session không thể hoạt động vì một số yêu cầu không được
    đáp ứng. Lớp :class:`NullSession` mặc định được tạo ra
    sẽ phàn nàn rằng secret key không được thiết lập.

    Để thay thế giao diện session trên một ứng dụng tất cả những gì bạn phải làm
    là gán :attr:`flask.Flask.session_interface`::

        app = Flask(__name__)
        app.session_interface = MySessionInterface()

    Nhiều request với cùng một session có thể được gửi và xử lý
    đồng thời. Khi triển khai một giao diện session mới, hãy xem xét
    xem việc đọc hoặc ghi vào kho lưu trữ hỗ trợ có phải được đồng bộ hóa hay không.
    Không có đảm bảo về thứ tự mà session cho mỗi
    request được mở hoặc lưu, nó sẽ xảy ra theo thứ tự mà các request
    bắt đầu và kết thúc xử lý.

    .. versionadded:: 0.8
    """

    #: :meth:`make_null_session` sẽ tìm ở đây cho lớp nên
    #: được tạo khi một session null được yêu cầu. Tương tự phương thức
    #: :meth:`is_null_session` sẽ thực hiện một kiểm tra kiểu đối với
    #: loại này.
    null_session_class = NullSession

    #: Một cờ chỉ ra nếu giao diện session dựa trên pickle.
    #: Điều này có thể được sử dụng bởi các tiện ích mở rộng Flask để đưa ra quyết định liên quan
    #: đến cách xử lý đối tượng session.
    #:
    #: .. versionadded:: 0.10
    pickle_based = False

    def make_null_session(self, app: Flask) -> NullSession:
        """Tạo một session null hoạt động như một đối tượng thay thế nếu
        hỗ trợ session thực sự không thể được tải do một lỗi cấu hình.
        Điều này chủ yếu hỗ trợ trải nghiệm người dùng vì công việc của
        session null là vẫn hỗ trợ tra cứu mà không phàn nàn nhưng
        các sửa đổi được trả lời với một thông báo lỗi hữu ích về những gì
        đã thất bại.

        Điều này tạo ra một thể hiện của :attr:`null_session_class` theo mặc định.
        """
        return self.null_session_class()

    def is_null_session(self, obj: object) -> bool:
        """Kiểm tra xem một đối tượng đã cho có phải là một session null hay không. Các session null
        không được yêu cầu lưu.

        Điều này kiểm tra xem đối tượng có phải là một thể hiện của :attr:`null_session_class`
        theo mặc định hay không.
        """
        return isinstance(obj, self.null_session_class)

    def get_cookie_name(self, app: Flask) -> str:
        """Tên của cookie session. Sử dụng ``app.config["SESSION_COOKIE_NAME"]``."""
        return app.config["SESSION_COOKIE_NAME"]  # type: ignore[no-any-return]

    def get_cookie_domain(self, app: Flask) -> str | None:
        """Giá trị của tham số ``Domain`` trên cookie session. Nếu không được thiết lập,
        các trình duyệt sẽ chỉ gửi cookie đến tên miền chính xác mà nó được thiết lập.
        Nếu không, chúng sẽ gửi nó đến bất kỳ tên miền phụ nào của giá trị đã cho.

        Sử dụng cấu hình :data:`SESSION_COOKIE_DOMAIN`.

        .. versionchanged:: 2.3
            Không được thiết lập theo mặc định, không quay lại ``SERVER_NAME``.
        """
        return app.config["SESSION_COOKIE_DOMAIN"]  # type: ignore[no-any-return]

    def get_cookie_path(self, app: Flask) -> str:
        """Trả về đường dẫn mà cookie nên hợp lệ. Triển khai
        mặc định sử dụng giá trị từ biến cấu hình ``SESSION_COOKIE_PATH``
        nếu nó được thiết lập, và quay lại ``APPLICATION_ROOT`` hoặc
        sử dụng ``/`` nếu nó là ``None``.
        """
        return app.config["SESSION_COOKIE_PATH"] or app.config["APPLICATION_ROOT"]  # type: ignore[no-any-return]

    def get_cookie_httponly(self, app: Flask) -> bool:
        """Trả về True nếu cookie session nên là httponly. Điều này
        hiện tại chỉ trả về giá trị của biến cấu hình ``SESSION_COOKIE_HTTPONLY``.
        """
        return app.config["SESSION_COOKIE_HTTPONLY"]  # type: ignore[no-any-return]

    def get_cookie_secure(self, app: Flask) -> bool:
        """Trả về True nếu cookie nên được bảo mật. Điều này hiện tại
        chỉ trả về giá trị của cài đặt ``SESSION_COOKIE_SECURE``.
        """
        return app.config["SESSION_COOKIE_SECURE"]  # type: ignore[no-any-return]

    def get_cookie_samesite(self, app: Flask) -> str | None:
        """Trả về ``'Strict'`` hoặc ``'Lax'`` nếu cookie nên sử dụng
        thuộc tính ``SameSite``. Điều này hiện tại chỉ trả về giá trị của
        cài đặt :data:`SESSION_COOKIE_SAMESITE`.
        """
        return app.config["SESSION_COOKIE_SAMESITE"]  # type: ignore[no-any-return]

    def get_cookie_partitioned(self, app: Flask) -> bool:
        """Trả về True nếu cookie nên được phân vùng. Theo mặc định, sử dụng
        giá trị của :data:`SESSION_COOKIE_PARTITIONED`.

        .. versionadded:: 3.1
        """
        return app.config["SESSION_COOKIE_PARTITIONED"]  # type: ignore[no-any-return]

    def get_expiration_time(self, app: Flask, session: SessionMixin) -> datetime | None:
        """Một phương thức trợ giúp trả về ngày hết hạn cho session
        hoặc ``None`` nếu session được liên kết với session trình duyệt. Triển khai
        mặc định trả về bây giờ + thời gian tồn tại session vĩnh viễn
        được cấu hình trên ứng dụng.
        """
        if session.permanent:
            return datetime.now(timezone.utc) + app.permanent_session_lifetime
        return None

    def should_set_cookie(self, app: Flask, session: SessionMixin) -> bool:
        """Được sử dụng bởi các backend session để xác định xem header ``Set-Cookie``
        có nên được thiết lập cho cookie session này cho phản hồi này hay không. Nếu session
        đã được sửa đổi, cookie được thiết lập. Nếu session là vĩnh viễn và
        cấu hình ``SESSION_REFRESH_EACH_REQUEST`` là true, cookie luôn được
        thiết lập.

        Kiểm tra này thường bị bỏ qua nếu session đã bị xóa.

        .. versionadded:: 0.11
        """

        return session.modified or (
            session.permanent and app.config["SESSION_REFRESH_EACH_REQUEST"]
        )

    def open_session(self, app: Flask, request: Request) -> SessionMixin | None:
        """Cái này được gọi ở đầu mỗi request, sau khi
        push ngữ cảnh request, trước khi khớp URL.

        Cái này phải trả về một đối tượng triển khai giao diện giống từ điển
        cũng như giao diện :class:`SessionMixin`.

        Cái này sẽ trả về ``None`` để chỉ ra rằng việc tải đã thất bại theo
        một cách nào đó không phải là lỗi ngay lập tức. Ngữ cảnh request
        sẽ quay lại sử dụng :meth:`make_null_session`
        trong trường hợp này.
        """
        raise NotImplementedError()

    def save_session(
        self, app: Flask, session: SessionMixin, response: Response
    ) -> None:
        """Cái này được gọi ở cuối mỗi request, sau khi tạo
        một phản hồi, trước khi xóa ngữ cảnh request. Nó bị bỏ qua
        nếu :meth:`is_null_session` trả về ``True``.
        """
        raise NotImplementedError()


session_json_serializer = TaggedJSONSerializer()


def _lazy_sha1(string: bytes = b"") -> t.Any:
    """Không truy cập ``hashlib.sha1`` cho đến khi runtime. Các bản build FIPS có thể không bao gồm
    SHA-1, trong trường hợp đó việc import và sử dụng làm mặc định sẽ thất bại trước khi
    nhà phát triển có thể cấu hình cái gì đó khác.
    """
    return hashlib.sha1(string)


class SecureCookieSessionInterface(SessionInterface):
    """Giao diện session mặc định lưu trữ các session trong các cookie đã ký
    thông qua module :mod:`itsdangerous`.
    """

    #: salt nên được áp dụng trên secret key cho
    #: việc ký các session dựa trên cookie.
    salt = "cookie-session"
    #: hàm băm để sử dụng cho chữ ký. Mặc định là sha1
    digest_method = staticmethod(_lazy_sha1)
    #: tên của dẫn xuất khóa được itsdangerous hỗ trợ. Mặc định
    #: là hmac.
    key_derivation = "hmac"
    #: Một serializer python cho payload. Mặc định là một serializer
    #: dẫn xuất JSON nhỏ gọn với hỗ trợ cho một số loại Python bổ sung
    #: chẳng hạn như các đối tượng datetime hoặc tuple.
    serializer = session_json_serializer
    session_class = SecureCookieSession

    def get_signing_serializer(self, app: Flask) -> URLSafeTimedSerializer | None:
        if not app.secret_key:
            return None

        keys: list[str | bytes] = []

        if fallbacks := app.config["SECRET_KEY_FALLBACKS"]:
            keys.extend(fallbacks)

        keys.append(app.secret_key)  # itsdangerous expects current key at top
        return URLSafeTimedSerializer(
            keys,  # type: ignore[arg-type]
            salt=self.salt,
            serializer=self.serializer,
            signer_kwargs={
                "key_derivation": self.key_derivation,
                "digest_method": self.digest_method,
            },
        )

    def open_session(self, app: Flask, request: Request) -> SecureCookieSession | None:
        s = self.get_signing_serializer(app)
        if s is None:
            return None
        val = request.cookies.get(self.get_cookie_name(app))
        if not val:
            return self.session_class()
        max_age = int(app.permanent_session_lifetime.total_seconds())
        try:
            data = s.loads(val, max_age=max_age)
            return self.session_class(data)
        except BadSignature:
            return self.session_class()

    def save_session(
        self, app: Flask, session: SessionMixin, response: Response
    ) -> None:
        name = self.get_cookie_name(app)
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        secure = self.get_cookie_secure(app)
        partitioned = self.get_cookie_partitioned(app)
        samesite = self.get_cookie_samesite(app)
        httponly = self.get_cookie_httponly(app)

        # Thêm một header "Vary: Cookie" nếu session đã được truy cập.
        if session.accessed:
            response.vary.add("Cookie")

        # Nếu session được sửa đổi thành trống, xóa cookie.
        # Nếu session trống, trả về mà không thiết lập cookie.
        if not session:
            if session.modified:
                response.delete_cookie(
                    name,
                    domain=domain,
                    path=path,
                    secure=secure,
                    partitioned=partitioned,
                    samesite=samesite,
                    httponly=httponly,
                )
                response.vary.add("Cookie")

            return

        if not self.should_set_cookie(app, session):
            return

        expires = self.get_expiration_time(app, session)
        val = self.get_signing_serializer(app).dumps(dict(session))  # type: ignore[union-attr]
        response.set_cookie(
            name,
            val,
            expires=expires,
            httponly=httponly,
            domain=domain,
            path=path,
            secure=secure,
            partitioned=partitioned,
            samesite=samesite,
        )
        response.vary.add("Cookie")
