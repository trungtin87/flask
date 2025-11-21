Bố cục Dự án
============

Tạo một thư mục dự án và vào đó:

.. code-block:: none

    $ mkdir flask-tutorial
    $ cd flask-tutorial

Sau đó làm theo :doc:`hướng dẫn cài đặt </installation>` để thiết lập
một môi trường ảo Python và cài đặt Flask cho dự án của bạn.

Tutorial sẽ giả định bạn đang làm việc từ thư mục ``flask-tutorial``
từ bây giờ. Tên file ở đầu mỗi khối mã là
tương đối với thư mục này.

----

Một ứng dụng Flask có thể đơn giản như một file duy nhất.

.. code-block:: python
    :caption: ``hello.py``

    from flask import Flask

    app = Flask(__name__)


    @app.route('/')
    def hello():
        return 'Hello, World!'

Tuy nhiên, khi một dự án trở nên lớn hơn, việc giữ tất cả
mã trong một file trở nên quá tải. Các dự án Python sử dụng *package* để tổ chức mã
thành nhiều module có thể được import khi cần, và
tutorial cũng sẽ làm điều này.

Thư mục dự án sẽ chứa:

* ``flaskr/``, một package Python chứa mã ứng dụng và
  file của bạn.
* ``tests/``, một thư mục chứa các module kiểm thử.
* ``.venv/``, một môi trường ảo Python nơi Flask và các
  dependency khác được cài đặt.
* Các file cài đặt cho Python biết cách cài đặt dự án của bạn.
* Cấu hình version control, chẳng hạn như `git`_. Bạn nên tạo thói quen
  sử dụng một số loại version control cho tất cả các dự án của mình, bất kể
  kích thước.
* Bất kỳ file dự án nào khác bạn có thể thêm trong tương lai.

.. _git: https://git-scm.com/

Đến cuối, bố cục dự án của bạn sẽ trông như thế này:

.. code-block:: none

    /home/user/Projects/flask-tutorial
    ├── flaskr/
    │   ├── __init__.py
    │   ├── db.py
    │   ├── schema.sql
    │   ├── auth.py
    │   ├── blog.py
    │   ├── templates/
    │   │   ├── base.html
    │   │   ├── auth/
    │   │   │   ├── login.html
    │   │   │   └── register.html
    │   │   └── blog/
    │   │       ├── create.html
    │   │       ├── index.html
    │   │       └── update.html
    │   └── static/
    │       └── style.css
    ├── tests/
    │   ├── conftest.py
    │   ├── data.sql
    │   ├── test_factory.py
    │   ├── test_db.py
    │   ├── test_auth.py
    │   └── test_blog.py
    ├── .venv/
    ├── pyproject.toml
    └── MANIFEST.in

Nếu bạn đang sử dụng version control, các file sau được tạo ra
trong khi chạy dự án của bạn nên được bỏ qua. Có thể có các file khác
dựa trên trình soạn thảo bạn sử dụng. Nói chung, hãy bỏ qua các file mà bạn không
viết. Ví dụ, với git:

.. code-block:: none
    :caption: ``.gitignore``

    .venv/

    *.pyc
    __pycache__/

    instance/

    .pytest_cache/
    .coverage
    htmlcov/

    dist/
    build/
    *.egg-info/

Tiếp tục đến :doc:`factory`.
