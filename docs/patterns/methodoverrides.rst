Thêm HTTP Method Overrides
==========================

Một số HTTP proxy không hỗ trợ các phương thức HTTP tùy ý hoặc các phương thức HTTP
mới hơn (chẳng hạn như PATCH). Trong trường hợp đó, có thể "proxy" các phương thức
HTTP thông qua một phương thức HTTP khác vi phạm hoàn toàn giao thức.

Cách thức hoạt động là để client thực hiện một HTTP POST request và
đặt header ``X-HTTP-Method-Override``. Sau đó phương thức được thay thế
bằng giá trị header trước khi được truyền cho Flask.

Điều này có thể được thực hiện với một HTTP middleware::

    class HTTPMethodOverrideMiddleware(object):
        allowed_methods = frozenset([
            'GET',
            'HEAD',
            'POST',
            'DELETE',
            'PUT',
            'PATCH',
            'OPTIONS'
        ])
        bodyless_methods = frozenset(['GET', 'HEAD', 'OPTIONS', 'DELETE'])

        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            method = environ.get('HTTP_X_HTTP_METHOD_OVERRIDE', '').upper()
            if method in self.allowed_methods:
                environ['REQUEST_METHOD'] = method
            if method in self.bodyless_methods:
                environ['CONTENT_LENGTH'] = '0'
            return self.app(environ, start_response)

Để sử dụng điều này với Flask, hãy bao bọc đối tượng app với middleware::

    from flask import Flask

    app = Flask(__name__)
    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)
