.. currentmodule:: flask

Test Coverage
=============

Viết các unit test cho ứng dụng của bạn cho phép bạn kiểm tra rằng mã
bạn đã viết hoạt động theo cách bạn mong đợi. Flask cung cấp một test client
mô phỏng các request đến ứng dụng và trả về dữ liệu phản hồi.

Bạn nên kiểm tra càng nhiều mã của mình càng tốt. Mã trong các hàm chỉ
chạy khi hàm được gọi, và mã trong các nhánh, chẳng hạn như các khối ``if``
, chỉ chạy khi điều kiện được đáp ứng. Bạn muốn đảm bảo rằng
mỗi hàm được kiểm tra với dữ liệu bao phủ mỗi nhánh.

Càng gần đến 100% coverage, bạn càng có thể thoải mái
rằng việc thực hiện một thay đổi sẽ không thay đổi hành vi khác một cách bất ngờ. Tuy nhiên,
100% coverage không đảm bảo rằng ứng dụng của bạn không có lỗi.
Đặc biệt, nó không kiểm tra cách người dùng tương tác với
ứng dụng trong trình duyệt. Mặc dù vậy, test coverage là một công cụ
quan trọng để sử dụng trong quá trình phát triển.

.. note::
    Điều này được giới thiệu muộn trong tutorial, nhưng trong các
    dự án tương lai của bạn, bạn nên kiểm tra khi bạn phát triển.

Bạn sẽ sử dụng `pytest`_ và `coverage`_ để kiểm tra và đo lường mã của bạn.
Cài đặt cả hai:

.. code-block:: none

    $ pip install pytest coverage

.. _pytest: https://pytest.readthedocs.io/
.. _coverage: https://coverage.readthedocs.io/


Thiết lập và Fixture
--------------------

Mã kiểm tra nằm trong thư mục ``tests``. Thư mục này nằm
*bên cạnh* package ``flaskr``, không phải bên trong nó.
File ``tests/conftest.py`` chứa các hàm thiết lập được gọi là *fixture*
mà mỗi bài kiểm tra sẽ sử dụng. Các bài kiểm tra nằm trong các module Python bắt đầu bằng
``test_``, và mỗi hàm kiểm tra trong các module đó cũng bắt đầu bằng
``test_``.

Mỗi bài kiểm tra sẽ tạo một file cơ sở dữ liệu tạm thời mới và điền một số
dữ liệu sẽ được sử dụng trong các bài kiểm tra. Viết một file SQL để chèn
dữ liệu đó.

.. code-block:: sql
    :caption: ``tests/data.sql``

    INSERT INTO user (username, password)
    VALUES
      ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
      ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

    INSERT INTO post (title, body, author_id, created)
    VALUES
      ('test title', 'test' || x'0a' || 'body', 1, '2018-01-01 00:00:00');

Fixture ``app`` sẽ gọi factory và truyền ``test_config`` để
cấu hình ứng dụng và cơ sở dữ liệu cho kiểm tra thay vì sử dụng
cấu hình phát triển cục bộ của bạn.

.. code-block:: python
    :caption: ``tests/conftest.py``

    import os
    import tempfile

    import pytest
    from flaskr import create_app
    from flaskr.db import get_db, init_db

    with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
        _data_sql = f.read().decode('utf8')


    @pytest.fixture
    def app():
        db_fd, db_path = tempfile.mkstemp()

        app = create_app({
            'TESTING': True,
            'DATABASE': db_path,
        })

        with app.app_context():
            init_db()
            get_db().executescript(_data_sql)

        yield app

        os.close(db_fd)
        os.unlink(db_path)


    @pytest.fixture
    def client(app):
        return app.test_client()


    @pytest.fixture
    def runner(app):
        return app.test_cli_runner()

