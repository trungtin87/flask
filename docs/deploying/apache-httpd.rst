Apache httpd
============

`Apache httpd`_ là một máy chủ HTTP cấp độ sản xuất, nhanh chóng. Khi phục vụ
ứng dụng của bạn với một trong các máy chủ WSGI được liệt kê trong :doc:`index`, thường
tốt hoặc cần thiết để đặt một máy chủ HTTP chuyên dụng phía trước
nó. "Reverse proxy" này có thể xử lý các request đến, TLS, và các
mối quan tâm về bảo mật và hiệu suất khác tốt hơn máy chủ WSGI.

httpd có thể được cài đặt bằng trình quản lý gói hệ thống của bạn, hoặc một
tệp thực thi được xây dựng sẵn cho Windows. Việc cài đặt và chạy httpd nằm ngoài
phạm vi của tài liệu này. Trang này phác thảo những điều cơ bản về cấu hình
httpd để proxy ứng dụng của bạn. Hãy chắc chắn đọc tài liệu của nó để
hiểu những tính năng nào có sẵn.

.. _Apache httpd: https://httpd.apache.org/


Tên Miền
--------

Việc mua và cấu hình tên miền nằm ngoài phạm vi của tài liệu
này. Nói chung, bạn sẽ mua một tên miền từ một nhà đăng ký, trả tiền cho
không gian máy chủ với một nhà cung cấp dịch vụ lưu trữ, và sau đó trỏ nhà đăng ký của bạn
đến các máy chủ tên của nhà cung cấp dịch vụ lưu trữ.

Để mô phỏng điều này, bạn cũng có thể chỉnh sửa file ``hosts`` của mình, nằm tại
``/etc/hosts`` trên Linux. Thêm một dòng liên kết một tên với
IP cục bộ.

Các hệ thống Linux hiện đại có thể được cấu hình để coi bất kỳ tên miền nào
kết thúc bằng ``.localhost`` như thế này mà không cần thêm nó vào file ``hosts``.

.. code-block:: python
    :caption: ``/etc/hosts``

    127.0.0.1 hello.localhost


Cấu hình
--------

Cấu hình httpd nằm tại ``/etc/httpd/conf/httpd.conf`` trên
Linux. Nó có thể khác nhau tùy thuộc vào hệ điều hành của bạn. Kiểm tra
tài liệu và tìm kiếm ``httpd.conf``.

Xóa hoặc comment bất kỳ chỉ thị ``DocumentRoot`` hiện có nào. Thêm các
dòng cấu hình bên dưới. Chúng ta sẽ giả sử máy chủ WSGI đang lắng nghe cục bộ tại
``http://127.0.0.1:8000``.

.. code-block:: apache
    :caption: ``/etc/httpd/conf/httpd.conf``

    LoadModule proxy_module modules/mod_proxy.so
    LoadModule proxy_http_module modules/mod_proxy_http.so
    ProxyPass / http://127.0.0.1:8000/
    RequestHeader set X-Forwarded-Proto http
    RequestHeader set X-Forwarded-Prefix /

Các dòng ``LoadModule`` có thể đã tồn tại. Nếu vậy, hãy chắc chắn rằng chúng được
uncomment thay vì thêm chúng thủ công.

Sau đó :doc:`proxy_fix` để ứng dụng của bạn sử dụng các header
``X-Forwarded``. ``X-Forwarded-For`` và ``X-Forwarded-Host`` được tự động
thiết lập bởi ``ProxyPass``.
