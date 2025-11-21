from __future__ import annotations

import typing as t

from . import typing as ft
from .globals import current_app
from .globals import request

F = t.TypeVar("F", bound=t.Callable[..., t.Any])

http_method_funcs = frozenset(
    ["get", "post", "head", "options", "delete", "put", "trace", "patch"]
)


class View:
    """Phân lớp lớp này và ghi đè :meth:`dispatch_request` để
    tạo một view dựa trên lớp chung. Gọi :meth:`as_view` để tạo một
    hàm view tạo ra một thể hiện của lớp với các đối số đã cho
    và gọi phương thức ``dispatch_request`` của nó với bất kỳ biến URL nào.

    Xem :doc:`views` để biết hướng dẫn chi tiết.

    .. code-block:: python

        class Hello(View):
            init_every_request = False

            def dispatch_request(self, name):
                return f"Hello, {name}!"

        app.add_url_rule(
            "/hello/<name>", view_func=Hello.as_view("hello")
        )

    Thiết lập :attr:`methods` trên lớp để thay đổi những phương thức mà view
    chấp nhận.

    Thiết lập :attr:`decorators` trên lớp để áp dụng một danh sách các decorator cho
    hàm view đã tạo. Các decorator được áp dụng cho chính lớp đó
    sẽ không được áp dụng cho hàm view đã tạo!

    Thiết lập :attr:`init_every_request` thành ``False`` để tăng hiệu quả, trừ khi
    bạn cần lưu trữ dữ liệu toàn cục request trên ``self``.
    """

    #: Các phương thức mà view này được đăng ký. Sử dụng cùng mặc định
    #: (``["GET", "HEAD", "OPTIONS"]``) như ``route`` và
    #: ``add_url_rule`` theo mặc định.
    methods: t.ClassVar[t.Collection[str] | None] = None

    #: Kiểm soát xem phương thức ``OPTIONS`` có được xử lý tự động hay không.
    #: Sử dụng cùng mặc định (``True``) như ``route`` và
    #: ``add_url_rule`` theo mặc định.
    provide_automatic_options: t.ClassVar[bool | None] = None

    #: Một danh sách các decorator để áp dụng, theo thứ tự, cho hàm view
    #: đã tạo. Hãy nhớ rằng cú pháp ``@decorator`` được áp dụng từ dưới
    #: lên trên, vì vậy decorator đầu tiên trong danh sách sẽ là decorator
    #: dưới cùng.
    #:
    #: .. versionadded:: 0.8
    decorators: t.ClassVar[list[t.Callable[..., t.Any]]] = []

    #: Tạo một thể hiện mới của lớp view này cho mỗi request theo
    #: mặc định. Nếu một lớp con view thiết lập cái này thành ``False``, cùng một
    #: thể hiện được sử dụng cho mỗi request.
    #:
    #: Một thể hiện duy nhất hiệu quả hơn, đặc biệt nếu thiết lập phức tạp
    #: được thực hiện trong quá trình init. Tuy nhiên, việc lưu trữ dữ liệu trên ``self`` không còn
    #: an toàn qua các request, và :data:`~flask.g` nên được sử dụng
    #: thay thế.
    #:
    #: .. versionadded:: 2.2
    init_every_request: t.ClassVar[bool] = True

    def dispatch_request(self) -> ft.ResponseReturnValue:
        """Hành vi hàm view thực tế. Các lớp con phải ghi đè
        cái này và trả về một phản hồi hợp lệ. Bất kỳ biến nào từ quy tắc
        URL đều được truyền dưới dạng đối số từ khóa.
        """
        raise NotImplementedError()

    @classmethod
    def as_view(
        cls, name: str, *class_args: t.Any, **class_kwargs: t.Any
    ) -> ft.RouteCallable:
        """Chuyển đổi lớp thành một hàm view có thể được đăng ký
        cho một route.

        Theo mặc định, view đã tạo sẽ tạo một thể hiện mới của
        lớp view cho mỗi request và gọi phương thức
        :meth:`dispatch_request` của nó. Nếu lớp view thiết lập
        :attr:`init_every_request` thành ``False``, cùng một thể hiện sẽ
        được sử dụng cho mỗi request.

        Ngoại trừ ``name``, tất cả các đối số khác được truyền cho phương thức này
        đều được chuyển tiếp đến phương thức ``__init__`` của lớp view.

        .. versionchanged:: 2.2
            Đã thêm thuộc tính lớp ``init_every_request``.
        """
        if cls.init_every_request:

            def view(**kwargs: t.Any) -> ft.ResponseReturnValue:
                self = view.view_class(  # type: ignore[attr-defined]
                    *class_args, **class_kwargs
                )
                return current_app.ensure_sync(self.dispatch_request)(**kwargs)  # type: ignore[no-any-return]

        else:
            self = cls(*class_args, **class_kwargs)  # pyright: ignore

            def view(**kwargs: t.Any) -> ft.ResponseReturnValue:
                return current_app.ensure_sync(self.dispatch_request)(**kwargs)  # type: ignore[no-any-return]

        if cls.decorators:
            view.__name__ = name
            view.__module__ = cls.__module__
            for decorator in cls.decorators:
                view = decorator(view)

        # Chúng tôi đính kèm lớp view vào hàm view vì hai lý do:
        # trước hết nó cho phép chúng tôi dễ dàng tìm ra view dựa trên lớp
        # này đến từ đâu, thứ hai nó cũng được sử dụng để khởi tạo
        # lớp view để bạn thực sự có thể thay thế nó bằng một cái gì đó khác
        # cho mục đích kiểm thử và gỡ lỗi.
        view.view_class = cls  # type: ignore
        view.__name__ = name
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.methods = cls.methods  # type: ignore
        view.provide_automatic_options = cls.provide_automatic_options  # type: ignore
        return view


class MethodView(View):
    """Gửi các phương thức request đến các phương thức thể hiện tương ứng.
    Ví dụ, nếu bạn triển khai một phương thức ``get``, nó sẽ được sử dụng để
    xử lý các request ``GET``.

    Điều này có thể hữu ích để định nghĩa một REST API.

    :attr:`methods` được thiết lập tự động dựa trên các phương thức được định nghĩa trên
    lớp.

    Xem :doc:`views` để biết hướng dẫn chi tiết.

    .. code-block:: python

        class CounterAPI(MethodView):
            def get(self):
                return str(session.get("counter", 0))

            def post(self):
                session["counter"] = session.get("counter", 0) + 1
                return redirect(url_for("counter"))

        app.add_url_rule(
            "/counter", view_func=CounterAPI.as_view("counter")
        )
    """

    def __init_subclass__(cls, **kwargs: t.Any) -> None:
        super().__init_subclass__(**kwargs)

        if "methods" not in cls.__dict__:
            methods = set()

            for base in cls.__bases__:
                if getattr(base, "methods", None):
                    methods.update(base.methods)  # type: ignore[attr-defined]

            for key in http_method_funcs:
                if hasattr(cls, key):
                    methods.add(key.upper())

            if methods:
                cls.methods = methods

    def dispatch_request(self, **kwargs: t.Any) -> ft.ResponseReturnValue:
        meth = getattr(self, request.method.lower(), None)

        # Nếu phương thức request là HEAD và chúng ta không có handler cho nó
        # thử lại với GET.
        if meth is None and request.method == "HEAD":
            meth = getattr(self, "get", None)

        assert meth is not None, f"Unimplemented method {request.method!r}"
        return current_app.ensure_sync(meth)(**kwargs)  # type: ignore[no-any-return]
