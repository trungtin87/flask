Flaskr
======

Ứng dụng blog cơ bản được xây dựng trong `hướng dẫn`_ Flask.

.. _hướng dẫn: https://flask.palletsprojects.com/tutorial/


Cài đặt
-------

**Hãy chắc chắn sử dụng cùng một phiên bản mã nguồn như phiên bản tài liệu
bạn đang đọc.** Bạn có thể muốn phiên bản được gắn thẻ mới nhất, nhưng
phiên bản Git mặc định là nhánh main. ::

    # clone kho lưu trữ
    $ git clone https://github.com/pallets/flask
    $ cd flask
    # checkout phiên bản chính xác
    $ git tag  # hiển thị các phiên bản đã gắn thẻ
    $ git checkout latest-tag-found-above
    $ cd examples/tutorial

Tạo một virtualenv và kích hoạt nó::

    $ python3 -m venv .venv
    $ . .venv/bin/activate

Hoặc trên Windows cmd::

    $ py -3 -m venv .venv
    $ .venv\Scripts\activate.bat

Cài đặt Flaskr::

    $ pip install -e .

Hoặc nếu bạn đang sử dụng nhánh main, hãy cài đặt Flask từ mã nguồn trước khi
cài đặt Flaskr::

    $ pip install -e ../..
    $ pip install -e .


Chạy
----

.. code-block:: text

    $ flask --app flaskr init-db
    $ flask --app flaskr run --debug

Mở http://127.0.0.1:5000 trong trình duyệt.


Kiểm thử
--------

::

    $ pip install '.[test]'
    $ pytest

Chạy với báo cáo độ bao phủ::

    $ coverage run -m pytest
    $ coverage report
    $ coverage html  # mở htmlcov/index.html trong trình duyệt
