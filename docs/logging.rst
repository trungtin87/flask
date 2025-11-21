Logging
=======

Flask sử dụng :mod:`logging` Python tiêu chuẩn. Các tin nhắn về
ứng dụng Flask của bạn được ghi log với :meth:`app.logger <flask.Flask.logger>`,
nhận cùng tên với :attr:`app.name <flask.Flask.name>`. Logger
này cũng có thể được sử dụng để ghi log các tin nhắn của riêng bạn.

.. code-block:: python

    @app.route('/login', methods=['POST'])
    def login():
        user = get_user(request.form['username'])

        if user.check_password(request.form['password']):
            login_user(user)
            app.logger.info('%s logged in successfully', user.username)
            return redirect(url_for('index'))
        else:
            app.logger.info('%s failed to log in', user.username)
            abort(401)

Nếu bạn không cấu hình logging, log level mặc định của Python thường là
'warning'. Không có gì dưới level được cấu hình sẽ hiển thị.


Cấu hình Cơ bản
---------------

Khi bạn muốn cấu hình logging cho dự án của mình, bạn nên làm điều đó càng sớm
càng tốt khi chương trình khởi động. Nếu :meth:`app.logger <flask.Flask.logger>`
được truy cập trước khi logging được cấu hình, nó sẽ thêm một handler mặc định. Nếu
có thể, hãy cấu hình logging trước khi tạo đối tượng ứng dụng.

Ví dụ này sử dụng :func:`~logging.config.dictConfig` để tạo một cấu hình logging
tương tự như cấu hình mặc định của Flask, ngoại trừ cho tất cả các log::

    from logging.config import dictConfig

    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })

    app = Flask(__name__)


Cấu hình Mặc định
`````````````````

Nếu bạn không tự cấu hình logging, Flask sẽ thêm một
:class:`~logging.StreamHandler` vào :meth:`app.logger <flask.Flask.logger>`
tự động. Trong các request, nó sẽ ghi vào stream được chỉ định bởi
máy chủ WSGI trong ``environ['wsgi.errors']`` (thường là
:data:`sys.stderr`). Bên ngoài một request, nó sẽ ghi log vào :data:`sys.stderr`.


Xóa Handler Mặc định
````````````````````

Nếu bạn cấu hình logging sau khi truy cập
:meth:`app.logger <flask.Flask.logger>`, và cần xóa handler
mặc định, bạn có thể import và xóa nó::

    from flask.logging import default_handler

    app.logger.removeHandler(default_handler)


Gửi Email Lỗi cho Admin
-----------------------

Khi chạy ứng dụng trên một máy chủ remote cho production, bạn có thể
sẽ không xem các tin nhắn log thường xuyên. Máy chủ WSGI có thể sẽ
gửi các tin nhắn log vào một file, và bạn sẽ chỉ kiểm tra file đó nếu một người dùng cho
bạn biết có gì đó sai.

Để chủ động phát hiện và sửa lỗi, bạn có thể cấu hình một
:class:`logging.handlers.SMTPHandler` để gửi email khi các lỗi và cao hơn
được ghi log. ::

    import logging
    from logging.handlers import SMTPHandler

    mail_handler = SMTPHandler(
        mailhost='127.0.0.1',
        fromaddr='server-error@example.com',
        toaddrs=['admin@example.com'],
        subject='Application Error'
    )
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))

    if not app.debug:
        app.logger.addHandler(mail_handler)

Điều này yêu cầu bạn có một máy chủ SMTP được thiết lập trên cùng một máy chủ. Xem
tài liệu Python để biết thêm thông tin về cấu hình handler.


Chèn Thông tin Request
-----------------------

Xem thêm thông tin về request, chẳng hạn như địa chỉ IP, có thể giúp
gỡ lỗi một số lỗi. Bạn có thể subclass :class:`logging.Formatter` để chèn
các trường của riêng bạn có thể được sử dụng trong các tin nhắn. Bạn có thể thay đổi formatter cho
handler mặc định của Flask, mail handler được định nghĩa ở trên, hoặc bất kỳ
handler nào khác. ::

    from flask import has_request_context, request
    from flask.logging import default_handler

    class RequestFormatter(logging.Formatter):
        def format(self, record):
            if has_request_context():
                record.url = request.url
                record.remote_addr = request.remote_addr
            else:
                record.url = None
                record.remote_addr = None

            return super().format(record)

    formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )
    default_handler.setFormatter(formatter)
    mail_handler.setFormatter(formatter)


Thư viện Khác
-------------

Các thư viện khác có thể sử dụng logging rộng rãi, và bạn muốn thấy các
tin nhắn liên quan từ những log đó. Cách đơn giản nhất để làm điều này là thêm handler
vào root logger thay vì chỉ app logger. ::

    from flask.logging import default_handler

    root = logging.getLogger()
    root.addHandler(default_handler)
    root.addHandler(mail_handler)

Tùy thuộc vào dự án của bạn, có thể hữu ích hơn khi cấu hình từng logger bạn
quan tâm riêng biệt, thay vì chỉ cấu hình root logger. ::

    for logger in (
        logging.getLogger(app.name),
        logging.getLogger('sqlalchemy'),
        logging.getLogger('other_package'),
    ):
        logger.addHandler(default_handler)
        logger.addHandler(mail_handler)


Werkzeug
````````

Werkzeug ghi log thông tin request/response cơ bản vào logger ``'werkzeug'``.
Nếu root logger không có handler nào được cấu hình, Werkzeug thêm một
:class:`~logging.StreamHandler` vào logger của nó.


Flask Extension
```````````````

Tùy thuộc vào tình huống, một extension có thể chọn ghi log vào
:meth:`app.logger <flask.Flask.logger>` hoặc logger có tên riêng của nó. Tham khảo
tài liệu của từng extension để biết chi tiết.
