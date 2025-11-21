Gỡ lỗi Lỗi Ứng dụng
===================


Trong Production
----------------

**Không chạy máy chủ phát triển, hoặc bật debugger tích hợp sẵn, trong
môi trường production.** Debugger cho phép thực thi mã
Python tùy ý từ trình duyệt. Nó được bảo vệ bởi một pin, nhưng điều đó không
nên được dựa vào cho bảo mật.

Sử dụng một công cụ ghi log lỗi, chẳng hạn như Sentry, như được mô tả trong
:ref:`error-logging-tools`, hoặc bật logging và thông báo như
được mô tả trong :doc:`/logging`.

Nếu bạn có quyền truy cập vào máy chủ, bạn có thể thêm một số mã để khởi động một
debugger bên ngoài nếu ``request.remote_addr`` khớp với IP của bạn. Một số IDE
debugger cũng có chế độ remote để các breakpoint trên máy chủ có thể được
tương tác cục bộ. Chỉ bật debugger tạm thời.


Debugger Tích hợp sẵn
---------------------

Máy chủ phát triển Werkzeug tích hợp sẵn cung cấp một debugger hiển thị
một traceback tương tác trong trình duyệt khi một lỗi không được xử lý xảy ra
trong một request. Debugger này chỉ nên được sử dụng trong quá trình phát triển.

.. image:: _static/debugger.png
   :align: center
   :class: screenshot
   :alt: screenshot of debugger in action

.. warning::

    Debugger cho phép thực thi mã Python tùy ý từ
    trình duyệt. Nó được bảo vệ bởi một pin, nhưng vẫn đại diện cho một
    rủi ro bảo mật lớn. Không chạy máy chủ phát triển hoặc debugger trong
    môi trường production.

Debugger được bật theo mặc định khi máy chủ phát triển được chạy trong chế độ debug.

.. code-block:: text

    $ flask --app hello run --debug

Khi chạy từ mã Python, truyền ``debug=True`` bật chế độ debug, điều này
hầu như tương đương.

.. code-block:: python

    app.run(debug=True)

:doc:`/server` và :doc:`/cli` có thêm thông tin về chạy debugger và
chế độ debug. Thêm thông tin về debugger có thể được tìm thấy trong `tài liệu Werkzeug
<https://werkzeug.palletsprojects.com/debug/>`__.


Debugger Bên ngoài
------------------

Các debugger bên ngoài, chẳng hạn như những debugger được cung cấp bởi IDE, có thể cung cấp một
trải nghiệm gỡ lỗi mạnh mẽ hơn so với debugger tích hợp sẵn. Chúng cũng có thể
được sử dụng để step through mã trong một request trước khi một lỗi được đưa ra,
hoặc nếu không có lỗi nào được đưa ra. Một số thậm chí có chế độ remote để bạn có thể gỡ lỗi
mã đang chạy trên một máy khác.

Khi sử dụng một debugger bên ngoài, ứng dụng vẫn nên ở chế độ debug, nếu không Flask
chuyển các lỗi không được xử lý thành các trang lỗi 500 chung. Tuy nhiên, debugger tích hợp sẵn và
reloader nên được tắt để chúng không can thiệp vào debugger bên ngoài.

.. code-block:: text

    $ flask --app hello run --debug --no-debugger --no-reload

Khi chạy từ Python:

.. code-block:: python

    app.run(debug=True, use_debugger=False, use_reloader=False)

Tắt những thứ này không bắt buộc, một debugger bên ngoài sẽ tiếp tục hoạt động với các
lưu ý sau.

-   Nếu debugger tích hợp sẵn không bị tắt, nó sẽ bắt các exception không được xử lý trước khi
    debugger bên ngoài có thể.
-   Nếu reloader không bị tắt, nó có thể gây ra một reload không mong muốn nếu mã thay đổi
    trong một breakpoint.
-   Máy chủ phát triển vẫn sẽ bắt các exception không được xử lý nếu debugger tích hợp sẵn
    bị tắt, nếu không nó sẽ crash trên bất kỳ lỗi nào. Nếu bạn muốn điều đó (và
    thường thì bạn không muốn) hãy truyền ``passthrough_errors=True`` cho ``app.run``.

    .. code-block:: python

        app.run(
            debug=True, passthrough_errors=True,
            use_debugger=False, use_reloader=False
        )
