.. currentmodule:: flask

Định nghĩa và Truy cập Cơ sở dữ liệu
====================================

Ứng dụng sẽ sử dụng cơ sở dữ liệu `SQLite`_ để lưu trữ người dùng và bài viết.
Python đi kèm với hỗ trợ tích hợp sẵn cho SQLite trong module :mod:`sqlite3`
.

SQLite rất tiện lợi vì nó không yêu cầu thiết lập một máy chủ
cơ sở dữ liệu riêng biệt và được tích hợp sẵn vào Python. Tuy nhiên, nếu các
request đồng thời cố gắng ghi vào cơ sở dữ liệu cùng một lúc, chúng sẽ chậm
lại vì mỗi lần ghi xảy ra tuần tự. Các ứng dụng nhỏ sẽ không nhận thấy
điều này. Khi bạn trở nên lớn, bạn có thể muốn chuyển sang một cơ sở dữ liệu
khác.

Tutorial không đi vào chi tiết về SQL. Nếu bạn không quen thuộc
với nó, tài liệu SQLite mô tả `ngôn ngữ`_.

.. _SQLite: https://sqlite.org/about.html
.. _language: https://sqlite.org/lang.html


Kết nối với Cơ sở dữ liệu
--------------------------

Điều đầu tiên cần làm khi làm việc với cơ sở dữ liệu SQLite (và hầu hết
các thư viện cơ sở dữ liệu Python khác) là tạo một kết nối đến nó. Bất kỳ
truy vấn và thao tác nào đều được thực hiện bằng cách sử dụng kết nối, được
đóng sau khi công việc hoàn thành.

Trong các ứng dụng web, kết nối này thường được gắn với request. Nó
được tạo tại một thời điểm nào đó khi xử lý một request, và đóng trước khi
phản hồi được gửi.

.. code-block:: python
    :caption: ``flaskr/db.py``

    import sqlite3
    from datetime import datetime

    import click
    from flask import current_app, g


    def get_db():
        if 'db' not in g:
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row

        return g.db


    def close_db(e=None):
        db = g.pop('db', None)

        if db is not None:
            db.close()

:data:`.g` là một đối tượng đặc biệt duy nhất cho mỗi request. Nó được
sử dụng để lưu trữ dữ liệu có thể được truy cập bởi nhiều hàm trong
request. Kết nối được lưu trữ và sử dụng lại thay vì tạo một
kết nối mới nếu ``get_db`` được gọi lần thứ hai trong cùng một
request.

:data:`.current_app` là một đối tượng đặc biệt khác trỏ đến ứng dụng Flask
đang xử lý request. Vì bạn đã sử dụng một application factory,
không có đối tượng ứng dụng khi viết phần còn lại của mã.
``get_db`` sẽ được gọi khi ứng dụng đã được tạo và đang
xử lý một request, vì vậy :data:`.current_app` có thể được sử dụng.

:func:`sqlite3.connect` thiết lập một kết nối đến file được trỏ đến
bởi khóa cấu hình ``DATABASE``. File này không cần tồn tại
ngay bây giờ, và sẽ không tồn tại cho đến khi bạn khởi tạo cơ sở dữ liệu sau.

:class:`sqlite3.Row` cho kết nối biết trả về các hàng hoạt động
như dict. Điều này cho phép truy cập các cột theo tên.

``close_db`` kiểm tra xem một kết nối đã được tạo bằng cách kiểm tra xem ``g.db``
đã được đặt chưa. Nếu kết nối tồn tại, nó sẽ bị đóng. Xa hơn nữa bạn sẽ
cho ứng dụng của mình biết về hàm ``close_db`` trong application
factory để nó được gọi sau mỗi request.


Tạo Bảng
--------

Trong SQLite, dữ liệu được lưu trữ trong *bảng* và *cột*. Chúng cần được
tạo trước khi bạn có thể lưu trữ và truy xuất dữ liệu. Flaskr sẽ lưu trữ người dùng
trong bảng ``user``, và bài viết trong bảng ``post``. Tạo một file
với các lệnh SQL cần thiết để tạo các bảng trống:

