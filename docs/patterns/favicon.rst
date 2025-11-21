Thêm một favicon
================

Một "favicon" là một biểu tượng được sử dụng bởi các trình duyệt cho các tab và bookmark. Điều này giúp
phân biệt trang web của bạn và cung cấp cho nó một thương hiệu độc đáo.

Một câu hỏi phổ biến là làm thế nào để thêm một favicon vào một ứng dụng Flask. Đầu tiên, tất
nhiên, bạn cần một biểu tượng. Nó nên là 16 × 16 pixel và ở định dạng file ICO.
Đây không phải là một yêu cầu nhưng là một tiêu chuẩn thực tế được hỗ trợ bởi tất cả
các trình duyệt liên quan. Đặt biểu tượng trong thư mục static của bạn dưới dạng
:file:`favicon.ico`.

Bây giờ, để các trình duyệt tìm thấy biểu tượng của bạn, cách chính xác là thêm một thẻ link
trong HTML của bạn. Vì vậy, ví dụ:

.. sourcecode:: html+jinja

    <link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}">

Đó là tất cả những gì bạn cần cho hầu hết các trình duyệt, tuy nhiên một số trình duyệt thực sự cũ không
hỗ trợ tiêu chuẩn này. Tiêu chuẩn thực tế cũ là phục vụ file này,
với tên này, tại thư mục gốc của trang web. Nếu ứng dụng của bạn không được gắn tại
đường dẫn gốc của tên miền, bạn cần cấu hình máy chủ web để
phục vụ biểu tượng tại thư mục gốc hoặc nếu bạn không thể làm điều đó thì bạn không may mắn. Tuy nhiên, nếu
ứng dụng của bạn là thư mục gốc, bạn có thể chỉ cần định tuyến một chuyển hướng::

    app.add_url_rule(
        "/favicon.ico",
        endpoint="favicon",
        redirect_to=url_for("static", filename="favicon.ico"),
    )

Nếu bạn muốn tiết kiệm request chuyển hướng bổ sung, bạn cũng có thể viết một view
sử dụng :func:`~flask.send_from_directory`::

    import os
    from flask import send_from_directory

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

Chúng ta có thể bỏ qua mimetype rõ ràng và nó sẽ được đoán, nhưng chúng ta cũng có thể
chỉ định nó để tránh việc đoán thêm, vì nó sẽ luôn luôn
giống nhau.

Ở trên sẽ phục vụ biểu tượng thông qua ứng dụng của bạn và nếu có thể thì
tốt hơn là cấu hình máy chủ web chuyên dụng của bạn để phục vụ nó; tham khảo
tài liệu của máy chủ web.

Xem thêm
--------

* Bài viết `Favicon <https://en.wikipedia.org/wiki/Favicon>`_ trên
  Wikipedia
