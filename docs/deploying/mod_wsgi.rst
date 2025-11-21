mod_wsgi
========

`mod_wsgi`_ là một máy chủ WSGI được tích hợp với máy chủ `Apache httpd`_.
Lệnh `mod_wsgi-express`_ hiện đại giúp dễ dàng cấu hình và
khởi động máy chủ mà không cần viết cấu hình Apache httpd.

*   Tích hợp chặt chẽ với Apache httpd.
*   Hỗ trợ Windows trực tiếp.
*   Yêu cầu trình biên dịch và các header phát triển Apache để cài đặt.
*   Không yêu cầu thiết lập reverse proxy.

Trang này phác thảo những điều cơ bản về việc chạy mod_wsgi-express, không phải
việc cài đặt và cấu hình phức tạp hơn với httpd. Hãy chắc chắn đọc tài liệu
`mod_wsgi-express`_, `mod_wsgi`_, và `Apache httpd`_ để
hiểu những tính năng nào có sẵn.

.. _mod_wsgi-express: https://pypi.org/project/mod-wsgi/
.. _mod_wsgi: https://modwsgi.readthedocs.io/
.. _Apache httpd: https://httpd.apache.org/


Cài đặt
-------

Cài đặt mod_wsgi yêu cầu trình biên dịch và máy chủ Apache và
các header phát triển được cài đặt. Bạn sẽ nhận được lỗi nếu chúng không có.
Cách cài đặt chúng phụ thuộc vào hệ điều hành và trình quản lý gói mà bạn sử dụng.

Tạo một virtualenv, cài đặt ứng dụng của bạn, sau đó cài đặt
``mod_wsgi``.

.. code-block:: text

    $ cd hello-app
    $ python -m venv .venv
    $ . .venv/bin/activate
    $ pip install .  # cài đặt ứng dụng của bạn
    $ pip install mod_wsgi


Chạy
----

Đối số duy nhất cho ``mod_wsgi-express`` chỉ định một script chứa
ứng dụng Flask của bạn, phải được gọi là ``application``. Bạn có thể
viết một script nhỏ để import ứng dụng của bạn với tên này, hoặc để tạo nó
nếu sử dụng mẫu app factory.

.. code-block:: python
    :caption: ``wsgi.py``

    from hello import app

    application = app

.. code-block:: python
    :caption: ``wsgi.py``

    from hello import create_app

    application = create_app()

Bây giờ chạy lệnh ``mod_wsgi-express start-server``.

.. code-block:: text

    $ mod_wsgi-express start-server wsgi.py --processes 4

Tùy chọn ``--processes`` chỉ định số lượng worker process để
chạy; một giá trị khởi đầu có thể là ``CPU * 2``.

Logs cho mỗi request không được hiển thị trong terminal. Nếu một lỗi xảy ra,
thông tin của nó được ghi vào file error log được hiển thị khi khởi động
máy chủ.


Binding Bên ngoài
-----------------

Không giống như các máy chủ WSGI khác trong các tài liệu này, mod_wsgi có thể được chạy dưới quyền
root để bind vào các cổng đặc quyền như 80 và 443. Tuy nhiên, nó phải được
cấu hình để giảm quyền xuống một người dùng và nhóm khác cho các
worker process.

Ví dụ, nếu bạn tạo một người dùng và nhóm ``hello``, bạn nên
cài đặt virtualenv và ứng dụng của bạn dưới quyền người dùng đó, sau đó bảo
mod_wsgi giảm xuống người dùng đó sau khi khởi động.

.. code-block:: text

    $ sudo /home/hello/.venv/bin/mod_wsgi-express start-server \
        /home/hello/wsgi.py \
        --user hello --group hello --port 80 --processes 4
