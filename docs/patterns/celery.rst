Tác vụ Nền với Celery
=======================

Nếu ứng dụng của bạn có một tác vụ chạy lâu, chẳng hạn như xử lý một số dữ liệu đã tải lên hoặc
gửi email, bạn không muốn đợi nó hoàn thành trong một request. Thay vào đó, hãy sử dụng một
hàng đợi tác vụ để gửi dữ liệu cần thiết đến một process khác sẽ chạy tác vụ trong
nền trong khi request trả về ngay lập tức.

`Celery`_ là một hàng đợi tác vụ mạnh mẽ có thể được sử dụng cho các tác vụ nền đơn giản cũng như
các chương trình và lịch trình đa giai đoạn phức tạp. Hướng dẫn này sẽ chỉ cho bạn cách cấu hình
Celery bằng Flask. Đọc hướng dẫn `First Steps with Celery`_ của Celery để tìm hiểu cách sử dụng
chính Celery.

.. _Celery: https://celery.readthedocs.io
.. _First Steps with Celery: https://celery.readthedocs.io/en/latest/getting-started/first-steps-with-celery.html

Kho lưu trữ Flask chứa `một ví dụ <https://github.com/pallets/flask/tree/main/examples/celery>`_
dựa trên thông tin trên trang này, cũng chỉ ra cách sử dụng JavaScript để gửi
các tác vụ và thăm dò tiến trình và kết quả.


Cài đặt
-------

Cài đặt Celery từ PyPI, ví dụ sử dụng pip:

.. code-block:: text

    $ pip install celery


Tích hợp Celery với Flask
-------------------------

Bạn có thể sử dụng Celery mà không cần bất kỳ sự tích hợp nào với Flask, nhưng thật tiện lợi khi cấu hình
nó thông qua config của Flask, và để các tác vụ truy cập vào ứng dụng Flask.

Celery sử dụng các ý tưởng tương tự như Flask, với một đối tượng ứng dụng ``Celery`` có cấu hình
và đăng ký các tác vụ. Trong khi tạo một ứng dụng Flask, hãy sử dụng mã sau để tạo và
cấu hình một ứng dụng Celery nữa.

.. code-block:: python

    from celery import Celery, Task

    def celery_init_app(app: Flask) -> Celery:
        class FlaskTask(Task):
            def __call__(self, *args: object, **kwargs: object) -> object:
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery_app = Celery(app.name, task_cls=FlaskTask)
        celery_app.config_from_object(app.config["CELERY"])
        celery_app.set_default()
        app.extensions["celery"] = celery_app
        return celery_app

Điều này tạo và trả về một đối tượng ứng dụng ``Celery``. `Cấu hình`_ Celery được lấy từ
khóa ``CELERY`` trong cấu hình Flask. Ứng dụng Celery được đặt làm mặc định, để
nó được nhìn thấy trong mỗi request. Lớp con ``Task`` tự động chạy các hàm
tác vụ với một ngữ cảnh ứng dụng Flask đang hoạt động, để các dịch vụ như kết nối cơ sở dữ liệu
của bạn có sẵn.

.. _configuration: https://celery.readthedocs.io/en/stable/userguide/configuration.html

Dưới đây là một ``example.py`` cơ bản cấu hình Celery để sử dụng Redis để giao tiếp. Chúng tôi
bật một result backend, nhưng bỏ qua kết quả theo mặc định. Điều này cho phép chúng tôi lưu trữ kết quả
chỉ cho các tác vụ mà chúng tôi quan tâm đến kết quả.

.. code-block:: python

    from flask import Flask

    app = Flask(__name__)
    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
        ),
    )
    celery_app = celery_init_app(app)

Trỏ lệnh ``celery worker`` vào đây và nó sẽ tìm thấy đối tượng ``celery_app``.

.. code-block:: text

    $ celery -A example worker --loglevel INFO

Bạn cũng có thể chạy lệnh ``celery beat`` để chạy các tác vụ theo lịch trình. Xem tài liệu
của Celery để biết thêm thông tin về việc định nghĩa lịch trình.

.. code-block:: text

    $ celery -A example beat --loglevel INFO


Application Factory
-------------------

Khi sử dụng mẫu application factory của Flask, hãy gọi hàm ``celery_init_app``
bên trong factory. Nó đặt ``app.extensions["celery"]`` thành đối tượng ứng dụng Celery, cái mà
có thể được sử dụng để lấy ứng dụng Celery từ ứng dụng Flask được trả về bởi factory.

.. code-block:: python

    def create_app() -> Flask:
        app = Flask(__name__)
        app.config.from_mapping(
            CELERY=dict(
                broker_url="redis://localhost",
                result_backend="redis://localhost",
                task_ignore_result=True,
            ),
        )
        app.config.from_prefixed_env()
        celery_init_app(app)
        return app

Để sử dụng các lệnh ``celery``, Celery cần một đối tượng ứng dụng, nhưng điều đó không còn
có sẵn trực tiếp nữa. Tạo một file ``make_celery.py`` gọi Flask app factory và lấy
ứng dụng Celery từ ứng dụng Flask được trả về.

.. code-block:: python

    from example import create_app

    flask_app = create_app()
    celery_app = flask_app.extensions["celery"]

Trỏ lệnh ``celery`` đến file này.