:func:`tempfile.mkstemp` tạo và mở một file tạm thời, trả về
file descriptor và đường dẫn đến nó. Đường dẫn ``DATABASE`` được
ghi đè để nó trỏ đến đường dẫn tạm thời này thay vì thư mục
instance. Sau khi đặt đường dẫn, các bảng cơ sở dữ liệu được tạo và
dữ liệu kiểm tra được chèn vào. Sau khi bài kiểm tra kết thúc, file tạm thời được
đóng và xóa.

:data:`TESTING` cho Flask biết rằng ứng dụng đang ở chế độ kiểm tra. Flask thay đổi
một số hành vi nội bộ để dễ kiểm tra hơn, và các extension khác cũng có thể
sử dụng cờ này để làm cho việc kiểm tra chúng dễ dàng hơn.

Fixture ``client`` gọi
:meth:`app.test_client() <Flask.test_client>` với đối tượng ứng dụng
được tạo bởi fixture ``app``. Các bài kiểm tra sẽ sử dụng client để thực hiện
các request đến ứng dụng mà không cần chạy máy chủ.

Fixture ``runner`` tương tự như ``client``.
:meth:`app.test_cli_runner() <Flask.test_cli_runner>` tạo một runner
có thể gọi các lệnh Click được đăng ký với ứng dụng.

Pytest sử dụng các fixture bằng cách khớp tên hàm của chúng với tên
của các đối số trong các hàm kiểm tra. Ví dụ, hàm ``test_hello``
bạn sẽ viết tiếp theo nhận một đối số ``client``. Pytest khớp
điều đó với hàm fixture ``client``, gọi nó, và truyền
giá trị được trả về cho hàm kiểm tra.


Factory
-------

Không có nhiều điều để kiểm tra về chính factory. Hầu hết mã sẽ
được thực thi cho mỗi bài kiểm tra rồi, vì vậy nếu có gì đó thất bại, các bài kiểm tra khác
sẽ nhận thấy.

Hành vi duy nhất có thể thay đổi là truyền test config. Nếu config không
được truyền, nên có một số cấu hình mặc định, nếu không
cấu hình nên được ghi đè.

.. code-block:: python
    :caption: ``tests/test_factory.py``

    from flaskr import create_app


    def test_config():
        assert not create_app().testing
        assert create_app({'TESTING': True}).testing


    def test_hello(client):
        response = client.get('/hello')
        assert response.data == b'Hello, World!'

Bạn đã thêm route ``hello`` làm ví dụ khi viết factory ở
đầu tutorial. Nó trả về "Hello, World!", vì vậy bài kiểm tra
kiểm tra rằng dữ liệu phản hồi khớp.


Cơ sở dữ liệu
-------------

Trong một application context, ``get_db`` nên trả về cùng một
kết nối mỗi khi nó được gọi. Sau context, kết nối
nên được đóng.

.. code-block:: python
    :caption: ``tests/test_db.py``

    import sqlite3

    import pytest
    from flaskr.db import get_db


    def test_get_close_db(app):
        with app.app_context():
            db = get_db()
            assert db is get_db()

        with pytest.raises(sqlite3.ProgrammingError) as e:
            db.execute('SELECT 1')

        assert 'closed' in str(e.value)

Lệnh ``init-db`` nên gọi hàm ``init_db`` và xuất ra
một tin nhắn.

.. code-block:: python
    :caption: ``tests/test_db.py``

    def test_init_db_command(runner, monkeypatch):
        class Recorder(object):
            called = False

        def fake_init_db():
            Recorder.called = True

        monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
        result = runner.invoke(args=['init-db'])
        assert 'Initialized' in result.output
        assert Recorder.called

Bài kiểm tra này sử dụng fixture ``monkeypatch`` của Pytest để thay thế hàm
``init_db`` bằng một hàm ghi lại rằng nó đã được gọi.
Fixture ``runner`` bạn đã viết ở trên được sử dụng để gọi lệnh ``init-db``
theo tên.


Xác thực
--------

