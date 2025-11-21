Triển khai lên Production
=========================

Phần này của tutorial giả định bạn có một máy chủ mà bạn muốn
triển khai ứng dụng của mình lên đó. Nó cung cấp cái nhìn tổng quan về cách tạo
file phân phối và cài đặt nó, nhưng sẽ không đi vào chi tiết về
máy chủ hoặc phần mềm nào để sử dụng. Bạn có thể thiết lập một môi trường mới trên
máy tính phát triển của mình để thử các hướng dẫn bên dưới, nhưng có lẽ
không nên sử dụng nó để lưu trữ một ứng dụng công khai thực sự. Xem
:doc:`/deploying/index` để có danh sách nhiều cách khác nhau để lưu trữ
ứng dụng của bạn.


Xây dựng và Cài đặt
-------------------

Khi bạn muốn triển khai ứng dụng của mình ở nơi khác, bạn xây dựng một file *wheel*
(``.whl``). Cài đặt và sử dụng công cụ ``build`` để làm điều này.

.. code-block:: none

    $ pip install build
    $ python -m build --wheel

Bạn có thể tìm thấy file trong ``dist/flaskr-1.0.0-py3-none-any.whl``. Tên
file ở định dạng {tên dự án}-{phiên bản}-{thẻ python}
-{thẻ abi}-{thẻ nền tảng}.

Sao chép file này sang một máy khác,
:ref:`thiết lập một virtualenv mới <install-create-env>`, sau đó cài đặt
file với ``pip``.

.. code-block:: none

    $ pip install flaskr-1.0.0-py3-none-any.whl

Pip sẽ cài đặt dự án của bạn cùng với các dependency của nó.

Vì đây là một máy khác, bạn cần chạy ``init-db`` lại để
tạo cơ sở dữ liệu trong instance folder.

    .. code-block:: text

        $ flask --app flaskr init-db

Khi Flask phát hiện rằng nó đã được cài đặt (không ở chế độ editable), nó sử dụng
một thư mục khác cho instance folder. Bạn có thể tìm thấy nó tại
``.venv/var/flaskr-instance`` thay thế.


Cấu hình Secret Key
-------------------

Ở đầu tutorial, bạn đã đưa ra một giá trị mặc định cho
:data:`SECRET_KEY`. Điều này nên được thay đổi thành một số byte ngẫu nhiên trong
production. Nếu không, kẻ tấn công có thể sử dụng khóa ``'dev'`` công khai để
sửa đổi session cookie, hoặc bất cứ thứ gì khác sử dụng secret key.

Bạn có thể sử dụng lệnh sau để xuất ra một secret key ngẫu nhiên:

.. code-block:: none

    $ python -c 'import secrets; print(secrets.token_hex())'

    '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'

Tạo file ``config.py`` trong instance folder, mà factory
sẽ đọc từ đó nếu nó tồn tại. Sao chép giá trị được tạo vào đó.

.. code-block:: python
    :caption: ``.venv/var/flaskr-instance/config.py``

    SECRET_KEY = '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'

Bạn cũng có thể đặt bất kỳ cấu hình cần thiết nào khác ở đây, mặc dù
``SECRET_KEY`` là cấu hình duy nhất cần thiết cho Flaskr.


Chạy với Máy chủ Production
---------------------------

Khi chạy công khai thay vì trong phát triển, bạn không nên sử dụng
máy chủ phát triển tích hợp sẵn (``flask run``). Máy chủ phát triển được
cung cấp bởi Werkzeug để thuận tiện, nhưng không được thiết kế để
đặc biệt hiệu quả, ổn định hoặc an toàn.

Thay vào đó, hãy sử dụng một máy chủ WSGI production. Ví dụ, để sử dụng `Waitress`_,
trước tiên hãy cài đặt nó trong môi trường ảo:

.. code-block:: none

    $ pip install waitress

Bạn cần cho Waitress biết về ứng dụng của mình, nhưng nó không sử dụng
``--app`` như ``flask run``. Bạn cần cho nó biết import và
gọi application factory để lấy một đối tượng ứng dụng.

.. code-block:: none

    $ waitress-serve --call 'flaskr:create_app'

    Serving on http://0.0.0.0:8080

Xem :doc:`/deploying/index` để có danh sách nhiều cách khác nhau để lưu trữ
ứng dụng của bạn. Waitress chỉ là một ví dụ, được chọn cho tutorial
vì nó hỗ trợ cả Windows và Linux. Có nhiều máy chủ WSGI
và tùy chọn triển khai hơn mà bạn có thể chọn cho dự án của mình.

.. _Waitress: https://docs.pylonsproject.org/projects/waitress/en/stable/

Tiếp tục đến :doc:`next`.
