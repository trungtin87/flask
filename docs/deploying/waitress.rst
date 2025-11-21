Waitress
========

`Waitress`_ là một máy chủ WSGI thuần Python.

*   Nó dễ cấu hình.
*   Nó hỗ trợ Windows trực tiếp.
*   Nó dễ cài đặt vì nó không yêu cầu các phụ thuộc bổ sung
    hoặc biên dịch.
*   Nó không hỗ trợ streaming requests, dữ liệu request đầy đủ luôn được
    lưu vào bộ đệm.
*   Nó sử dụng một process duy nhất với nhiều thread worker.

Trang này phác thảo những điều cơ bản về việc chạy Waitress. Hãy chắc chắn đọc
tài liệu của nó và ``waitress-serve --help`` để hiểu những tính năng nào
có sẵn.

.. _Waitress: https://docs.pylonsproject.org/projects/waitress/


Cài đặt
-------

Tạo một virtualenv, cài đặt ứng dụng của bạn, sau đó cài đặt
``waitress``.

.. code-block:: text

    $ cd hello-app
    $ python -m venv .venv
    $ . .venv/bin/activate
    $ pip install .  # cài đặt ứng dụng của bạn
    $ pip install waitress


Chạy
----

Đối số bắt buộc duy nhất cho ``waitress-serve`` cho nó biết cách tải
ứng dụng Flask của bạn. Cú pháp là ``{module}:{app}``. ``module`` là
tên import có dấu chấm đến module chứa ứng dụng của bạn. ``app`` là
biến chứa ứng dụng. Nếu bạn đang sử dụng mẫu app factory,
hãy sử dụng ``--call {module}:{factory}`` thay thế.

.. code-block:: text

    # tương đương với 'from hello import app'
    $ waitress-serve --host 127.0.0.1 hello:app

    # tương đương với 'from hello import create_app; create_app()'
    $ waitress-serve --host 127.0.0.1 --call hello:create_app

    Serving on http://127.0.0.1:8080

Tùy chọn ``--host`` liên kết máy chủ với ``127.0.0.1`` cục bộ.

Logs cho mỗi request không được hiển thị, chỉ các lỗi được hiển thị. Logging có thể
được cấu hình thông qua giao diện Python thay vì dòng lệnh.


Binding Bên ngoài
-----------------

Waitress không nên được chạy dưới quyền root vì nó sẽ khiến
mã ứng dụng của bạn chạy dưới quyền root, điều này không an toàn. Tuy nhiên, điều này
có nghĩa là sẽ không thể bind vào cổng 80 hoặc 443. Thay vào đó, một
reverse proxy như :doc:`nginx` hoặc :doc:`apache-httpd` nên được sử dụng
phía trước Waitress.

Bạn có thể bind vào tất cả các IP bên ngoài trên một cổng không có đặc quyền bằng cách không
chỉ định tùy chọn ``--host``. Đừng làm điều này khi sử dụng thiết lập reverse
proxy, nếu không sẽ có thể bỏ qua proxy.

``0.0.0.0`` không phải là một địa chỉ hợp lệ để điều hướng đến, bạn sẽ sử dụng một
địa chỉ IP cụ thể trong trình duyệt của mình.
