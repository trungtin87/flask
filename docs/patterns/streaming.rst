Streaming Contents
==================

Đôi khi bạn muốn gửi một lượng dữ liệu khổng lồ đến client, nhiều hơn
nhiều so với những gì bạn muốn giữ trong bộ nhớ. Khi bạn đang tạo dữ liệu ngay lập tức
, làm thế nào để bạn gửi lại cho client mà không cần
vòng quay đến hệ thống tệp?

Câu trả lời là bằng cách sử dụng generator và phản hồi trực tiếp.

Sử dụng Cơ bản
--------------

Đây là một view function cơ bản tạo ra rất nhiều dữ liệu CSV ngay lập tức.
Mẹo là có một hàm bên trong sử dụng một generator để tạo
dữ liệu và sau đó gọi hàm đó và truyền nó cho một đối tượng phản hồi::

    @app.route('/large.csv')
    def generate_large_csv():
        def generate():
            for row in iter_all_rows():
                yield f"{','.join(row)}\n"
        return generate(), {"Content-Type": "text/csv"}

Mỗi biểu thức ``yield`` được gửi trực tiếp đến trình duyệt. Tuy nhiên lưu ý
rằng một số WSGI middleware có thể phá vỡ streaming, vì vậy hãy cẩn thận ở đó trong
các môi trường debug với profiler và những thứ khác bạn có thể đã bật.

Streaming từ Template
---------------------

Engine template Jinja hỗ trợ render một template từng
phần, trả về một iterator của các chuỗi. Flask cung cấp các hàm
:func:`~flask.stream_template` và :func:`~flask.stream_template_string`
để làm cho điều này dễ sử dụng hơn.

.. code-block:: python

    from flask import stream_template

    @app.get("/timeline")
    def timeline():
        return stream_template("timeline.html")

Các phần được yield bởi render stream có xu hướng khớp với các khối câu lệnh trong
template.


Streaming với Context
---------------------

Proxy :data:`.request` sẽ không hoạt động trong khi generator đang
chạy, vì ứng dụng đã trả lại quyền kiểm soát cho máy chủ WSGI tại thời điểm đó.
Nếu bạn cố gắng truy cập ``request``, bạn sẽ nhận được một ``RuntimeError``.

Nếu hàm generator của bạn dựa vào dữ liệu trong ``request``, hãy sử dụng
wrapper :func:`.stream_with_context`. Điều này sẽ giữ ngữ cảnh request hoạt động
trong suốt generator.

.. code-block:: python

    from flask import stream_with_context, request
    from markupsafe import escape

    @app.route('/stream')
    def streamed_response():
        def generate():
            yield '<p>Hello '
            yield escape(request.args['name'])
            yield '!</p>'
        return stream_with_context(generate())

Nó cũng có thể được sử dụng như một decorator.

.. code-block:: python

    @stream_with_context
    def generate():
        ...

    return generate()

Các hàm :func:`~flask.stream_template` và
:func:`~flask.stream_template_string` tự động
sử dụng :func:`~flask.stream_with_context` nếu một request đang hoạt động.
