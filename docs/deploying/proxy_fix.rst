Báo cho Flask biết nó đang ở Phía sau một Proxy
=============================================

Khi sử dụng một reverse proxy, hoặc nhiều nền tảng lưu trữ Python, proxy
sẽ chặn và chuyển tiếp tất cả các request bên ngoài đến máy chủ WSGI
cục bộ.

Từ quan điểm của máy chủ WSGI và ứng dụng Flask, các request
bây giờ đến từ máy chủ HTTP đến địa chỉ cục bộ, thay vì từ
địa chỉ từ xa đến địa chỉ máy chủ bên ngoài.

Các máy chủ HTTP nên đặt các header ``X-Forwarded-`` để truyền các giá trị
thực cho ứng dụng. Ứng dụng sau đó có thể được bảo để tin tưởng và
sử dụng các giá trị đó bằng cách bao bọc nó với middleware
:doc:`werkzeug:middleware/proxy_fix` được cung cấp bởi Werkzeug.

Middleware này chỉ nên được sử dụng nếu ứng dụng thực sự
ở phía sau một proxy, và nên được cấu hình với số lượng proxy
được chuỗi phía trước nó. Không phải tất cả các proxy đều đặt tất cả các header. Vì
các header đến có thể bị giả mạo, bạn phải đặt bao nhiêu proxy đang đặt
mỗi header để middleware biết cái gì nên tin tưởng.

.. code-block:: python

    from werkzeug.middleware.proxy_fix import ProxyFix

    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

Hãy nhớ, chỉ áp dụng middleware này nếu bạn đang ở phía sau một proxy, và đặt
đúng số lượng proxy đặt mỗi header. Nó có thể là một vấn đề bảo mật
nếu bạn cấu hình sai điều này.
