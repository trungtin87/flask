ASGI
====

Nếu bạn muốn sử dụng một máy chủ ASGI bạn sẽ cần sử dụng middleware WSGI sang
ASGI. Adapter asgiref
`WsgiToAsgi <https://github.com/django/asgiref#wsgi-to-asgi-adapter>`_
được khuyến nghị vì nó tích hợp với vòng lặp sự kiện được sử dụng cho
hỗ trợ :ref:`async_await` của Flask. Bạn có thể sử dụng adapter bằng cách
bao bọc ứng dụng Flask,

.. code-block:: python

    from asgiref.wsgi import WsgiToAsgi
    from flask import Flask

    app = Flask(__name__)

    ...

    asgi_app = WsgiToAsgi(app)

và sau đó phục vụ ``asgi_app`` với máy chủ ASGI, ví dụ sử dụng
`Hypercorn <https://github.com/pgjones/hypercorn>`_,

.. sourcecode:: text

    $ hypercorn module:asgi_app
