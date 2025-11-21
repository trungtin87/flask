App và Request Context
=======================

Context theo dõi dữ liệu và các đối tượng trong một request, lệnh CLI, hoặc
hoạt động khác. Thay vì truyền dữ liệu này đến mọi hàm, các proxy
:data:`.current_app`, :data:`.g`, :data:`.request`, và :data:`.session`
được truy cập thay thế.

Khi xử lý một request, context được gọi là "request context"
vì nó chứa dữ liệu request ngoài dữ liệu ứng dụng. Ngược lại,
chẳng hạn như trong một lệnh CLI, nó được gọi là "app context". Trong một
app context, :data:`.current_app` và :data:`.g` có sẵn, trong khi trong một
request context :data:`.request` và :data:`.session` cũng có sẵn.


Mục đích của Context
--------------------

Context và các proxy giúp giải quyết hai vấn đề phát triển: circular imports (import vòng tròn), và
truyền dữ liệu toàn cục trong một request.

Đối tượng ứng dụng :class:`.Flask` có các thuộc tính, chẳng hạn như
:attr:`~.Flask.config`, hữu ích để truy cập trong các view và các hàm
khác. Tuy nhiên, việc import thể hiện ``app`` trong các module trong
dự án của bạn dễ bị các vấn đề circular import. Khi sử dụng
:doc:`mẫu app factory </patterns/appfactories>` hoặc viết các
:doc:`blueprints </blueprints>` hoặc :doc:`extensions </extensions>` có thể tái sử dụng, sẽ không
có thể hiện ``app`` nào để import cả.

Khi ứng dụng xử lý một request, nó tạo ra một đối tượng :class:`.Request`.
Bởi vì một *worker* chỉ xử lý một request tại một thời điểm, dữ liệu request có thể
được coi là toàn cục đối với worker đó trong request đó. Truyền nó như một đối số
qua mọi hàm trong request trở nên dài dòng và dư thừa.

Flask giải quyết những vấn đề này với mẫu *active context*. Thay vì
import trực tiếp một ``app``, hoặc phải truyền nó và request qua
từng hàm một, bạn import và truy cập các proxy, trỏ đến
ứng dụng và dữ liệu request đang hoạt động hiện tại. Điều này đôi khi được gọi
là dữ liệu "context local".


Context Trong Quá trình Thiết lập
---------------------------------

Nếu bạn cố gắng truy cập :data:`.current_app`, :data:`.g`, hoặc bất cứ thứ gì sử dụng nó,
bên ngoài một app context, bạn sẽ nhận được thông báo lỗi này:

.. code-block:: pytb

    RuntimeError: Working outside of application context.

    Attempted to use functionality that expected a current application to be
    set. To solve this, set up an app context using 'with app.app_context()'.
    See the documentation on app context for more information.

Nếu bạn thấy lỗi đó trong khi cấu hình ứng dụng của mình, chẳng hạn như khi
khởi tạo một extension, bạn có thể đẩy (push) một context thủ công vì bạn có quyền truy cập trực tiếp
đến ``app``. Sử dụng :meth:`.Flask.app_context` trong một khối ``with``.

.. code-block:: python

    def create_app():
        app = Flask(__name__)

        with app.app_context():
            init_db()

        return app

Nếu bạn thấy lỗi đó ở đâu đó khác trong mã của bạn không liên quan đến việc thiết lập
ứng dụng, nó rất có thể chỉ ra rằng bạn nên di chuyển mã đó vào một hàm view
hoặc lệnh CLI.


Context Trong Quá trình Kiểm thử (Testing)
------------------------------------------

Xem :doc:`/testing` để biết thông tin chi tiết về việc quản lý context trong
các bài kiểm thử.

Nếu bạn cố gắng truy cập :data:`.request`, :data:`.session`, hoặc bất cứ thứ gì sử dụng
nó, bên ngoài một request context, bạn sẽ nhận được thông báo lỗi này:

.. code-block:: pytb

    RuntimeError: Working outside of request context.

    Attempted to use functionality that expected an active HTTP request. See the
    documentation on request context for more information.

Điều này có lẽ sẽ chỉ xảy ra trong các bài kiểm thử. Nếu bạn thấy lỗi đó ở đâu đó
khác trong mã của bạn không liên quan đến kiểm thử, nó rất có thể chỉ ra rằng bạn
nên di chuyển mã đó vào một hàm view.

Cách chính để giải quyết vấn đề này là sử dụng :meth:`.Flask.test_client` để mô phỏng
một request đầy đủ.

