Tác vụ nền với Celery
============================

Ví dụ này cho thấy cách cấu hình Celery với Flask, cách thiết lập một API để
gửi các tác vụ và thăm dò kết quả, và cách sử dụng API đó với JavaScript. Xem
[tài liệu của Flask về Celery](https://flask.palletsprojects.com/patterns/celery/).

Từ thư mục này, tạo một virtualenv và cài đặt ứng dụng vào đó. Sau đó chạy một
worker Celery.

```shell
python3 -m venv .venv
. ./.venv/bin/activate
pip install -r requirements.txt && pip install -e .
celery -A make_celery worker --loglevel INFO
```

Trong một terminal riêng biệt, kích hoạt virtualenv và chạy máy chủ phát triển Flask.

```shell
. ./.venv/bin/activate
flask -A task_app run --debug
```

Truy cập <http://localhost:5000/> và sử dụng các biểu mẫu để gửi các tác vụ. Bạn có thể thấy các yêu cầu thăm dò
trong công cụ dành cho nhà phát triển trình duyệt và nhật ký Flask. Bạn có thể thấy các tác vụ đang gửi
và hoàn thành trong nhật ký Celery.
