Bối cảnh Ứng dụng và Yêu cầu
===========================

Bối cảnh theo dõi dữ liệu và các đối tượng trong một yêu cầu, lệnh CLI hoặc hoạt động khác. Thay vì truyền dữ liệu này đến mọi hàm, các đối tượng proxy :data:`.current_app`, :data:`.g`, :data:`.request`, và :data:`.session` được truy cập thay thế.

Khi xử lý một yêu cầu, bối cảnh được gọi là "bối cảnh yêu cầu" vì nó chứa dữ liệu yêu cầu ngoài dữ liệu ứng dụng. Ngược lại, chẳng hạn như trong một lệnh CLI, nó được gọi là "bối cảnh ứng dụng". Trong một bối cảnh ứng dụng, :data:`.current_app` và :data:`.g` có sẵn, trong khi trong một bối cảnh yêu cầu, :data:`.request` và :data:`.session` cũng có sẵn.


Mục đích của Bối cảnh
----------------------

Bối cảnh và các đối tượng proxy giúp giải quyết hai vấn đề trong phát triển: nhập vòng tròn (circular imports), và truyền dữ liệu toàn cục trong một yêu cầu.

Đối tượng ứng dụng :class:`.Flask` có các thuộc tính, chẳng hạn như :attr:`~.Flask.config`, rất hữu ích để truy cập trong các view và các hàm khác. Tuy nhiên, việc nhập thực thể ``app`` trong các mô-đun của dự án của bạn dễ gây ra các vấn đề nhập vòng tròn. [12] Khi sử dụng :doc:`mẫu hình nhà máy ứng dụng (app factory pattern) </patterns/appfactories>` hoặc viết các :doc:`blueprint </blueprints>` hoặc :doc:`tiện ích mở rộng </extensions>` có thể tái sử dụng, sẽ không có thực thể ``app`` nào để nhập cả.

Khi ứng dụng xử lý một yêu cầu, nó tạo ra một đối tượng :class:`.Request`. Bởi vì một *worker* chỉ xử lý một yêu cầu tại một thời điểm, dữ liệu yêu cầu có thể được coi là toàn cục đối với worker đó trong suốt yêu cầu đó. Việc truyền nó như một đối số qua mọi hàm trong quá trình yêu cầu trở nên dài dòng và dư thừa.

Flask giải quyết những vấn đề này bằng mẫu hình *bối cảnh hoạt động*. Thay vì nhập trực tiếp một ``app``, hoặc phải truyền nó và yêu cầu qua mọi hàm, bạn nhập và truy cập các đối tượng proxy, chúng trỏ đến ứng dụng và dữ liệu yêu cầu đang hoạt động. Điều này đôi khi được gọi là dữ liệu "cục bộ theo bối cảnh" (context local). [9]


Bối cảnh trong quá trình Thiết lập
--------------------

Nếu bạn cố gắng truy cập :data:`.current_app`, :data:`.g`, hoặc bất cứ thứ gì sử dụng nó, bên ngoài một bối cảnh ứng dụng, bạn sẽ nhận được thông báo lỗi này:

.. code-block:: pytb

    RuntimeError: Working outside of application context.

    Attempted to use functionality that expected a current application to be
    set. To solve this, set up an app context using 'with app.app_context()'.
    See the documentation on app context for more information.

Nếu bạn thấy lỗi đó trong khi cấu hình ứng dụng của mình, chẳng hạn như khi khởi tạo một tiện ích mở rộng, bạn có thể đẩy một bối cảnh theo cách thủ công vì bạn có quyền truy cập trực tiếp vào ``app``. Sử dụng :meth:`.Flask.app_context` trong một khối ``with``.

.. code-block:: python

    def create_app():
        app = Flask(__name__)

        with app.app_context():
            init_db()

        return app

Nếu bạn thấy lỗi đó ở một nơi khác trong mã của mình không liên quan đến việc thiết lập ứng dụng, rất có thể điều đó cho thấy bạn nên chuyển mã đó vào một hàm view hoặc lệnh CLI.


Bối cảnh trong quá trình Kiểm thử
----------------------

Xem :doc:`/testing` để biết thông tin chi tiết về việc quản lý bối cảnh trong các bài kiểm thử.

Nếu bạn cố gắng truy cập :data:`.request`, :data:`.session`, hoặc bất cứ thứ gì sử dụng nó, bên ngoài một bối cảnh yêu cầu, bạn sẽ nhận được thông báo lỗi này:

.. code-block:: pytb

    RuntimeError: Working outside of request context.

    Attempted to use functionality that expected an active HTTP request. See the
    documentation on request context for more information.

Điều này có lẽ sẽ chỉ xảy ra trong các bài kiểm thử. Nếu bạn thấy lỗi đó ở một nơi khác trong mã của mình không liên quan đến việc kiểm thử, rất có thể điều đó cho thấy bạn nên chuyển mã đó vào một hàm view.

Cách chính để giải quyết vấn đề này là sử dụng :meth:`.Flask.test_client` để mô phỏng một yêu cầu đầy đủ.

Nếu bạn chỉ muốn kiểm thử đơn vị (unit test) một hàm, thay vì một yêu cầu đầy đủ, hãy sử dụng :meth:`.Flask.test_request_context` trong một khối ``with``.

