Triển khai lên Sản xuất
=======================

Sau khi phát triển ứng dụng của bạn, bạn sẽ muốn làm cho nó có sẵn
công khai cho những người dùng khác. Khi bạn đang phát triển cục bộ, bạn có thể đang
sử dụng máy chủ phát triển tích hợp, trình gỡ lỗi, và trình tải lại. Những thứ này
không nên được sử dụng trong sản xuất. Thay vào đó, bạn nên sử dụng một
máy chủ WSGI chuyên dụng hoặc nền tảng lưu trữ, một số trong đó sẽ được mô tả ở đây.

"Sản xuất" có nghĩa là "không phải phát triển", điều này áp dụng cho dù bạn đang
phục vụ ứng dụng của mình công khai cho hàng triệu người dùng hay riêng tư /
cục bộ cho một người dùng duy nhất. **Không sử dụng máy chủ phát triển khi
triển khai lên sản xuất. Nó chỉ dành cho mục đích sử dụng trong quá trình phát triển
cục bộ. Nó không được thiết kế để đặc biệt an toàn, ổn định, hoặc
hiệu quả.**

Các Tùy chọn Tự Lưu trữ (Self-Hosted)
-------------------------------------

Flask là một *ứng dụng* WSGI. Một *máy chủ* WSGI được sử dụng để chạy
ứng dụng, chuyển đổi các request HTTP đến thành môi trường WSGI
tiêu chuẩn, và chuyển đổi các phản hồi WSGI thành các phản hồi HTTP.

Mục tiêu chính của các tài liệu này là làm quen cho bạn với các khái niệm
liên quan đến việc chạy một ứng dụng WSGI sử dụng một máy chủ WSGI sản xuất
và máy chủ HTTP. Có nhiều máy chủ WSGI và máy chủ HTTP, với nhiều
khả năng cấu hình. Các trang dưới đây thảo luận về các máy chủ phổ biến nhất,
và chỉ ra những điều cơ bản về việc chạy từng cái. Phần tiếp theo
thảo luận về các nền tảng có thể quản lý điều này cho bạn.

.. toctree::
    :maxdepth: 1

    gunicorn
    waitress
    mod_wsgi
    uwsgi
    gevent
    eventlet
    asgi

Các máy chủ WSGI có tích hợp sẵn các máy chủ HTTP. Tuy nhiên, một máy chủ HTTP
chuyên dụng có thể an toàn hơn, hiệu quả hơn, hoặc có khả năng hơn. Đặt một máy chủ
HTTP phía trước máy chủ WSGI được gọi là một "reverse proxy."

.. toctree::
    :maxdepth: 1

    proxy_fix
    nginx
    apache-httpd

Danh sách này không đầy đủ, và bạn nên đánh giá những cái này và các máy chủ
khác dựa trên nhu cầu của ứng dụng của bạn. Các máy chủ khác nhau sẽ có
các khả năng, cấu hình, và hỗ trợ khác nhau.


Các Nền tảng Lưu trữ
--------------------

Có nhiều dịch vụ có sẵn để lưu trữ các ứng dụng web mà không
cần phải duy trì máy chủ, mạng, tên miền, v.v. của riêng bạn. Một số
dịch vụ có thể có gói miễn phí lên đến một thời gian hoặc băng thông nhất định. Nhiều trong số
các dịch vụ này sử dụng một trong các máy chủ WSGI được mô tả ở trên, hoặc một giao diện
tương tự. Các liên kết dưới đây dành cho một số nền tảng phổ biến nhất,
có hướng dẫn cho Flask, WSGI, hoặc Python.

- `PythonAnywhere <https://help.pythonanywhere.com/pages/Flask/>`_
- `Google App Engine <https://cloud.google.com/appengine/docs/standard/python3/building-app>`_
- `Google Cloud Run <https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service>`_
- `AWS Elastic Beanstalk <https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html>`_
- `Microsoft Azure <https://docs.microsoft.com/en-us/azure/app-service/quickstart-python>`_

Danh sách này không đầy đủ, và bạn nên đánh giá những cái này và các dịch vụ
khác dựa trên nhu cầu của ứng dụng của bạn. Các dịch vụ khác nhau sẽ có
các khả năng, cấu hình, giá cả, và hỗ trợ khác nhau.

Bạn có thể sẽ cần :doc:`proxy_fix` khi sử dụng hầu hết các nền tảng
lưu trữ.