Nếu bạn chỉ muốn kiểm thử đơn vị (unit test) một hàm, thay vì một request đầy đủ, hãy sử dụng
:meth:`.Flask.test_request_context` trong một khối ``with``.

.. code-block:: python

    def generate_report(year):
        format = request.args.get("format")
        ...

    with app.test_request_context(
        "/make_report/2017", query_string={"format": "short"}
    ):
        generate_report()


.. _context-visibility:

Khả năng hiển thị của Context
-----------------------------

Context sẽ có cùng vòng đời với một hoạt động, chẳng hạn như một request, lệnh CLI,
hoặc khối ``with``. Các callback và signals khác nhau được đăng ký với
app sẽ được chạy trong context.

Khi một ứng dụng Flask xử lý một request, nó đẩy một request context
để thiết lập ứng dụng và dữ liệu request đang hoạt động. Khi nó xử lý một lệnh CLI,
nó đẩy một app context để thiết lập ứng dụng đang hoạt động. Khi hoạt động kết thúc,
nó pop context đó. Các đối tượng proxy như :data:`.request`, :data:`.session`,
:data:`.g`, và :data:`.current_app`, có thể truy cập được trong khi context được đẩy
và hoạt động, và không thể truy cập được sau khi context bị pop.

Context là duy nhất cho mỗi luồng (hoặc loại worker khác). Các proxy không thể
được truyền sang một worker khác, worker này có không gian context khác và sẽ không
biết về context đang hoạt động trong không gian của cha.

Ngoài việc được giới hạn phạm vi cho mỗi worker, đối tượng proxy có một loại và
định danh riêng biệt so với đối tượng thực được proxy. Trong một số trường hợp bạn sẽ cần truy cập vào
đối tượng thực, thay vì proxy. Sử dụng phương thức
:meth:`~.LocalProxy._get_current_object` trong những trường hợp đó.

.. code-block:: python

    app = current_app._get_current_object()
    my_signal.send(app)


Vòng đời của Context
--------------------

Flask điều phối một request qua nhiều giai đoạn có thể ảnh hưởng đến request,
response, và cách xử lý lỗi. Xem :doc:`/lifecycle` để biết danh sách tất cả
các bước, callbacks, và signals trong mỗi request. Dưới đây là các
bước liên quan trực tiếp đến context.

-   App context được đẩy, các proxy có sẵn.
-   Signal :data:`.appcontext_pushed` được gửi.
-   Request được điều phối.
-   Bất kỳ hàm nào được trang trí bằng :meth:`.Flask.teardown_request` đều được gọi.
-   Signal :data:`.request_tearing_down` được gửi.
-   Bất kỳ hàm nào được trang trí bằng :meth:`.Flask.teardown_appcontext` đều được gọi.
-   Signal :data:`.appcontext_tearing_down` được gửi.
-   App context bị pop, các proxy không còn có sẵn.
-   Signal :data:`.appcontext_popped` được gửi.

Các callback teardown được gọi bởi context khi nó bị pop. Chúng được
gọi ngay cả khi có một ngoại lệ không được xử lý trong quá trình điều phối. Chúng có thể được
gọi nhiều lần trong một số kịch bản kiểm thử. Điều này có nghĩa là không có đảm bảo
rằng bất kỳ phần nào khác của quá trình điều phối request đã chạy. Hãy chắc chắn viết các
hàm này theo cách không phụ thuộc vào các callback khác và sẽ không thất bại.


Cách Context Hoạt động
----------------------

Context locals được triển khai bằng cách sử dụng :mod:`contextvars` của Python và
:class:`~werkzeug.local.LocalProxy` của Werkzeug. Contextvars của Python là một cấu trúc
cấp thấp để quản lý dữ liệu cục bộ cho một luồng hoặc coroutine. ``LocalProxy`` bọc
contextvar để việc truy cập vào bất kỳ thuộc tính và phương thức nào cũng được chuyển tiếp đến
đối tượng được lưu trữ trong contextvar.

Context được theo dõi giống như một ngăn xếp (stack), với context đang hoạt động ở trên cùng của
ngăn xếp. Flask quản lý việc đẩy và pop context trong các request, lệnh CLI,
kiểm thử, khối ``with``, v.v. Các proxy truy cập các thuộc tính trên context
đang hoạt động.

Bởi vì nó là một ngăn xếp, các context khác có thể được đẩy để thay đổi các proxy trong
một context đã hoạt động. Đây không phải là một mẫu phổ biến, nhưng có thể được sử dụng trong
các trường hợp sử dụng nâng cao. Ví dụ, một ứng dụng Flask có thể được sử dụng làm WSGI
middleware, gọi một ứng dụng Flask được bọc khác từ một view.
