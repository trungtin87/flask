Kiểm thử Ứng dụng Flask
=======================

Flask cung cấp các tiện ích để kiểm thử một ứng dụng. Tài liệu này
đi qua các kỹ thuật để làm việc với các phần khác nhau của ứng dụng
trong các bài kiểm thử.

Chúng ta sẽ sử dụng framework `pytest`_ để thiết lập và chạy các bài kiểm thử của mình.

.. code-block:: text

    $ pip install pytest

.. _pytest: https://docs.pytest.org/

:doc:`Tutorial </tutorial/index>` đi qua cách viết các bài kiểm thử cho
100% coverage của ứng dụng blog Flaskr mẫu. Xem
:doc:`tutorial về các bài kiểm thử </tutorial/tests>` để biết
giải thích chi tiết về các bài kiểm thử cụ thể cho một ứng dụng.


Xác định Bài kiểm thử
---------------------

Các bài kiểm thử thường nằm trong thư mục ``tests``. Các bài kiểm thử là các hàm
bắt đầu bằng ``test_``, trong các module Python bắt đầu bằng ``test_``.
Các bài kiểm thử cũng có thể được nhóm thêm trong các class bắt đầu bằng ``Test``.

Có thể khó biết nên kiểm thử cái gì. Nói chung, hãy cố gắng kiểm thử
mã mà bạn viết, không phải mã của các thư viện mà bạn sử dụng, vì chúng
đã được kiểm thử rồi. Hãy cố gắng trích xuất các hành vi phức tạp thành các
hàm riêng biệt để kiểm thử riêng lẻ.


Fixture
-------

Pytest *fixture* cho phép viết các đoạn mã có thể tái sử dụng qua
các bài kiểm thử. Một fixture đơn giản trả về một giá trị, nhưng một fixture cũng có thể
thiết lập, yield một giá trị, sau đó dọn dẹp. Các fixture cho ứng dụng,
test client, và CLI runner được hiển thị bên dưới, chúng có thể được đặt trong
``tests/conftest.py``.

Nếu bạn đang sử dụng một
:doc:`application factory </patterns/appfactories>`, hãy định nghĩa một fixture ``app``
để tạo và cấu hình một instance ứng dụng. Bạn có thể thêm mã trước
và sau ``yield`` để thiết lập và dọn dẹp các tài nguyên khác, chẳng hạn như
tạo và xóa một cơ sở dữ liệu.

Nếu bạn không sử dụng factory, bạn đã có một đối tượng app mà bạn có thể
import và cấu hình trực tiếp. Bạn vẫn có thể sử dụng một fixture ``app`` để
thiết lập và dọn dẹp tài nguyên.

.. code-block:: python

    import pytest
    from my_project import create_app

    @pytest.fixture()
    def app():
        app = create_app()
        app.config.update({
            "TESTING": True,
        })

        # other setup can go here

        yield app

        # clean up / reset resources here


    @pytest.fixture()
    def client(app):
        return app.test_client()


    @pytest.fixture()
    def runner(app):
        return app.test_cli_runner()


Gửi Request với Test Client
----------------------------

Test client thực hiện các request đến ứng dụng mà không cần chạy một máy chủ
live. Client của Flask mở rộng
:doc:`client của Werkzeug <werkzeug:test>`, xem các tài liệu đó để biết thêm
thông tin.

``client`` có các phương thức khớp với các phương thức HTTP request phổ biến,
chẳng hạn như ``client.get()`` và ``client.post()``. Chúng nhận nhiều đối số
để xây dựng request; bạn có thể tìm tài liệu đầy đủ trong
:class:`~werkzeug.test.EnvironBuilder`. Thông thường bạn sẽ sử dụng ``path``,
``query_string``, ``headers``, và ``data`` hoặc ``json``.

