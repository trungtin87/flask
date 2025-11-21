.. rst-class:: hide-header

Chào mừng đến với Flask
=======================

.. image:: _static/flask-name.svg
    :align: center
    :height: 200px

Chào mừng đến với tài liệu của Flask. Flask là một framework ứng dụng web WSGI nhẹ.
Nó được thiết kế để giúp việc bắt đầu nhanh chóng và dễ dàng, với khả năng mở rộng lên
các ứng dụng phức tạp.

Bắt đầu với :doc:`installation`
và sau đó xem tổng quan với :doc:`quickstart`. Ngoài ra còn có một
:doc:`tutorial/index` chi tiết hơn chỉ ra cách tạo một ứng dụng nhỏ nhưng
hoàn chỉnh với Flask. Các mẫu phổ biến được mô tả trong phần
:doc:`patterns/index`. Phần còn lại của tài liệu mô tả chi tiết từng
thành phần của Flask, với tham chiếu đầy đủ trong phần :doc:`api`.

Flask phụ thuộc vào bộ công cụ WSGI `Werkzeug`_, công cụ template `Jinja`_, và
bộ công cụ CLI `Click`_. Hãy chắc chắn kiểm tra tài liệu của chúng cũng như của Flask khi
tìm kiếm thông tin.

.. _Werkzeug: https://werkzeug.palletsprojects.com
.. _Jinja: https://jinja.palletsprojects.com
.. _Click: https://click.palletsprojects.com


Hướng dẫn Người dùng
--------------------

Flask cung cấp cấu hình và quy ước, với các mặc định hợp lý, để bắt đầu.
Phần này của tài liệu giải thích các phần khác nhau của framework Flask
và cách chúng có thể được sử dụng, tùy chỉnh và mở rộng. Ngoài bản thân Flask, hãy tìm kiếm
các tiện ích mở rộng do cộng đồng duy trì để thêm nhiều chức năng hơn nữa.

.. toctree::
   :maxdepth: 2

   installation
   quickstart
   tutorial/index
   templating
   testing
   errorhandling
   debugging
   logging
   config
   signals
   views
   lifecycle
   appcontext
   blueprints
   extensions
   cli
   server
   shell
   patterns/index
   web-security
   deploying/index
   async-await


Tham chiếu API
--------------

Nếu bạn đang tìm kiếm thông tin về một hàm, lớp hoặc
phương thức cụ thể, phần này của tài liệu là dành cho bạn.

.. toctree::
   :maxdepth: 2

   api


Ghi chú Bổ sung
---------------

.. toctree::
   :maxdepth: 2

   design
   extensiondev
   contributing
   license
   changes
