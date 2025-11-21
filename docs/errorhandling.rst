Xử Lý Lỗi Ứng Dụng
=====================

Các ứng dụng luôn có khả năng gặp lỗi, và Flask cũng không ngoại lệ. Khi một ngoại lệ xảy ra trong môi trường production, Flask sẽ ghi lại lỗi vào logger và trả về một trang lỗi đơn giản. Tuy nhiên, bạn có thể tùy chỉnh cách xử lý lỗi để cung cấp trải nghiệm người dùng tốt hơn và tích hợp các công cụ giám sát.

.. _error-logging-tools:

Công Cụ Ghi Nhận Lỗi
----------------------

Việc gửi email khi có lỗi nghiêm trọng có thể gây quá tải nếu có nhiều người dùng gặp lỗi. Đối với việc này, chúng tôi khuyến nghị sử dụng `Sentry <https://sentry.io/>`_ để quản lý lỗi ứng dụng. Sentry là một dự án nguồn mở trên `GitHub <https://github.com/getsentry/sentry>`_ và cũng có phiên bản dịch vụ được host miễn phí. Sentry sẽ gom các lỗi trùng lặp, lưu lại stack trace và biến cục bộ, và gửi email dựa trên các ngưỡng bạn thiết lập.

Để sử dụng Sentry, cài đặt client ``sentry-sdk`` với phần mở rộng ``flask``:

.. code-block:: text

    $ pip install sentry-sdk[flask]

Sau đó thêm đoạn code sau vào ứng dụng Flask của bạn:

.. code-block:: python

    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    sentry_sdk.init('YOUR_DSN_HERE', integrations=[FlaskIntegration()])

Thay ``YOUR_DSN_HERE`` bằng DSN bạn nhận được từ Sentry.

.. _error-handlers:

Xử Lý Lỗi (Error Handlers)
----------------------------

Khi một lỗi xảy ra trong Flask, một mã trạng thái HTTP thích hợp sẽ được trả về. Các mã 400-499 cho lỗi phía client, 500-599 cho lỗi phía server.

Bạn có thể đăng ký các hàm xử lý lỗi để trả về trang tùy chỉnh cho người dùng. Hàm xử lý lỗi nhận một đối tượng lỗi (thường là ``werkzeug.exceptions.HTTPException``) và trả về một phản hồi.

.. code-block:: python

    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def handle_bad_request(e):
        return 'Yêu cầu không hợp lệ!', 400

    # Hoặc đăng ký sau này
    app.register_error_handler(400, handle_bad_request)

Lưu ý rằng khi trả về phản hồi, bạn cần chỉ định mã trạng thái HTTP.

Các mã lỗi không chuẩn không thể đăng ký bằng số vì Werkzeug không biết chúng. Thay vào đó, tạo một subclass của ``HTTPException`` với mã và mô tả tùy chỉnh, sau đó đăng ký và raise.

.. code-block:: python

    class InsufficientStorage(werkzeug.exceptions.HTTPException):
        code = 507
        description = 'Không đủ không gian lưu trữ.'

    app.register_error_handler(InsufficientStorage, handle_507)
    raise InsufficientStorage()

Bạn có thể đăng ký handler cho bất kỳ lớp ngoại lệ nào, không chỉ ``HTTPException``.

.. _handling-exceptions:

Xử Lý Ngoại Lệ (Handling Exceptions)
--------------------------------------

Nếu không có handler nào được đăng ký, Flask sẽ trả về trang "500 Internal Server Error" trong production và một trình gỡ lỗi tương tác trong debug mode.

Bạn có thể đăng ký handler cho ``Exception`` để bắt mọi lỗi không được xử lý, nhưng cần cẩn thận để không bắt các lỗi HTTP và làm mất thông tin mã trạng thái.

.. code-block:: python

    @app.errorhandler(Exception)
    def handle_all_exceptions(e):
        if isinstance(e, werkzeug.exceptions.HTTPException):
            return e
        return render_template('500_generic.html', e=e), 500

.. _unhandled-exceptions:

Ngoại Lệ Không Được Xử Lý (Unhandled Exceptions)
-------------------------------------------------

Khi không có handler cho một ngoại lệ, Flask sẽ gọi ``flask.Flask.handle_exception`` và trả về 500. Nếu bạn đăng ký handler cho ``InternalServerError``, Flask sẽ truyền cho nó một instance của ``InternalServerError`` chứ không phải ngoại lệ gốc. Bạn có thể truy cập ngoại lệ gốc qua ``e.original_exception``.

.. _custom-error-pages:

Trang Lỗi Tùy Chỉnh (Custom Error Pages)
----------------------------------------

Bạn có thể tạo các template HTML cho các lỗi cụ thể, ví dụ ``404.html`` và ``500.html``.

.. code-block:: python

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('500.html'), 500

Khi sử dụng pattern ``appfactory`` (factory pattern), bạn có thể đăng ký các handler trong hàm ``create_app`` và trả về app.

.. code-block:: python

    def create_app():
        app = Flask(__name__)
        app.register_error_handler(404, page_not_found)
        app.register_error_handler(500, internal_error)
        return app

.. _blueprint-error-handlers:

Xử Lý Lỗi trong Blueprint (Blueprint Error Handlers)
------------------------------------------------------

Trong blueprint, các handler thường hoạt động như bình thường, nhưng có một ngoại lệ: các lỗi 404 và 405 không được gọi khi URL không khớp với bất kỳ route nào trong blueprint. Để xử lý các lỗi này dựa trên tiền tố URL, bạn cần đăng ký handler ở mức ứng dụng và kiểm tra ``request.path``.

.. code-block:: python

    @app.errorhandler(404)
    def page_not_found(e):
        if request.path.startswith('/blog/'):
            return render_template('blog/404.html'), 404
        return render_template('404.html'), 404

.. _api-error-json:

Lỗi API trả về JSON (Returning API Errors as JSON)
---------------------------------------------------

Khi xây dựng API, trả về HTML cho lỗi không hữu ích. Bạn có thể đăng ký handler cho ``HTTPException`` để trả về JSON.

.. code-block:: python

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = e.get_response()
        response.data = json.dumps({
            'code': e.code,
            'name': e.name,
            'description': e.description,
        })
        response.content_type = 'application/json'
        return response

Bạn cũng có thể tạo các ngoại lệ tùy chỉnh cho API và trả về JSON chi tiết.

.. code-block:: python

    class InvalidAPIUsage(Exception):
        status_code = 400
        def __init__(self, message, status_code=None, payload=None):
            super().__init__()
            self.message = message
            if status_code is not None:
                self.status_code = status_code
            self.payload = payload
        def to_dict(self):
            rv = dict(self.payload or ())
            rv['message'] = self.message
            return rv

    @app.errorhandler(InvalidAPIUsage)
    def handle_invalid_api_usage(e):
        return jsonify(e.to_dict()), e.status_code

.. _logging-errors:

Ghi Nhận Lỗi (Logging)
-----------------------

Xem tài liệu :doc:`/logging` để biết cách ghi nhận lỗi, ví dụ gửi email cho admin.

.. _debugging-errors:

Gỡ Lỗi (Debugging)
--------------------

Xem tài liệu :doc:`/debugging` để biết cách gỡ lỗi trong development và production.