Để thực hiện một request, hãy gọi phương thức mà request nên sử dụng với đường dẫn
đến route để kiểm thử. Một :class:`~werkzeug.test.TestResponse` được trả về
để kiểm tra dữ liệu phản hồi. Nó có tất cả các thuộc tính thông thường của một
đối tượng phản hồi. Bạn thường sẽ xem ``response.data``, là
byte được trả về bởi view. Nếu bạn muốn sử dụng văn bản, Werkzeug 2.1
cung cấp ``response.text``, hoặc sử dụng ``response.get_data(as_text=True)``.

.. code-block:: python

    def test_request_example(client):
        response = client.get("/posts")
        assert b"<h2>Hello, World!</h2>" in response.data


Truyền một dict ``query_string={"key": "value", ...}`` để đặt các đối số trong
query string (sau ``?`` trong URL). Truyền một dict
``headers={}`` để đặt các request header.

Để gửi một request body trong một POST hoặc PUT request, hãy truyền một giá trị cho
``data``. Nếu raw byte được truyền, body chính xác đó được sử dụng. Thông thường,
bạn sẽ truyền một dict để đặt dữ liệu form.


Dữ liệu Form
~~~~~~~~~~~~

Để gửi dữ liệu form, hãy truyền một dict cho ``data``. Header ``Content-Type``
sẽ được đặt thành ``multipart/form-data`` hoặc
``application/x-www-form-urlencoded`` tự động.

Nếu một giá trị là một file object được mở để đọc byte (chế độ ``"rb"``), nó
sẽ được coi là một file được tải lên. Để thay đổi tên file và
loại nội dung được phát hiện, hãy truyền một tuple ``(file, filename, content_type)``. Các file
object sẽ được đóng sau khi thực hiện request, vì vậy chúng không cần
sử dụng mẫu ``with open() as f:`` thông thường.

Có thể hữu ích khi lưu trữ các file trong thư mục ``tests/resources``, sau đó
sử dụng ``pathlib.Path`` để lấy các file tương đối với file kiểm thử hiện tại.

.. code-block:: python

    from pathlib import Path

    # get the resources folder in the tests folder
    resources = Path(__file__).parent / "resources"

    def test_edit_user(client):
        response = client.post("/user/2/edit", data={
            "name": "Flask",
            "theme": "dark",
            "picture": (resources / "picture.png").open("rb"),
        })
        assert response.status_code == 200


Dữ liệu JSON
~~~~~~~~~~~~

Để gửi dữ liệu JSON, hãy truyền một đối tượng cho ``json``. Header ``Content-Type``
sẽ được đặt thành ``application/json`` tự động.

Tương tự, nếu phản hồi chứa dữ liệu JSON, thuộc tính ``response.json``
sẽ chứa đối tượng đã được deserialize.

.. code-block:: python

    def test_json_data(client):
        response = client.post("/graphql", json={
            "query": """
                query User($id: String!) {
                    user(id: $id) {
                        name
                        theme
                        picture_url
                    }
                }
            """,
            variables={"id": 2},
        })
        assert response.json["data"]["user"]["name"] == "Flask"


Theo dõi Redirect
-----------------

Theo mặc định, client không thực hiện các request bổ sung nếu phản hồi
là một redirect. Bằng cách truyền ``follow_redirects=True`` cho một phương thức request,
client sẽ tiếp tục thực hiện các request cho đến khi một phản hồi không redirect
được trả về.

:attr:`TestResponse.history <werkzeug.test.TestResponse.history>` là
một tuple của các phản hồi dẫn đến phản hồi cuối cùng. Mỗi
phản hồi có một thuộc tính :attr:`~werkzeug.test.TestResponse.request`
ghi lại request đã tạo ra phản hồi đó.

.. code-block:: python

    def test_logout_redirect(client):
        response = client.get("/logout", follow_redirects=True)
        # Check that there was one redirect response.
        assert len(response.history) == 1
        # Check that the second request was to the index page.
        assert response.request.path == "/index"


Truy cập và Sửa đổi Session
----------------------------

