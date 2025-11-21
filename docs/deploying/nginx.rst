nginx
=====

`nginx`_ là một máy chủ HTTP cấp độ sản xuất, nhanh chóng. Khi phục vụ
ứng dụng của bạn với một trong các máy chủ WSGI được liệt kê trong :doc:`index`, thường
tốt hoặc cần thiết để đặt một máy chủ HTTP chuyên dụng phía trước nó.
"Reverse proxy" này có thể xử lý các request đến, TLS, và các
mối quan tâm về bảo mật và hiệu suất khác tốt hơn máy chủ WSGI.

Nginx có thể được cài đặt bằng trình quản lý gói hệ thống của bạn, hoặc một
tệp thực thi được xây dựng sẵn cho Windows. Việc cài đặt và chạy Nginx nằm ngoài
phạm vi của tài liệu này. Trang này phác thảo những điều cơ bản về cấu hình
Nginx để proxy ứng dụng của bạn. Hãy chắc chắn đọc tài liệu của nó để
hiểu những tính năng nào có sẵn.

.. _nginx: https://nginx.org/


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

Cấu hình nginx nằm tại ``/etc/nginx/nginx.conf`` trên
Linux. Nó có thể khác nhau tùy thuộc vào hệ điều hành của bạn. Kiểm tra
tài liệu và tìm kiếm ``nginx.conf``.

Xóa hoặc comment bất kỳ phần ``server`` hiện có nào. Thêm một phần ``server``
và sử dụng chỉ thị ``proxy_pass`` để trỏ đến địa chỉ mà
máy chủ WSGI đang lắng nghe. Chúng ta sẽ giả sử máy chủ WSGI đang lắng nghe
cục bộ tại ``http://127.0.0.1:8000``.

.. code-block:: nginx
    :caption: ``/etc/nginx.conf``

    server {
        listen 80;
        server_name _;

        location / {
            proxy_pass http://127.0.0.1:8000/;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-Prefix /;
        }
    }

Sau đó :doc:`proxy_fix` để ứng dụng của bạn sử dụng các header này.