.. code-block:: text

    $ celery -A make_celery worker --loglevel INFO
    $ celery -A make_celery beat --loglevel INFO


Định nghĩa Tác vụ
-----------------

Sử dụng ``@celery_app.task`` để decorate các hàm tác vụ yêu cầu quyền truy cập vào
đối tượng ``celery_app``, cái mà sẽ không có sẵn khi sử dụng mẫu factory. Nó cũng
có nghĩa là các tác vụ được decorate bị ràng buộc với các instance ứng dụng Flask và Celery cụ thể,
điều này có thể là một vấn đề trong quá trình kiểm thử nếu bạn thay đổi cấu hình cho một bài kiểm tra.

Thay vào đó, hãy sử dụng decorator ``@shared_task`` của Celery. Điều này tạo ra các đối tượng tác vụ sẽ
truy cập bất cứ thứ gì là "ứng dụng hiện tại", một khái niệm tương tự như các blueprint
và ngữ cảnh ứng dụng của Flask. Đây là lý do tại sao chúng ta đã gọi ``celery_app.set_default()`` ở trên.

Dưới đây là một tác vụ ví dụ cộng hai số lại với nhau và trả về kết quả.

.. code-block:: python

    from celery import shared_task

    @shared_task(ignore_result=False)
    def add_together(a: int, b: int) -> int:
        return a + b

Trước đó, chúng ta đã cấu hình Celery để bỏ qua kết quả tác vụ theo mặc định. Vì chúng ta muốn biết
giá trị trả về của tác vụ này, chúng ta đặt ``ignore_result=False``. Mặt khác, một tác vụ
không cần kết quả, chẳng hạn như gửi email, sẽ không đặt điều này.


Gọi Tác vụ
----------

Hàm được decorate trở thành một đối tượng tác vụ với các phương thức để gọi nó trong nền.
Cách đơn giản nhất là sử dụng phương thức ``delay(*args, **kwargs)``. Xem tài liệu của Celery để biết
thêm các phương thức.

Một worker Celery phải đang chạy để chạy tác vụ. Việc khởi động một worker được hiển thị trong
các phần trước.

.. code-block:: python

    from flask import request

    @app.post("/add")
    def start_add() -> dict[str, object]:
        a = request.form.get("a", type=int)
        b = request.form.get("b", type=int)
        result = add_together.delay(a, b)
        return {"result_id": result.id}

Route không nhận được kết quả của tác vụ ngay lập tức. Điều đó sẽ đánh bại mục đích bằng cách
chặn phản hồi. Thay vào đó, chúng ta trả về id kết quả của tác vụ đang chạy, cái mà chúng ta có thể sử dụng
sau này để lấy kết quả.


Lấy Kết quả
-----------

Để lấy kết quả của tác vụ chúng ta đã bắt đầu ở trên, chúng ta sẽ thêm một route khác nhận
id kết quả mà chúng ta đã trả về trước đó. Chúng ta trả về việc liệu tác vụ đã hoàn thành (sẵn sàng) chưa, liệu nó
đã hoàn thành thành công chưa, và giá trị trả về (hoặc lỗi) là gì nếu nó đã hoàn thành.

.. code-block:: python

    from celery.result import AsyncResult

    @app.get("/result/<id>")
    def task_result(id: str) -> dict[str, object]:
        result = AsyncResult(id)
        return {
            "ready": result.ready(),
            "successful": result.successful(),
            "value": result.result if result.ready() else None,
        }

Bây giờ bạn có thể bắt đầu tác vụ bằng cách sử dụng route đầu tiên, sau đó thăm dò kết quả bằng cách sử dụng
route thứ hai. Điều này giữ cho các worker request của Flask không bị chặn chờ đợi các tác vụ
hoàn thành.

Kho lưu trữ Flask chứa `một ví dụ <https://github.com/pallets/flask/tree/main/examples/celery>`_
sử dụng JavaScript để gửi các tác vụ và thăm dò tiến trình và kết quả.


Truyền Dữ liệu cho Tác vụ
-------------------------

Tác vụ "add" ở trên đã nhận hai số nguyên làm đối số. Để truyền các đối số cho các tác vụ, Celery
phải tuần tự hóa chúng thành một định dạng mà nó có thể truyền cho các process khác. Do đó,
việc truyền các đối tượng phức tạp không được khuyến nghị. Ví dụ, sẽ không thể truyền
một đối tượng model SQLAlchemy, vì đối tượng đó có thể không tuần tự hóa được và bị ràng buộc với
phiên làm việc đã truy vấn nó.

Truyền lượng dữ liệu tối thiểu cần thiết để lấy hoặc tạo lại bất kỳ dữ liệu phức tạp nào bên trong
tác vụ. Hãy xem xét một tác vụ sẽ chạy khi người dùng đã đăng nhập yêu cầu một bản lưu trữ
dữ liệu của họ. Request Flask biết người dùng đã đăng nhập, và có đối tượng người dùng được truy vấn
từ cơ sở dữ liệu. Nó có được điều đó bằng cách truy vấn cơ sở dữ liệu cho một id nhất định, vì vậy tác vụ có thể
làm điều tương tự. Truyền id của người dùng thay vì đối tượng người dùng.

.. code-block:: python

    @shared_task
    def generate_user_archive(user_id: str) -> None:
        user = db.session.get(User, user_id)
        ...

    generate_user_archive.delay(current_user.id)
