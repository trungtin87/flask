eventlet
========

Ưu tiên sử dụng :doc:`gunicorn` với các worker eventlet hơn là sử dụng
`eventlet`_ trực tiếp. Gunicorn cung cấp một máy chủ có thể cấu hình hơn nhiều và
đã được kiểm thử trong sản xuất.

`eventlet`_ cho phép viết mã bất đồng bộ, dựa trên coroutine trông
giống như Python đồng bộ tiêu chuẩn. Nó sử dụng `greenlet`_ để cho phép chuyển đổi
tác vụ mà không cần viết ``async/await`` hoặc sử dụng ``asyncio``.

:doc:`gevent` là một thư viện khác làm điều tương tự. Một số
phụ thuộc bạn có, hoặc các cân nhắc khác, có thể ảnh hưởng đến việc bạn chọn sử dụng
cái nào trong hai cái.

eventlet cung cấp một máy chủ WSGI có thể xử lý nhiều kết nối cùng một lúc
thay vì một kết nối trên mỗi worker process. Bạn thực sự phải sử dụng eventlet trong
mã của riêng bạn để thấy bất kỳ lợi ích nào khi sử dụng máy chủ.

.. _eventlet: https://eventlet.net/
.. _greenlet: https://greenlet.readthedocs.io/en/latest/


Cài đặt
-------

Khi sử dụng eventlet, yêu cầu greenlet>=1.0, nếu không các biến cục bộ ngữ cảnh
như ``request`` sẽ không hoạt động như mong đợi. Khi sử dụng PyPy,
yêu cầu PyPy>=7.3.7.

Tạo một virtualenv, cài đặt ứng dụng của bạn, sau đó cài đặt
``eventlet``.

.. code-block:: text

    $ cd hello-app
    $ python -m venv .venv
    $ . .venv/bin/activate
    $ pip install .  # cài đặt ứng dụng của bạn
    $ pip install eventlet


Chạy
----

Để sử dụng eventlet để phục vụ ứng dụng của bạn, hãy viết một script import
``wsgi.server`` của nó, cũng như ứng dụng hoặc app factory của bạn.

.. code-block:: python
    :caption: ``wsgi.py``

    import eventlet
    from eventlet import wsgi
    from hello import create_app

    app = create_app()
    wsgi.server(eventlet.listen(("127.0.0.1", 8000)), app)

.. code-block:: text

    $ python wsgi.py
    (x) wsgi starting up on http://127.0.0.1:8000


Binding Bên ngoài
-----------------

eventlet không nên được chạy dưới quyền root vì nó sẽ khiến
mã ứng dụng của bạn chạy dưới quyền root, điều này không an toàn. Tuy nhiên, điều này
có nghĩa là sẽ không thể bind vào cổng 80 hoặc 443. Thay vào đó, một
reverse proxy như :doc:`nginx` hoặc :doc:`apache-httpd` nên được sử dụng
phía trước eventlet.

Bạn có thể bind vào tất cả các IP bên ngoài trên một cổng không có đặc quyền bằng cách sử dụng
``0.0.0.0`` trong các đối số máy chủ được hiển thị trong phần trước.
Đừng làm điều này khi sử dụng thiết lập reverse proxy, nếu không sẽ
có thể bỏ qua proxy.

``0.0.0.0`` không phải là một địa chỉ hợp lệ để điều hướng đến, bạn sẽ sử dụng một
địa chỉ IP cụ thể trong trình duyệt của mình.