Đối với hầu hết các view, một người dùng cần phải đăng nhập. Cách dễ nhất để
làm điều này trong các bài kiểm tra là thực hiện một request ``POST`` đến view ``login``
với client. Thay vì viết điều đó ra mỗi lần, bạn có thể viết
một class với các phương thức để làm điều đó, và sử dụng một fixture để truyền nó client
cho mỗi bài kiểm tra.

.. code-block:: python
    :caption: ``tests/conftest.py``

    class AuthActions(object):
        def __init__(self, client):
            self._client = client

        def login(self, username='test', password='test'):
            return self._client.post(
                '/auth/login',
                data={'username': username, 'password': password}
            )

        def logout(self):
            return self._client.get('/auth/logout')


    @pytest.fixture
    def auth(client):
        return AuthActions(client)

Với fixture ``auth``, bạn có thể gọi ``auth.login()`` trong một bài kiểm tra để
đăng nhập với tư cách là người dùng ``test``, đã được chèn vào như một phần của
dữ liệu kiểm tra trong fixture ``app``.

View ``register`` nên render thành công trên ``GET``. Trên ``POST``
với dữ liệu form hợp lệ, nó nên chuyển hướng đến URL đăng nhập và dữ liệu của người dùng
nên có trong cơ sở dữ liệu. Dữ liệu không hợp lệ nên hiển thị các thông báo
lỗi.

.. code-block:: python
    :caption: ``tests/test_auth.py``

    import pytest
    from flask import g, session
    from flaskr.db import get_db


    def test_register(client, app):
        assert client.get('/auth/register').status_code == 200
        response = client.post(
            '/auth/register', data={'username': 'a', 'password': 'a'}
        )
        assert response.headers["Location"] == "/auth/login"

        with app.app_context():
            assert get_db().execute(
                "SELECT * FROM user WHERE username = 'a'",
            ).fetchone() is not None


    @pytest.mark.parametrize(('username', 'password', 'message'), (
        ('', '', b'Username is required.'),
        ('a', '', b'Password is required.'),
        ('test', 'test', b'already registered'),
    ))
    def test_register_validate_input(client, username, password, message):
        response = client.post(
            '/auth/register',
            data={'username': username, 'password': password}
        )
        assert message in response.data

:meth:`client.get() <werkzeug.test.Client.get>` thực hiện một request ``GET``
và trả về đối tượng :class:`Response` được trả về bởi Flask. Tương tự,
:meth:`client.post() <werkzeug.test.Client.post>` thực hiện một request ``POST``
, chuyển đổi dict ``data`` thành dữ liệu form.

Để kiểm tra rằng trang render thành công, một request đơn giản được thực hiện và
kiểm tra mã :attr:`~Response.status_code` ``200 OK``. Nếu
rendering thất bại, Flask sẽ trả về mã ``500 Internal Server Error``
.

:attr:`~Response.headers` sẽ có một header ``Location`` với URL đăng nhập
khi view register chuyển hướng đến view login.

:attr:`~Response.data` chứa nội dung phản hồi dưới dạng byte. Nếu
bạn mong đợi một giá trị nhất định được render trên trang, hãy kiểm tra rằng nó có trong
``data``. Byte phải được so sánh với byte. Nếu bạn muốn so sánh văn bản,
hãy sử dụng :meth:`get_data(as_text=True) <werkzeug.wrappers.Response.get_data>`
thay thế.

``pytest.mark.parametrize`` cho Pytest biết chạy cùng một hàm kiểm tra
với các đối số khác nhau. Bạn sử dụng nó ở đây để kiểm tra các đầu vào không hợp lệ
và thông báo lỗi khác nhau mà không cần viết cùng một mã ba lần.

Các bài kiểm tra cho view ``login`` rất giống với các bài kiểm tra cho
``register``. Thay vì kiểm tra dữ liệu trong cơ sở dữ liệu,
:data:`.session` nên có ``user_id`` được đặt sau khi đăng nhập.

