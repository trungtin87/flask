Extension
==========

Extension là các package bổ sung thêm chức năng cho một
ứng dụng Flask. Ví dụ, một extension có thể thêm hỗ trợ để gửi
email hoặc kết nối với cơ sở dữ liệu. Một số extension thêm toàn bộ
framework mới để giúp xây dựng các loại ứng dụng nhất định, như một REST API.


Tìm Extension
-------------

Các Flask extension thường được đặt tên là "Flask-Foo" hoặc "Foo-Flask". Bạn có thể
tìm kiếm PyPI cho các package được gắn thẻ với `Framework :: Flask <pypi_>`_.


Sử dụng Extension
-----------------

Tham khảo tài liệu của từng extension để biết hướng dẫn cài đặt, cấu hình,
và sử dụng. Nói chung, các extension lấy
cấu hình riêng của chúng từ :attr:`app.config <flask.Flask.config>` và được
truyền một instance ứng dụng trong quá trình khởi tạo. Ví dụ,
một extension có tên "Flask-Foo" có thể được sử dụng như thế này::

    from flask_foo import Foo

    foo = Foo()

    app = Flask(__name__)
    app.config.update(
        FOO_BAR='baz',
        FOO_SPAM='eggs',
    )

    foo.init_app(app)


Xây dựng Extension
------------------

Mặc dù `PyPI <pypi_>`_ chứa nhiều Flask extension, bạn có thể không tìm thấy
một extension phù hợp với nhu cầu của mình. Nếu đây là trường hợp, bạn có thể tạo
extension của riêng bạn, và publish nó cho người khác sử dụng. Đọc
:doc:`extensiondev` để phát triển Flask extension của riêng bạn.


.. _pypi: https://pypi.org/search/?c=Framework+%3A%3A+Flask