.. code-block:: python

    def generate_report(year):
        format = request.args.get("format")
        ...

    with app.test_request_context(
        "/make_report/2017", query_string={"format": "short"}
    ):
        generate_report()


.. _context-visibility:

Phạm vi hiển thị của Bối cảnh
-------------------------

Bối cảnh sẽ có vòng đời giống như một hoạt động, chẳng hạn như một yêu cầu, lệnh CLI, hoặc khối ``with``. Các lệnh gọi lại (callback) và tín hiệu (signal) khác nhau được đăng ký với ứng dụng sẽ được chạy trong suốt bối cảnh.

Khi một ứng dụng Flask xử lý một yêu cầu, nó sẽ đẩy một bối cảnh yêu cầu để thiết lập dữ liệu ứng dụng và yêu cầu đang hoạt động. Khi nó xử lý một lệnh CLI, nó sẽ đẩy một bối cảnh ứng dụng để thiết lập ứng dụng đang hoạt động. Khi hoạt động kết thúc, nó sẽ bật (pop) bối cảnh đó ra. Các đối tượng proxy như :data:`.request`, :data:`.session`, :data:`.g`, và :data:`.current_app`, có thể truy cập được khi bối cảnh được đẩy và đang hoạt động, và không thể truy cập được sau khi bối cảnh được bật ra.

Bối cảnh là duy nhất cho mỗi luồng (hoặc loại worker khác). Các đối tượng proxy không thể được truyền cho một worker khác, vốn có một không gian bối cảnh khác và sẽ không biết về bối cảnh đang hoạt động trong không gian của worker cha.

Ngoài việc được giới hạn trong phạm vi của mỗi worker, đối tượng proxy có một kiểu và định danh riêng biệt so với đối tượng thực được ủy quyền. Trong một số trường hợp, bạn sẽ cần truy cập vào đối tượng thực, thay vì đối tượng proxy. Sử dụng phương thức :meth:`~.LocalProxy._get_current_object` trong những trường hợp đó.

.. code-block:: python

    app = current_app._get_current_object()
    my_signal.send(app)


Vòng đời của Bối cảnh
------------------------

Flask điều phối một yêu cầu qua nhiều giai đoạn có thể ảnh hưởng đến yêu cầu, phản hồi và cách xử lý lỗi. Xem :doc:`/lifecycle` để biết danh sách tất cả các bước, lệnh gọi lại và tín hiệu trong mỗi yêu cầu. Sau đây là các bước liên quan trực tiếp đến bối cảnh.

-   Bối cảnh ứng dụng được đẩy vào, các proxy có sẵn.
-   Tín hiệu :data:`.appcontext_pushed` được gửi đi.
-   Yêu cầu được điều phối.
-   Bất kỳ hàm nào được trang trí bằng :meth:`.Flask.teardown_request` đều được gọi. [1, 4, 5, 7]
-   Tín hiệu :data:`.request_tearing_down` được gửi đi.
-   Bất kỳ hàm nào được trang trí bằng :meth:`.Flask.teardown_appcontext` đều được gọi.
-   Tín hiệu :data:`.appcontext_tearing_down` được gửi đi.
-   Bối cảnh ứng dụng được bật ra, các proxy không còn khả dụng.
-   Tín hiệu :data:`.appcontext_popped` được gửi đi.

Các lệnh gọi lại dọn dẹp (teardown callbacks) được gọi bởi bối cảnh khi nó được bật ra. [1, 4, 5, 7] Chúng được gọi ngay cả khi có một ngoại lệ không được xử lý trong quá trình điều phối. Chúng có thể được gọi nhiều lần trong một số kịch bản kiểm thử. Điều này có nghĩa là không có gì đảm bảo rằng bất kỳ phần nào khác của quá trình điều phối yêu cầu đã chạy. Hãy chắc chắn rằng bạn viết các hàm này theo cách không phụ thuộc vào các lệnh gọi lại khác và sẽ không bị lỗi.


Cách Bối cảnh Hoạt động
---------------------

Các biến cục bộ theo bối cảnh (context locals) được triển khai bằng cách sử dụng :mod:`contextvars` của Python và :class:`~werkzeug.local.LocalProxy` của Werkzeug. `contextvars` của Python là một cấu trúc cấp thấp để quản lý dữ liệu cục bộ cho một luồng hoặc coroutine. ``LocalProxy`` bao bọc contextvar để mọi truy cập vào bất kỳ thuộc tính và phương thức nào đều được chuyển tiếp đến đối tượng được lưu trữ trong contextvar.

Bối cảnh được theo dõi giống như một ngăn xếp, với bối cảnh hoạt động ở trên cùng của ngăn xếp. Flask quản lý việc đẩy và bật các bối cảnh trong các yêu cầu, lệnh CLI, kiểm thử, khối ``with``, v.v. Các proxy truy cập các thuộc tính trên bối cảnh đang hoạt động.

Bởi vì nó là một ngăn xếp, các bối cảnh khác có thể được đẩy vào để thay đổi các proxy trong một bối cảnh đã hoạt động. Đây không phải là một mẫu hình phổ biến, nhưng có thể được sử dụng trong các trường hợp sử dụng nâng cao. Ví dụ, một ứng dụng Flask có thể được sử dụng làm phần mềm trung gian WSGI, gọi một ứng dụng Flask được bao bọc khác từ một view.
