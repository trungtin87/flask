Điều phối Ứng dụng (Application Dispatching)
==========================================

Điều phối ứng dụng là quá trình kết hợp nhiều ứng dụng Flask
ở cấp độ WSGI. Bạn có thể kết hợp không chỉ các ứng dụng Flask
mà còn bất kỳ ứng dụng WSGI nào. Điều này sẽ cho phép bạn chạy một
ứng dụng Django và một ứng dụng Flask trong cùng một trình thông dịch cạnh nhau nếu
bạn muốn. Tính hữu ích của điều này phụ thuộc vào cách các ứng dụng hoạt động
bên trong.

Sự khác biệt cơ bản so với :doc:`packages` là trong trường hợp này bạn
đang chạy các ứng dụng Flask giống nhau hoặc khác nhau hoàn toàn
bị cô lập với nhau. Chúng chạy các cấu hình khác nhau và được
điều phối ở cấp độ WSGI.


Làm việc với Tài liệu này
-------------------------

Mỗi kỹ thuật và ví dụ dưới đây dẫn đến một đối tượng ``application``
có thể chạy với bất kỳ máy chủ WSGI nào. Để phát triển, sử dụng lệnh
``flask run`` để khởi động một máy chủ phát triển. Để sản xuất, xem
:doc:`/deploying/index`.

.. code-block:: python

    from flask import Flask

    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello World!'


Kết hợp các Ứng dụng
--------------------

Nếu bạn có các ứng dụng hoàn toàn tách biệt và bạn muốn chúng hoạt động cạnh
nhau trong cùng một quy trình trình thông dịch Python, bạn có thể tận dụng
lợi thế của :class:`werkzeug.wsgi.DispatcherMiddleware`. Ý tưởng
ở đây là mỗi ứng dụng Flask là một ứng dụng WSGI hợp lệ và chúng
được kết hợp bởi middleware điều phối thành một ứng dụng lớn hơn được
điều phối dựa trên tiền tố (prefix).

Ví dụ bạn có thể có ứng dụng chính của mình chạy trên ``/`` và giao diện
backend của bạn trên ``/backend``.

.. code-block:: python

    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    from frontend_app import application as frontend
    from backend_app import application as backend

    application = DispatcherMiddleware(frontend, {
        '/backend': backend
    })


Điều phối theo Tên miền phụ (Subdomain)
---------------------------------------

Đôi khi bạn có thể muốn sử dụng nhiều instance của cùng một ứng dụng
với các cấu hình khác nhau. Giả sử ứng dụng được tạo bên trong
một hàm và bạn có thể gọi hàm đó để khởi tạo nó, điều đó
thực sự dễ dàng để triển khai. Để phát triển ứng dụng của bạn để hỗ trợ
tạo các instance mới trong các hàm, hãy xem mẫu
:doc:`appfactories`.

Một ví dụ rất phổ biến sẽ là tạo các ứng dụng cho mỗi tên miền phụ. Ví dụ
bạn cấu hình máy chủ web của mình để điều phối tất cả các request cho tất cả
các tên miền phụ đến ứng dụng của bạn và sau đó bạn sử dụng thông tin tên miền phụ
để tạo các instance cụ thể cho người dùng. Khi bạn đã thiết lập máy chủ của mình để
lắng nghe trên tất cả các tên miền phụ, bạn có thể sử dụng một ứng dụng WSGI rất đơn giản để thực hiện
việc tạo ứng dụng động.

Mức độ hoàn hảo cho sự trừu tượng trong khía cạnh đó là lớp WSGI. Bạn
viết ứng dụng WSGI của riêng mình để xem xét request đến và
ủy quyền nó cho ứng dụng Flask của bạn. Nếu ứng dụng đó chưa
tồn tại, nó được tạo động và được ghi nhớ.

.. code-block:: python

    from threading import Lock

    class SubdomainDispatcher:

        def __init__(self, domain, create_app):
            self.domain = domain
            self.create_app = create_app
            self.lock = Lock()
            self.instances = {}

        def get_application(self, host):
            host = host.split(':')[0]
            assert host.endswith(self.domain), 'Configuration error'
            subdomain = host[:-len(self.domain)].rstrip('.')
            with self.lock:
                app = self.instances.get(subdomain)
                if app is None:
                    app = self.create_app(subdomain)
                    self.instances[subdomain] = app
                return app

        def __call__(self, environ, start_response):
            app = self.get_application(environ['HTTP_HOST'])
            return app(environ, start_response)


Dispatcher này sau đó có thể được sử dụng như thế này:

.. code-block:: python

    from myapplication import create_app, get_user_for_subdomain
    from werkzeug.exceptions import NotFound

    def make_app(subdomain):
        user = get_user_for_subdomain(subdomain)
        if user is None:
            # nếu không có người dùng cho tên miền phụ đó chúng ta vẫn phải
            # trả về một ứng dụng WSGI xử lý request đó.
            # Chúng ta có thể chỉ cần trả về ngoại lệ NotFound() như là
            # ứng dụng sẽ render một trang 404 mặc định.
            # Bạn cũng có thể chuyển hướng người dùng đến trang chính sau đó
            return NotFound()

        # nếu không thì tạo ứng dụng cho người dùng cụ thể
        return create_app(user)

    application = SubdomainDispatcher('example.com', make_app)


Điều phối theo Đường dẫn (Path)
-------------------------------

Điều phối theo một đường dẫn trên URL rất giống nhau. Thay vì nhìn vào
header ``Host`` để tìm ra tên miền phụ, người ta chỉ cần nhìn vào
đường dẫn request cho đến dấu gạch chéo đầu tiên.

.. code-block:: python

    from threading import Lock
    from wsgiref.util import shift_path_info

    class PathDispatcher:

        def __init__(self, default_app, create_app):
            self.default_app = default_app
            self.create_app = create_app
            self.lock = Lock()
            self.instances = {}

        def get_application(self, prefix):
            with self.lock:
                app = self.instances.get(prefix)
                if app is None:
                    app = self.create_app(prefix)
                    if app is not None:
                        self.instances[prefix] = app
                return app

        def __call__(self, environ, start_response):
            app = self.get_application(_peek_path_info(environ))
            if app is not None:
                shift_path_info(environ)
            else:
                app = self.default_app
            return app(environ, start_response)

    def _peek_path_info(environ):
        segments = environ.get("PATH_INFO", "").lstrip("/").split("/", 1)
        if segments:
            return segments[0]

        return None

Sự khác biệt lớn giữa cái này và cái tên miền phụ là cái này
dự phòng sang một ứng dụng khác nếu hàm tạo trả về ``None``.

.. code-block:: python

    from myapplication import create_app, default_app, get_user_for_prefix

    def make_app(prefix):
        user = get_user_for_prefix(prefix)
        if user is not None:
            return create_app(user)

    application = PathDispatcher(default_app, make_app)
