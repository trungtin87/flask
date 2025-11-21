.. _async_await:

Sử dụng ``async`` và ``await``
===============================

.. versionadded:: 2.0

Các route, error handler, before request, after request, và teardown
function đều có thể là các coroutine function nếu Flask được cài đặt với
``async`` extra (``pip install flask[async]``). Điều này cho phép các view được
định nghĩa với ``async def`` và sử dụng ``await``.

.. code-block:: python

    @app.route("/get-data")
    async def get_data():
        data = await async_db_query(...)
        return jsonify(data)

Các pluggable class-based view cũng hỗ trợ các handler được triển khai dưới dạng
coroutine. Điều này áp dụng cho phương thức :meth:`~flask.views.View.dispatch_request`
trong các view kế thừa từ class :class:`flask.views.View`, cũng như
tất cả các HTTP method handler trong các view kế thừa từ
class :class:`flask.views.MethodView`.

.. admonition:: Sử dụng ``async`` với greenlet

    Khi sử dụng gevent hoặc eventlet để phục vụ một ứng dụng hoặc patch
    runtime, greenlet>=1.0 là bắt buộc. Khi sử dụng PyPy, PyPy>=7.3.7 là
    bắt buộc.


Hiệu suất
---------

Các async function yêu cầu một event loop để chạy. Flask, với tư cách là một ứng dụng WSGI
, sử dụng một worker để xử lý một chu kỳ request/response.
Khi một request đến một async view, Flask sẽ khởi động một event loop
trong một thread, chạy view function ở đó, sau đó trả về kết quả.

Mỗi request vẫn chiếm một worker, ngay cả đối với các async view. Ưu điểm
là bạn có thể chạy async code trong một view, ví dụ để thực hiện
nhiều truy vấn cơ sở dữ liệu đồng thời, các HTTP request đến một API bên ngoài,
v.v. Tuy nhiên, số lượng request mà ứng dụng của bạn có thể xử lý cùng một
lúc sẽ vẫn giống nhau.

**Async không vốn dĩ nhanh hơn sync code.** Async có lợi
khi thực hiện các tác vụ IO-bound đồng thời, nhưng có thể sẽ không cải thiện
các tác vụ CPU-bound. Các view Flask truyền thống vẫn sẽ phù hợp cho
hầu hết các trường hợp sử dụng, nhưng hỗ trợ async của Flask cho phép viết và sử dụng
mã không thể thực hiện được một cách native trước đây.


Background task
---------------

Các async function sẽ chạy trong một event loop cho đến khi chúng hoàn thành, tại
giai đoạn đó event loop sẽ dừng. Điều này có nghĩa là bất kỳ
task được spawn bổ sung nào chưa hoàn thành khi async function hoàn thành
sẽ bị hủy. Do đó bạn không thể spawn background task, ví dụ
qua ``asyncio.create_task``.

Nếu bạn muốn sử dụng background task, tốt nhất là sử dụng một task queue để
kích hoạt công việc nền, thay vì spawn task trong một view
function. Với ý nghĩ đó, bạn có thể spawn asyncio task bằng cách phục vụ
Flask với một máy chủ ASGI và sử dụng adapter asgiref WsgiToAsgi
như được mô tả trong :doc:`deploying/asgi`. Điều này hoạt động vì adapter tạo
một event loop chạy liên tục.


Khi nào nên sử dụng Quart thay thế
-----------------------------------

Hỗ trợ async của Flask kém hiệu suất hơn các framework async-first do
cách nó được triển khai. Nếu bạn có một codebase chủ yếu là async, sẽ
hợp lý khi xem xét `Quart`_. Quart là một triển khai lại của
Flask dựa trên tiêu chuẩn `ASGI`_ thay vì WSGI. Điều này cho phép nó
xử lý nhiều request đồng thời, các request chạy lâu, và websocket
mà không yêu cầu nhiều worker process hoặc thread.

Cũng đã có thể chạy Flask với Gevent hoặc Eventlet
để có được nhiều lợi ích của xử lý request async. Các thư viện này
patch các hàm Python cấp thấp để thực hiện điều này, trong khi ``async``/
``await`` và ASGI sử dụng các khả năng Python tiêu chuẩn, hiện đại. Quyết định
xem bạn nên sử dụng Flask, Quart, hay một cái gì đó khác cuối cùng là
hiểu các nhu cầu cụ thể của dự án của bạn.

.. _Quart: https://github.com/pallets/quart
.. _ASGI: https://asgi.readthedocs.io/en/latest/


Extension
---------

Các Flask extension có trước hỗ trợ async của Flask không mong đợi các async view.
Nếu chúng cung cấp decorator để thêm chức năng vào view, những decorator đó có thể sẽ
không hoạt động với async view vì chúng sẽ không await hàm hoặc có thể
awaitable. Các hàm khác mà chúng cung cấp cũng sẽ không awaitable và
có thể sẽ blocking nếu được gọi trong một async view.

Các tác giả extension có thể hỗ trợ async function bằng cách sử dụng
phương thức :meth:`flask.Flask.ensure_sync`. Ví dụ, nếu extension
cung cấp một view function decorator, hãy thêm ``ensure_sync`` trước khi gọi
hàm được decorate,

.. code-block:: python

    def extension(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ...  # Extension logic
            return current_app.ensure_sync(func)(*args, **kwargs)

        return wrapper

Kiểm tra changelog của extension bạn muốn sử dụng để xem liệu họ đã
triển khai hỗ trợ async chưa, hoặc thực hiện feature request hoặc PR cho họ.


Event loop khác
---------------

Hiện tại Flask chỉ hỗ trợ :mod:`asyncio`. Có thể
ghi đè :meth:`flask.Flask.ensure_sync` để thay đổi cách các async function
được wrap để sử dụng một thư viện khác.