Để truy cập các biến context của Flask, chủ yếu là
:data:`~flask.session`, hãy sử dụng client trong một câu lệnh ``with``.
App và request context sẽ vẫn hoạt động *sau khi* thực hiện một request,
cho đến khi khối ``with`` kết thúc.

.. code-block:: python

    from flask import session

    def test_access_session(client):
        with client:
            client.post("/auth/login", data={"username": "flask"})
            # session is still accessible
            assert session["user_id"] == 1

        # session is no longer accessible

Nếu bạn muốn truy cập hoặc đặt một giá trị trong session *trước khi* thực hiện một
request, hãy sử dụng phương thức
:meth:`~flask.testing.FlaskClient.session_transaction` của client trong một
câu lệnh ``with``. Nó trả về một đối tượng session, và sẽ lưu
session khi khối kết thúc.

.. code-block:: python

    from flask import session

    def test_modify_session(client):
        with client.session_transaction() as session:
            # set a user id without going through the login route
            session["user_id"] = 1

        # session is saved now

        response = client.get("/users/me")
        assert response.json["username"] == "flask"


.. _testing-cli:

Chạy Lệnh với CLI Runner
-------------------------

Flask cung cấp :meth:`~flask.Flask.test_cli_runner` để tạo một
:class:`~flask.testing.FlaskCliRunner`, chạy các lệnh CLI trong
isolation và bắt đầu ra trong một đối tượng :class:`~click.testing.Result`
. Runner của Flask mở rộng :doc:`runner của Click <click:testing>`,
xem các tài liệu đó để biết thêm thông tin.

Sử dụng phương thức :meth:`~flask.testing.FlaskCliRunner.invoke` của runner để
gọi các lệnh theo cách giống như chúng sẽ được gọi với lệnh ``flask``
từ dòng lệnh.

.. code-block:: python

    import click

    @app.cli.command("hello")
    @click.option("--name", default="World")
    def hello_command(name):
        click.echo(f"Hello, {name}!")

    def test_hello_command(runner):
        result = runner.invoke(args="hello")
        assert "World" in result.output

        result = runner.invoke(args=["hello", "--name", "Flask"])
        assert "Flask" in result.output


Bài kiểm thử phụ thuộc vào Context Hoạt động
---------------------------------------------

Bạn có thể có các hàm được gọi từ các view hoặc lệnh, mong đợi một
:doc:`app context </appcontext>` hoạt động vì chúng truy cập :data:`.request`,
:data:`.session`, :data:`.g`, hoặc :data:`.current_app`. Thay vì kiểm thử chúng bằng cách
thực hiện một request hoặc gọi lệnh, bạn có thể tạo và kích hoạt một context
trực tiếp.

Sử dụng ``with app.app_context()`` để push một application context. Ví dụ
, các extension cơ sở dữ liệu thường yêu cầu một app context hoạt động để
thực hiện các truy vấn.

.. code-block:: python

    def test_db_post_model(app):
        with app.app_context():
            post = db.session.query(Post).get(1)

Sử dụng ``with app.test_request_context()`` để push một request context. Nó
nhận các đối số giống như các phương thức request của test client.

.. code-block:: python

    def test_validate_user_edit(app):
        with app.test_request_context(
            "/user/2/edit", method="POST", data={"name": ""}
        ):
            # call a function that accesses `request`
            messages = validate_edit_user()

        assert messages["name"][0] == "Name cannot be empty."

Tạo một test request context không chạy bất kỳ mã dispatching nào của Flask
, vì vậy các hàm ``before_request`` không được gọi. Nếu bạn cần
gọi chúng, thường tốt hơn là thực hiện một request đầy đủ thay thế. Tuy nhiên,
có thể gọi chúng thủ công.

.. code-block:: python

    def test_auth_token(app):
        with app.test_request_context("/user/2/edit", headers={"X-Auth-Token": "1"}):
            app.preprocess_request()
            assert g.user.name == "Flask"