.. code-block:: python
    :caption: ``tests/test_auth.py``

    def test_login(client, auth):
        assert client.get('/auth/login').status_code == 200
        response = auth.login()
        assert response.headers["Location"] == "/"

        with client:
            client.get('/')
            assert session['user_id'] == 1
            assert g.user['username'] == 'test'


    @pytest.mark.parametrize(('username', 'password', 'message'), (
        ('a', 'test', b'Incorrect username.'),
        ('test', 'a', b'Incorrect password.'),
    ))
    def test_login_validate_input(auth, username, password, message):
        response = auth.login(username, password)
        assert message in response.data

Sử dụng ``client`` trong một khối ``with`` cho phép truy cập các biến context
chẳng hạn như :data:`.session` sau khi phản hồi được trả về. Thông thường,
truy cập ``session`` bên ngoài một request sẽ đưa ra lỗi.

Kiểm tra ``logout`` là ngược lại của ``login``. :data:`.session` không nên
chứa ``user_id`` sau khi đăng xuất.

.. code-block:: python
    :caption: ``tests/test_auth.py``

    def test_logout(client, auth):
        auth.login()

        with client:
            auth.logout()
            assert 'user_id' not in session


Blog
----

Tất cả các view blog sử dụng fixture ``auth`` bạn đã viết trước đó. Gọi
``auth.login()`` và các request tiếp theo từ client sẽ được đăng nhập
với tư cách là người dùng ``test``.

View ``index`` nên hiển thị thông tin về bài viết đã được
thêm vào với dữ liệu kiểm tra. Khi đăng nhập với tư cách là tác giả, nên có
một liên kết để chỉnh sửa bài viết.

Bạn cũng có thể kiểm tra một số hành vi xác thực khác trong khi kiểm tra
view ``index``. Khi chưa đăng nhập, mỗi trang hiển thị các liên kết để đăng nhập hoặc
đăng ký. Khi đã đăng nhập, có một liên kết để đăng xuất.

.. code-block:: python
    :caption: ``tests/test_blog.py``

    import pytest
    from flaskr.db import get_db


    def test_index(client, auth):
        response = client.get('/')
        assert b"Log In" in response.data
        assert b"Register" in response.data

        auth.login()
        response = client.get('/')
        assert b'Log Out' in response.data
        assert b'test title' in response.data
        assert b'by test on 2018-01-01' in response.data
        assert b'test\nbody' in response.data
        assert b'href="/1/update"' in response.data

Một người dùng phải đăng nhập để truy cập các view ``create``, ``update``, và
``delete``. Người dùng đã đăng nhập phải là tác giả của bài viết để
truy cập ``update`` và ``delete``, nếu không trạng thái ``403 Forbidden``
được trả về. Nếu một ``post`` với ``id`` đã cho không tồn tại,
``update`` và ``delete`` nên trả về ``404 Not Found``.

.. code-block:: python
    :caption: ``tests/test_blog.py``

    @pytest.mark.parametrize('path', (
        '/create',
        '/1/update',
        '/1/delete',
    ))
    def test_login_required(client, path):
        response = client.post(path)
        assert response.headers["Location"] == "/auth/login"


    def test_author_required(app, client, auth):
        # thay đổi tác giả bài viết thành người dùng khác
        with app.app_context():
            db = get_db()
            db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
            db.commit()

        auth.login()
        # người dùng hiện tại không thể sửa đổi bài viết của người dùng khác
        assert client.post('/1/update').status_code == 403
        assert client.post('/1/delete').status_code == 403
        # người dùng hiện tại không thấy liên kết chỉnh sửa
        assert b'href="/1/update"' not in client.get('/').data


    @pytest.mark.parametrize('path', (
        '/2/update',
        '/2/delete',
    ))
    def test_exists_required(client, auth, path):
        auth.login()
        assert client.post(path).status_code == 404

Các view ``create`` và ``update`` nên render và trả về trạng thái
``200 OK`` cho một request ``GET``. Khi dữ liệu hợp lệ được gửi trong một
request ``POST``, ``create`` nên chèn dữ liệu bài viết mới vào
cơ sở dữ liệu, và ``update`` nên sửa đổi dữ liệu hiện có. Cả hai trang
nên hiển thị thông báo lỗi trên dữ liệu không hợp lệ.

