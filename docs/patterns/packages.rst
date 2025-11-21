Ứng dụng Lớn dưới dạng Package
==============================

Hãy tưởng tượng một cấu trúc ứng dụng flask đơn giản trông như thế này::

    /yourapplication
        yourapplication.py
        /static
            style.css
        /templates
            layout.html
            index.html
            login.html
            ...

Mặc dù điều này tốt cho các ứng dụng nhỏ, đối với các ứng dụng lớn hơn
nên sử dụng một package thay vì một module.
:doc:`/tutorial/index` được cấu trúc để sử dụng mẫu package,
xem :gh:`mã ví dụ <examples/tutorial>`.

Package Đơn giản
----------------

Để chuyển đổi điều đó thành một cái lớn hơn, chỉ cần tạo một thư mục mới
:file:`yourapplication` bên trong thư mục hiện có và di chuyển mọi thứ vào bên dưới nó.
Sau đó đổi tên :file:`yourapplication.py` thành :file:`__init__.py`. (Hãy chắc chắn xóa
tất cả các file ``.pyc`` trước, nếu không mọi thứ rất có thể sẽ bị hỏng)

Sau đó bạn sẽ có một cái gì đó như thế này::

    /yourapplication
        /yourapplication
            __init__.py
            /static
                style.css
            /templates
                layout.html
                index.html
                login.html
                ...

Nhưng làm thế nào để bạn chạy ứng dụng của mình bây giờ? Lệnh ngây thơ ``python
yourapplication/__init__.py`` sẽ không hoạt động. Hãy chỉ nói rằng Python
không muốn các module trong package là file khởi động. Nhưng đó không phải là
một vấn đề lớn, chỉ cần thêm một file mới có tên :file:`pyproject.toml` bên cạnh
thư mục :file:`yourapplication` bên trong với nội dung sau:

.. code-block:: toml

    [project]
    name = "yourapplication"
    dependencies = [
        "flask",
    ]

    [build-system]
    requires = ["flit_core<4"]
    build-backend = "flit_core.buildapi"

Cài đặt ứng dụng của bạn để nó có thể import được:

.. code-block:: text

    $ pip install -e .

Để sử dụng lệnh ``flask`` và chạy ứng dụng của bạn, bạn cần đặt
tùy chọn ``--app`` cho Flask biết nơi tìm instance ứng dụng:

.. code-block:: text

    $ flask --app yourapplication run

Chúng ta đã đạt được gì từ điều này? Bây giờ chúng ta có thể tái cấu trúc ứng dụng một chút
thành nhiều module. Điều duy nhất bạn phải nhớ là
danh sách kiểm tra nhanh sau:

1. việc tạo đối tượng ứng dụng `Flask` phải ở trong
   file :file:`__init__.py`. Bằng cách đó mỗi module có thể import nó một cách an toàn và
   biến `__name__` sẽ phân giải thành package chính xác.
2. tất cả các view function (những cái có decorator :meth:`~flask.Flask.route`
   ở trên) phải được import trong file :file:`__init__.py`.
   Không phải chính đối tượng, mà là module mà nó ở trong. Import module view
   **sau khi đối tượng ứng dụng được tạo**.

Đây là một ví dụ :file:`__init__.py`::

    from flask import Flask
    app = Flask(__name__)

    import yourapplication.views

Và đây là những gì :file:`views.py` sẽ trông như thế nào::

    from yourapplication import app

    @app.route('/')
    def index():
        return 'Hello World!'

Sau đó bạn sẽ có một cái gì đó như thế này::

    /yourapplication
        pyproject.toml
        /yourapplication
            __init__.py
            views.py
            /static
                style.css
            /templates
                layout.html
                index.html
                login.html
                ...

.. admonition:: Import Vòng (Circular Imports)

   Mọi lập trình viên Python đều ghét chúng, nhưng chúng ta vừa thêm một số:
   import vòng (Đó là khi hai module phụ thuộc vào nhau. Trong trường hợp
   này :file:`views.py` phụ thuộc vào :file:`__init__.py`). Hãy lưu ý rằng đây là một
   ý tưởng tồi nói chung nhưng ở đây nó thực sự ổn. Lý do cho điều này là
   chúng ta không thực sự sử dụng các view trong :file:`__init__.py` và chỉ
   đảm bảo module được import và chúng ta đang làm điều đó ở cuối
   file.


Làm việc với Blueprint
----------------------

Nếu bạn có các ứng dụng lớn hơn, nên chia chúng thành
các nhóm nhỏ hơn trong đó mỗi nhóm được triển khai với sự trợ giúp của một
blueprint. Để giới thiệu nhẹ nhàng về chủ đề này, hãy tham khảo
chương :doc:`/blueprints` của tài liệu.
