Gunicorn
========

`Gunicorn`_ là một máy chủ WSGI thuần Python với cấu hình đơn giản và
nhiều triển khai worker để điều chỉnh hiệu suất.

*   Nó có xu hướng tích hợp dễ dàng với các nền tảng lưu trữ.
*   Nó không hỗ trợ Windows (nhưng chạy trên WSL).
*   Nó dễ cài đặt vì nó không yêu cầu các phụ thuộc bổ sung
    hoặc biên dịch.
*   Nó có hỗ trợ worker async tích hợp sử dụng gevent hoặc eventlet.

Trang này phác thảo những điều cơ bản về việc chạy Gunicorn. Hãy chắc chắn đọc
`tài liệu`_ của nó và sử dụng ``gunicorn --help`` để hiểu những tính năng nào
có sẵn.

.. _Gunicorn: https://gunicorn.org/
.. _documentation: https://docs.gunicorn.org/


Cài đặt
-------

Gunicorn dễ cài đặt, vì nó không yêu cầu các phụ thuộc bên ngoài
hoặc biên dịch. Nó chỉ chạy trên Windows dưới WSL.

Tạo một virtualenv, cài đặt ứng dụng của bạn, sau đó cài đặt
``gunicorn``.

.. code-block:: text

    $ cd hello-app
    $ python -m venv .venv
    $ . .venv/bin/activate
    $ pip install .  # cài đặt ứng dụng của bạn
    $ pip install gunicorn


Chạy
----

Đối số bắt buộc duy nhất cho Gunicorn cho nó biết cách tải ứng dụng Flask
của bạn. Cú pháp là ``{module_import}:{app_variable}``.
``module_import`` là tên import có dấu chấm đến module chứa
ứng dụng của bạn. ``app_variable`` là biến chứa ứng dụng. Nó
cũng có thể là một cuộc gọi hàm (với bất kỳ đối số nào) nếu bạn đang sử dụng
mẫu app factory.

.. code-block:: text

    # tương đương với 'from hello import app'
    $ gunicorn -w 4 'hello:app'

    # tương đương với 'from hello import create_app; create_app()'
    $ gunicorn -w 4 'hello:create_app()'

    Starting gunicorn 20.1.0
    Listening at: http://127.0.0.1:8000 (x)
    Using worker: sync
    Booting worker with pid: x
    Booting worker with pid: x
    Booting worker with pid: x
    Booting worker with pid: x

Tùy chọn ``-w`` chỉ định số lượng process để chạy; một giá trị khởi đầu
có thể là ``CPU * 2``. Mặc định chỉ là 1 worker, điều này
có lẽ không phải là những gì bạn muốn cho loại worker mặc định.

Logs cho mỗi request không được hiển thị theo mặc định, chỉ thông tin worker và
lỗi được hiển thị. Để hiển thị access logs trên stdout, sử dụng
tùy chọn ``--access-logfile=-``.


Binding Bên ngoài
-----------------

Gunicorn không nên được chạy dưới quyền root vì nó sẽ khiến
mã ứng dụng của bạn chạy dưới quyền root, điều này không an toàn. Tuy nhiên, điều này
có nghĩa là sẽ không thể bind vào cổng 80 hoặc 443. Thay vào đó, một
reverse proxy như :doc:`nginx` hoặc :doc:`apache-httpd` nên được sử dụng
phía trước Gunicorn.

Bạn có thể bind vào tất cả các IP bên ngoài trên một cổng không có đặc quyền bằng cách sử dụng
tùy chọn ``-b 0.0.0.0``. Đừng làm điều này khi sử dụng thiết lập reverse proxy,
nếu không sẽ có thể bỏ qua proxy.

.. code-block:: text

    $ gunicorn -w 4 -b 0.0.0.0 'hello:create_app()'
    Listening at: http://0.0.0.0:8000 (x)

``0.0.0.0`` không phải là một địa chỉ hợp lệ để điều hướng đến, bạn sẽ sử dụng một
địa chỉ IP cụ thể trong trình duyệt của mình.


Async với gevent hoặc eventlet
------------------------------

Sync worker mặc định phù hợp cho nhiều trường hợp sử dụng. Nếu bạn cần
hỗ trợ bất đồng bộ, Gunicorn cung cấp các worker sử dụng `gevent`_
hoặc `eventlet`_. Điều này không giống như ``async/await`` của Python, hoặc
đặc tả máy chủ ASGI. Bạn thực sự phải sử dụng gevent/eventlet trong mã của riêng bạn
để thấy bất kỳ lợi ích nào khi sử dụng các worker.

Khi sử dụng gevent hoặc eventlet, yêu cầu greenlet>=1.0,
nếu không các biến cục bộ ngữ cảnh như ``request`` sẽ không hoạt động như mong đợi.
Khi sử dụng PyPy, yêu cầu PyPy>=7.3.7.

Để sử dụng gevent:

.. code-block:: text

    $ gunicorn -k gevent 'hello:create_app()'
    Starting gunicorn 20.1.0
    Listening at: http://127.0.0.1:8000 (x)
    Using worker: gevent
    Booting worker with pid: x

Để sử dụng eventlet:

.. code-block:: text

    $ gunicorn -k eventlet 'hello:create_app()'
    Starting gunicorn 20.1.0
    Listening at: http://127.0.0.1:8000 (x)
    Using worker: eventlet
    Booting worker with pid: x

.. _gevent: https://www.gevent.org/
.. _eventlet: https://eventlet.net/