.. code-block:: python
    :caption: ``tests/test_blog.py``

    def test_create(client, auth, app):
        auth.login()
        assert client.get('/create').status_code == 200
        client.post('/create', data={'title': 'created', 'body': ''})

        with app.app_context():
            db = get_db()
            count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
            assert count == 2


    def test_update(client, auth, app):
        auth.login()
        assert client.get('/1/update').status_code == 200
        client.post('/1/update', data={'title': 'updated', 'body': ''})

        with app.app_context():
            db = get_db()
            post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
            assert post['title'] == 'updated'


    @pytest.mark.parametrize('path', (
        '/create',
        '/1/update',
    ))
    def test_create_update_validate(client, auth, path):
        auth.login()
        response = client.post(path, data={'title': '', 'body': ''})
        assert b'Title is required.' in response.data

View ``delete`` nên chuyển hướng đến URL index và bài viết không nên
còn tồn tại trong cơ sở dữ liệu nữa.

.. code-block:: python
    :caption: ``tests/test_blog.py``

    def test_delete(client, auth, app):
        auth.login()
        response = client.post('/1/delete')
        assert response.headers["Location"] == "/"

        with app.app_context():
            db = get_db()
            post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
            assert post is None


Chạy Các Bài kiểm tra
---------------------

Một số cấu hình bổ sung, không bắt buộc nhưng làm cho việc chạy các bài kiểm tra với coverage
ít dài dòng hơn, có thể được thêm vào file ``pyproject.toml`` của dự án.

.. code-block:: toml
    :caption: ``pyproject.toml``

    [tool.pytest.ini_options]
    testpaths = ["tests"]

    [tool.coverage.run]
    branch = true
    source = ["flaskr"]

Để chạy các bài kiểm tra, sử dụng lệnh ``pytest``. Nó sẽ tìm và chạy tất cả
các hàm kiểm tra bạn đã viết.

.. code-block:: none

    $ pytest

    ========================= test session starts ==========================
    platform linux -- Python 3.6.4, pytest-3.5.0, py-1.5.3, pluggy-0.6.0
    rootdir: /home/user/Projects/flask-tutorial
    collected 23 items

    tests/test_auth.py ........                                      [ 34%]
    tests/test_blog.py ............                                  [ 86%]
    tests/test_db.py ..                                              [ 95%]
    tests/test_factory.py ..                                         [100%]

    ====================== 24 passed in 0.64 seconds =======================

Nếu bất kỳ bài kiểm tra nào thất bại, pytest sẽ hiển thị lỗi đã được đưa ra. Bạn có thể
chạy ``pytest -v`` để có danh sách từng hàm kiểm tra thay vì các dấu chấm.

Để đo lường code coverage của các bài kiểm tra của bạn, sử dụng lệnh ``coverage``
để chạy pytest thay vì chạy nó trực tiếp.

.. code-block:: none

    $ coverage run -m pytest

Bạn có thể xem một báo cáo coverage đơn giản trong terminal:

.. code-block:: none

    $ coverage report

    Name                 Stmts   Miss Branch BrPart  Cover
    ------------------------------------------------------
    flaskr/__init__.py      21      0      2      0   100%
    flaskr/auth.py          54      0     22      0   100%
    flaskr/blog.py          54      0     16      0   100%
    flaskr/db.py            24      0      4      0   100%
    ------------------------------------------------------
    TOTAL                  153      0     44      0   100%

Một báo cáo HTML cho phép bạn xem các dòng nào đã được bao phủ trong mỗi file:

.. code-block:: none

    $ coverage html

Điều này tạo ra các file trong thư mục ``htmlcov``. Mở
``htmlcov/index.html`` trong trình duyệt của bạn để xem báo cáo.

Tiếp tục đến :doc:`deploy`.