.. code-block:: sql
    :caption: ``flaskr/schema.sql``

    DROP TABLE IF EXISTS user;
    DROP TABLE IF EXISTS post;

    CREATE TABLE user (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL
    );

    CREATE TABLE post (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      author_id INTEGER NOT NULL,
      created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      title TEXT NOT NULL,
      body TEXT NOT NULL,
      FOREIGN KEY (author_id) REFERENCES user (id)
    );

Thêm các hàm Python sẽ chạy các lệnh SQL này vào file
``db.py``:

.. code-block:: python
    :caption: ``flaskr/db.py``

    def init_db():
        db = get_db()

        with current_app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))


    @click.command('init-db')
    def init_db_command():
        """Clear the existing data and create new tables."""
        init_db()
        click.echo('Initialized the database.')


    sqlite3.register_converter(
        "timestamp", lambda v: datetime.fromisoformat(v.decode())
    )

:meth:`open_resource() <Flask.open_resource>` mở một file tương đối với
package ``flaskr``, điều này hữu ích vì bạn sẽ không nhất thiết biết
vị trí đó ở đâu khi triển khai ứng dụng sau này. ``get_db``
trả về một kết nối cơ sở dữ liệu, được sử dụng để thực thi các lệnh
đọc từ file.

:func:`click.command` định nghĩa một lệnh dòng lệnh có tên ``init-db``
gọi hàm ``init_db`` và hiển thị thông báo thành công cho
người dùng. Bạn có thể đọc :doc:`/cli` để tìm hiểu thêm về viết lệnh.

Cuộc gọi đến :func:`sqlite3.register_converter` cho Python biết cách
diễn giải các giá trị timestamp trong cơ sở dữ liệu. Chúng ta chuyển đổi giá trị thành một
:class:`datetime.datetime`.


Đăng ký với Ứng dụng
--------------------

Các hàm ``close_db`` và ``init_db_command`` cần được đăng ký
với instance ứng dụng; nếu không, chúng sẽ không được ứng dụng sử dụng
. Tuy nhiên, vì bạn đang sử dụng một factory function, instance
đó không có sẵn khi viết các hàm. Thay vào đó, hãy viết một
hàm nhận một ứng dụng và thực hiện đăng ký.

.. code-block:: python
    :caption: ``flaskr/db.py``

    def init_app(app):
        app.teardown_appcontext(close_db)
        app.cli.add_command(init_db_command)

:meth:`app.teardown_appcontext() <Flask.teardown_appcontext>` cho
Flask biết gọi hàm đó khi dọn dẹp sau khi trả về
phản hồi.

:meth:`app.cli.add_command() <click.Group.add_command>` thêm một
lệnh mới có thể được gọi bằng lệnh ``flask``.

Import và gọi hàm này từ factory. Đặt mã mới ở
cuối hàm factory trước khi trả về ứng dụng.

.. code-block:: python
    :caption: ``flaskr/__init__.py``

    def create_app():
        app = ...
        # existing code omitted

        from . import db
        db.init_app(app)

        return app


Khởi tạo File Cơ sở dữ liệu
---------------------------

Bây giờ ``init-db`` đã được đăng ký với ứng dụng, nó có thể được gọi
bằng lệnh ``flask``, tương tự như lệnh ``run`` từ
trang trước.

.. note::

    Nếu bạn vẫn đang chạy máy chủ từ trang trước, bạn có thể
    dừng máy chủ, hoặc chạy lệnh này trong một terminal mới. Nếu
    bạn sử dụng một terminal mới, hãy nhớ chuyển đến thư mục dự án của bạn
    và kích hoạt env như được mô tả trong :doc:`/installation`.

Chạy lệnh ``init-db``:

.. code-block:: none

    $ flask --app flaskr init-db
    Initialized the database.

Bây giờ sẽ có một file ``flaskr.sqlite`` trong thư mục ``instance`` trong
dự án của bạn.

Tiếp tục đến :doc:`views`.
