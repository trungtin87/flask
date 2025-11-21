Làm cho Dự án Có thể Cài đặt
=============================

Làm cho dự án của bạn có thể cài đặt có nghĩa là bạn có thể xây dựng một file *wheel* và cài đặt nó
trong một môi trường khác, giống như bạn đã cài đặt Flask trong môi trường dự án của mình.
Điều này làm cho việc triển khai dự án của bạn giống như cài đặt bất kỳ thư viện nào khác, vì vậy bạn đang
sử dụng tất cả các công cụ Python tiêu chuẩn để quản lý mọi thứ.

Cài đặt cũng đi kèm với các lợi ích khác có thể không rõ ràng từ
tutorial hoặc với tư cách là người dùng Python mới, bao gồm:

*   Hiện tại, Python và Flask hiểu cách sử dụng package ``flaskr``
    chỉ vì bạn đang chạy từ thư mục dự án của mình.
    Cài đặt có nghĩa là bạn có thể import nó bất kể bạn chạy từ đâu.

*   Bạn có thể quản lý các dependency của dự án giống như các package
    khác làm, vì vậy ``pip install yourproject.whl`` cài đặt chúng.

*   Các công cụ kiểm thử có thể cô lập môi trường kiểm thử của bạn khỏi môi trường phát triển
    của bạn.

.. note::
    Điều này được giới thiệu muộn trong tutorial, nhưng trong các
    dự án tương lai của bạn, bạn nên luôn bắt đầu với điều này.


Mô tả Dự án
-----------

File ``pyproject.toml`` mô tả dự án của bạn và cách xây dựng nó.

.. code-block:: toml
    :caption: ``pyproject.toml``

    [project]
    name = "flaskr"
    version = "1.0.0"
    description = "The basic blog app built in the Flask tutorial."
    dependencies = [
        "flask",
    ]

    [build-system]
    requires = ["flit_core<4"]
    build-backend = "flit_core.buildapi"

Xem `Hướng dẫn Packaging chính thức <packaging tutorial_>`_ để biết thêm
giải thích về các file và tùy chọn được sử dụng.

.. _packaging tutorial: https://packaging.python.org/tutorials/packaging-projects/


Cài đặt Dự án
-------------

Sử dụng ``pip`` để cài đặt dự án của bạn trong môi trường ảo.

.. code-block:: none

    $ pip install -e .

Điều này cho pip biết tìm ``pyproject.toml`` trong thư mục hiện tại và cài đặt
dự án ở chế độ *editable* hoặc *development*. Chế độ editable có nghĩa là khi bạn thực hiện
các thay đổi đối với mã cục bộ của mình, bạn chỉ cần cài đặt lại nếu bạn thay đổi metadata
về dự án, chẳng hạn như các dependency của nó.

Bạn có thể quan sát rằng dự án hiện đã được cài đặt với ``pip list``.

.. code-block:: none

    $ pip list

    Package        Version   Location
    -------------- --------- ----------------------------------
    click          6.7
    Flask          1.0
    flaskr         1.0.0     /home/user/Projects/flask-tutorial
    itsdangerous   0.24
    Jinja2         2.10
    MarkupSafe     1.0
    pip            9.0.3
    Werkzeug       0.14.1

Không có gì thay đổi so với cách bạn đã chạy dự án của mình cho đến nay.
``--app`` vẫn được đặt thành ``flaskr`` và ``flask run`` vẫn chạy
ứng dụng, nhưng bạn có thể gọi nó từ bất kỳ đâu, không chỉ từ
thư mục ``flask-tutorial``.

Tiếp tục đến :doc:`tests`.
