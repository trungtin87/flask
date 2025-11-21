.. currentmodule:: flask

Máy chủ Phát triển (Development Server)
========================================

Flask cung cấp lệnh ``run`` để chạy ứng dụng với một máy chủ phát triển. Trong
chế độ debug, máy chủ này cung cấp một debugger tương tác và sẽ tải lại khi mã được
thay đổi.

.. warning::

    Không sử dụng máy chủ phát triển khi triển khai lên production. Nó
    chỉ dành cho sử dụng trong quá trình phát triển cục bộ. Nó không
    được thiết kế để đặc biệt hiệu quả, ổn định hoặc an toàn.

    Xem :doc:`/deploying/index` để biết các tùy chọn triển khai.

Dòng lệnh
---------

Lệnh CLI ``flask run`` là cách được khuyến nghị để chạy máy chủ phát triển. Sử dụng
tùy chọn ``--app`` để trỏ đến ứng dụng của bạn, và tùy chọn ``--debug`` để bật
chế độ debug.

.. code-block:: text

    $ flask --app hello run --debug

Điều này bật chế độ debug, bao gồm debugger tương tác và reloader, và sau đó
khởi động máy chủ trên http://localhost:5000/. Sử dụng ``flask run --help`` để xem các
tùy chọn có sẵn, và :doc:`/cli` để biết hướng dẫn chi tiết về cấu hình và sử dụng
CLI.


.. _address-already-in-use:

Địa chỉ đã được sử dụng
~~~~~~~~~~~~~~~~~~~~~~~

Nếu một chương trình khác đã sử dụng cổng 5000, bạn sẽ thấy một ``OSError``
khi máy chủ cố gắng khởi động. Nó có thể có một trong các
thông báo sau:

-   ``OSError: [Errno 98] Address already in use``
-   ``OSError: [WinError 10013] An attempt was made to access a socket
    in a way forbidden by its access permissions``

Hãy xác định và dừng chương trình khác, hoặc sử dụng
``flask run --port 5001`` để chọn một cổng khác.

Bạn có thể sử dụng ``netstat`` hoặc ``lsof`` để xác định process id nào đang sử dụng
một cổng, sau đó sử dụng các công cụ hệ điều hành khác để dừng process đó.
Ví dụ sau cho thấy process id 6847 đang sử dụng cổng 5000.

.. tabs::

    .. tab:: ``netstat`` (Linux)

        .. code-block:: text

            $ netstat -nlp | grep 5000
            tcp 0 0 127.0.0.1:5000 0.0.0.0:* LISTEN 6847/python

    .. tab:: ``lsof`` (macOS / Linux)

        .. code-block:: text

            $ lsof -P -i :5000
            Python 6847 IPv4 TCP localhost:5000 (LISTEN)

    .. tab:: ``netstat`` (Windows)

        .. code-block:: text

            > netstat -ano | findstr 5000
            TCP 127.0.0.1:5000 0.0.0.0:0 LISTENING 6847

macOS Monterey và các phiên bản mới hơn tự động khởi động một dịch vụ sử dụng cổng
5000. Bạn có thể chọn tắt dịch vụ này thay vì sử dụng một cổng khác bằng cách
tìm kiếm "AirPlay Receiver" trong System Settings và tắt nó đi.


Lỗi Hoãn lại khi Tải lại (Deferred Errors on Reload)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Khi sử dụng lệnh ``flask run`` với reloader, máy chủ sẽ
tiếp tục chạy ngay cả khi bạn đưa ra lỗi cú pháp hoặc các
lỗi khởi tạo khác vào mã. Truy cập trang web sẽ hiển thị
debugger tương tác cho lỗi, thay vì làm crash máy chủ.

Nếu lỗi cú pháp đã tồn tại khi gọi ``flask run``, nó sẽ
thất bại ngay lập tức và hiển thị traceback thay vì chờ đợi cho đến khi
trang web được truy cập. Điều này nhằm làm cho các lỗi dễ thấy hơn ban đầu
trong khi vẫn cho phép máy chủ xử lý các lỗi khi tải lại.


Trong Mã
---------

Máy chủ phát triển cũng có thể được khởi động từ Python với phương thức :meth:`Flask.run`
. Phương thức này nhận các đối số tương tự như các tùy chọn CLI để kiểm soát máy chủ.
Sự khác biệt chính so với lệnh CLI là máy chủ sẽ crash nếu có
lỗi khi tải lại. ``debug=True`` có thể được truyền để bật chế độ debug.

Đặt cuộc gọi trong một khối main, nếu không nó sẽ can thiệp khi cố gắng import và
chạy ứng dụng với một máy chủ production sau này.

.. code-block:: python

    if __name__ == "__main__":
        app.run(debug=True)

.. code-block:: text

    $ python hello.py
