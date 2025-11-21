uWSGI
=====

`uWSGI`_ là một bộ máy chủ được biên dịch nhanh chóng với cấu hình mở rộng
và các khả năng vượt ra ngoài một máy chủ cơ bản.

*   Nó có thể rất hiệu quả do là một chương trình được biên dịch.
*   Nó phức tạp để cấu hình vượt ra ngoài ứng dụng cơ bản, và có quá
    nhiều tùy chọn khiến người mới bắt đầu khó hiểu.
*   Nó không hỗ trợ Windows (nhưng chạy trên WSL).
*   Nó yêu cầu một trình biên dịch để cài đặt trong một số trường hợp.

Trang này phác thảo những điều cơ bản về việc chạy uWSGI. Hãy chắc chắn đọc
tài liệu của nó để hiểu những tính năng nào có sẵn.

.. _uWSGI: https://uwsgi-docs.readthedocs.io/en/latest/


Cài đặt
-------

uWSGI có nhiều cách để cài đặt nó. Cách đơn giản nhất là
cài đặt package ``pyuwsgi``, cung cấp các wheel được biên dịch sẵn cho
các nền tảng phổ biến. Tuy nhiên, nó không cung cấp hỗ trợ SSL, cái mà có thể được
cung cấp với một reverse proxy thay thế.

Tạo một virtualenv, cài đặt ứng dụng của bạn, sau đó cài đặt ``pyuwsgi``.

.. code-block:: text

    $ cd hello-app
    $ python -m venv .venv
    $ . .venv/bin/activate
    $ pip install .  # cài đặt ứng dụng của bạn
    $ pip install pyuwsgi

Nếu bạn có sẵn một trình biên dịch, bạn có thể cài đặt package ``uwsgi``
thay thế. Hoặc cài đặt package ``pyuwsgi`` từ sdist thay vì wheel.
Cả hai phương pháp sẽ bao gồm hỗ trợ SSL.

.. code-block:: text

    $ pip install uwsgi

    # hoặc
    $ pip install --no-binary pyuwsgi pyuwsgi


Chạy
----

Cách cơ bản nhất để chạy uWSGI là bảo nó khởi động một máy chủ HTTP
và import ứng dụng của bạn.

.. code-block:: text

    $ uwsgi --http 127.0.0.1:8000 --master -p 4 -w hello:app

    *** Starting uWSGI 2.0.20 (64bit) on [x] ***
    *** Operational MODE: preforking ***
    mounting hello:app on /
    spawned uWSGI master process (pid: x)
    spawned uWSGI worker 1 (pid: x, cores: 1)
    spawned uWSGI worker 2 (pid: x, cores: 1)
    spawned uWSGI worker 3 (pid: x, cores: 1)
    spawned uWSGI worker 4 (pid: x, cores: 1)
    spawned uWSGI http 1 (pid: x)

Nếu bạn đang sử dụng mẫu app factory, bạn sẽ cần tạo một
file Python nhỏ để tạo ứng dụng, sau đó trỏ uWSGI vào đó.

.. code-block:: python
    :caption: ``wsgi.py``

    from hello import create_app

    app = create_app()

.. code-block:: text

    $ uwsgi --http 127.0.0.1:8000 --master -p 4 -w wsgi:app

Tùy chọn ``--http`` khởi động một máy chủ HTTP tại 127.0.0.1 cổng 8000.
Tùy chọn ``--master`` chỉ định trình quản lý worker tiêu chuẩn. Tùy chọn ``-p``
khởi động 4 worker process; một giá trị khởi đầu có thể là ``CPU * 2``.
Tùy chọn ``-w`` bảo uWSGI cách import ứng dụng của bạn


Binding Bên ngoài
-----------------

uWSGI không nên được chạy dưới quyền root với cấu hình được hiển thị trong tài liệu này
vì nó sẽ khiến mã ứng dụng của bạn chạy dưới quyền root, điều này không
an toàn. Tuy nhiên, điều này có nghĩa là sẽ không thể bind vào cổng
80 hoặc 443. Thay vào đó, một reverse proxy như :doc:`nginx` hoặc
:doc:`apache-httpd` nên được sử dụng phía trước uWSGI. Có thể
chạy uWSGI dưới quyền root một cách an toàn, nhưng điều đó nằm ngoài phạm vi của tài liệu này.

uWSGI có tích hợp tối ưu hóa với `Nginx uWSGI`_ và
`Apache mod_proxy_uwsgi`_, và có thể các máy chủ khác, thay vì sử dụng
một proxy HTTP tiêu chuẩn. Cấu hình đó nằm ngoài phạm vi của tài liệu
này, xem các liên kết để biết thêm thông tin.

.. _Nginx uWSGI: https://uwsgi-docs.readthedocs.io/en/latest/Nginx.html
.. _Apache mod_proxy_uwsgi: https://uwsgi-docs.readthedocs.io/en/latest/Apache.html#mod-proxy-uwsgi

Bạn có thể bind vào tất cả các IP bên ngoài trên một cổng không có đặc quyền bằng cách sử dụng
tùy chọn ``--http 0.0.0.0:8000``. Đừng làm điều này khi sử dụng thiết lập reverse proxy,
nếu không sẽ có thể bỏ qua proxy.

.. code-block:: text

    $ uwsgi --http 0.0.0.0:8000 --master -p 4 -w wsgi:app

``0.0.0.0`` không phải là một địa chỉ hợp lệ để điều hướng đến, bạn sẽ sử dụng một
địa chỉ IP cụ thể trong trình duyệt của mình.


Async với gevent
----------------

Sync worker mặc định phù hợp cho nhiều trường hợp sử dụng. Nếu bạn cần
hỗ trợ bất đồng bộ, uWSGI cung cấp một worker `gevent`_. Điều này không
giống như ``async/await`` của Python, hoặc đặc tả máy chủ ASGI. Bạn phải
thực sự sử dụng gevent trong mã của riêng bạn để thấy bất kỳ lợi ích nào khi sử dụng
worker.

Khi sử dụng gevent, yêu cầu greenlet>=1.0, nếu không các biến cục bộ ngữ cảnh
như ``request`` sẽ không hoạt động như mong đợi. Khi sử dụng PyPy,
yêu cầu PyPy>=7.3.7.

.. code-block:: text

    $ uwsgi --http 127.0.0.1:8000 --master --gevent 100 -w wsgi:app

    *** Starting uWSGI 2.0.20 (64bit) on [x] ***
    *** Operational MODE: async ***
    mounting hello:app on /
    spawned uWSGI master process (pid: x)
    spawned uWSGI worker 1 (pid: x, cores: 100)
    spawned uWSGI http 1 (pid: x)
    *** running gevent loop engine [addr:x] ***


.. _gevent: https://www.gevent.org/
