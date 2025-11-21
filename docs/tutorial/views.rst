.. currentmodule:: flask

Blueprint và View
==================

Một view function là mã bạn viết để phản hồi các request đến
ứng dụng của bạn. Flask sử dụng các mẫu để khớp URL request đến với
view nên xử lý nó. View trả về dữ liệu mà Flask chuyển
thành một phản hồi đi ra. Flask cũng có thể đi theo hướng khác và
tạo một URL đến một view dựa trên tên và đối số của nó.


Tạo một Blueprint
-----------------

Một :class:`Blueprint` là một cách để tổ chức một nhóm các view liên quan và
mã khác. Thay vì đăng ký các view và mã khác trực tiếp với
một ứng dụng, chúng được đăng ký với một blueprint. Sau đó blueprint
được đăng ký với ứng dụng khi nó có sẵn trong hàm
factory.

Flaskr sẽ có hai blueprint, một cho các hàm xác thực và
một cho các hàm bài viết blog. Mã cho mỗi blueprint sẽ đi
vào một module riêng biệt. Vì blog cần biết về xác thực,
bạn sẽ viết blueprint xác thực trước.

.. code-block:: python
    :caption: ``flaskr/auth.py``

    import functools

    from flask import (
        Blueprint, flash, g, redirect, render_template, request, session, url_for
    )
    from werkzeug.security import check_password_hash, generate_password_hash

    from flaskr.db import get_db

    bp = Blueprint('auth', __name__, url_prefix='/auth')

Điều này tạo ra một :class:`Blueprint` có tên ``'auth'``. Giống như đối tượng ứng dụng
, blueprint cần biết nơi nó được định nghĩa, vì vậy ``__name__``
được truyền làm đối số thứ hai. ``url_prefix`` sẽ được thêm vào đầu
tất cả các URL liên quan đến blueprint.

Import và đăng ký blueprint từ factory bằng cách sử dụng
:meth:`app.register_blueprint() <Flask.register_blueprint>`. Đặt
mã mới ở cuối hàm factory trước khi trả về ứng dụng.

.. code-block:: python
    :caption: ``flaskr/__init__.py``

    def create_app():
        app = ...
        # existing code omitted

        from . import auth
        app.register_blueprint(auth.bp)

        return app

Blueprint xác thực sẽ có các view để đăng ký người dùng mới và
để đăng nhập và đăng xuất.


View Đầu tiên: Đăng ký
----------------------

Khi người dùng truy cập URL ``/auth/register``, view ``register``
sẽ trả về `HTML`_ với một form để họ điền vào. Khi họ gửi
form, nó sẽ xác thực đầu vào của họ và hiển thị form lại
với một thông báo lỗi hoặc tạo người dùng mới và đến trang đăng nhập.

.. _HTML: https://developer.mozilla.org/docs/Web/HTML

Hiện tại bạn sẽ chỉ viết mã view. Ở trang tiếp theo, bạn sẽ
viết các template để tạo form HTML.

.. code-block:: python
    :caption: ``flaskr/auth.py``

    @bp.route('/register', methods=('GET', 'POST'))
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            db = get_db()
            error = None

            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'

            if error is None:
                try:
                    db.execute(
                        "INSERT INTO user (username, password) VALUES (?, ?)",
                        (username, generate_password_hash(password)),
                    )
                    db.commit()
                except db.IntegrityError:
                    error = f"User {username} is already registered."
                else:
                    return redirect(url_for("auth.login"))

            flash(error)

        return render_template('auth/register.html')

Đây là những gì view function ``register`` đang làm:

#.  :meth:`@bp.route <Blueprint.route>` liên kết URL ``/register``
    với view function ``register``. Khi Flask nhận được một request
    đến ``/auth/register``, nó sẽ gọi view ``register`` và sử dụng
    giá trị trả về làm phản hồi.

#.  Nếu người dùng gửi form,
    :attr:`request.method <Request.method>` sẽ là ``'POST'``. Trong trường hợp
    này, bắt đầu xác thực đầu vào.

#.  :attr:`request.form <Request.form>` là một loại đặc biệt của
    :class:`dict` ánh xạ các khóa và giá trị form đã gửi. Người dùng sẽ
    nhập ``username`` và ``password`` của họ.

#.  Xác thực rằng ``username`` và ``password`` không trống.

#.  Nếu xác thực thành công, chèn dữ liệu người dùng mới vào cơ sở dữ liệu.

    -   :meth:`db.execute <sqlite3.Connection.execute>` nhận một truy vấn SQL
        với các placeholder ``?`` cho bất kỳ đầu vào người dùng nào, và một tuple các
        giá trị để thay thế các placeholder. Thư viện cơ sở dữ liệu
        sẽ chăm sóc việc thoát các giá trị để bạn không dễ bị tấn công
        *SQL injection*.

    -   Vì lý do bảo mật, mật khẩu không bao giờ nên được lưu trữ trong cơ sở dữ liệu
        trực tiếp. Thay vào đó,
        :func:`~werkzeug.security.generate_password_hash` được sử dụng để
        hash mật khẩu một cách an toàn, và hash đó được lưu trữ. Vì truy vấn
        này sửa đổi dữ liệu,
        :meth:`db.commit() <sqlite3.Connection.commit>` cần được
        gọi sau đó để lưu các thay đổi.

    -   Một :exc:`sqlite3.IntegrityError` sẽ xảy ra nếu tên người dùng
        đã tồn tại, điều này nên được hiển thị cho người dùng dưới dạng một
        lỗi xác thực khác.

#.  Sau khi lưu trữ người dùng, họ được chuyển hướng đến trang đăng nhập.
    :func:`url_for` tạo URL cho view đăng nhập dựa trên
    tên của nó. Điều này tốt hơn so với viết URL trực tiếp vì nó cho phép
    bạn thay đổi URL sau mà không cần thay đổi tất cả mã liên kết đến
    nó. :func:`redirect` tạo một phản hồi chuyển hướng đến URL được tạo
    .

#.  Nếu xác thực thất bại, lỗi được hiển thị cho người dùng. :func:`flash`
    lưu trữ các tin nhắn có thể được truy xuất khi render template.

#.  Khi người dùng ban đầu điều hướng đến ``auth/register``, hoặc
    có lỗi xác thực, một trang HTML với form đăng ký
    nên được hiển thị. :func:`render_template` sẽ render một template
    chứa HTML, mà bạn sẽ viết trong bước tiếp theo của
    tutorial.


Đăng nhập
---------

View này tuân theo cùng một mẫu như view ``register`` ở trên.

.. code-block:: python
    :caption: ``flaskr/auth.py``

    @bp.route('/login', methods=('GET', 'POST'))
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            db = get_db()
            error = None
            user = db.execute(
                'SELECT * FROM user WHERE username = ?', (username,)
            ).fetchone()

            if user is None:
                error = 'Incorrect username.'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password.'

            if error is None:
                session.clear()
                session['user_id'] = user['id']
                return redirect(url_for('index'))

            flash(error)

        return render_template('auth/login.html')

Có một vài khác biệt so với view ``register``:

#.  Người dùng được truy vấn trước và lưu trữ trong một biến để sử dụng sau.

    :meth:`~sqlite3.Cursor.fetchone` trả về một hàng từ truy vấn.
    Nếu truy vấn không trả về kết quả nào, nó trả về ``None``. Sau đó,
    :meth:`~sqlite3.Cursor.fetchall` sẽ được sử dụng, trả về một danh sách
    tất cả kết quả.

#.  :func:`~werkzeug.security.check_password_hash` hash mật khẩu đã gửi
    theo cùng một cách như hash được lưu trữ và so sánh chúng
    một cách an toàn. Nếu chúng khớp, mật khẩu hợp lệ.

#.  :data:`.session` là một :class:`dict` lưu trữ dữ liệu qua các request.
    Khi xác thực thành công, ``id`` của người dùng được lưu trữ trong một
    session mới. Dữ liệu được lưu trữ trong một *cookie* được gửi đến
    trình duyệt, và trình duyệt sau đó gửi nó lại với các request tiếp theo.
    Flask *ký* dữ liệu một cách an toàn để nó không thể bị giả mạo.

Bây giờ ``id`` của người dùng được lưu trữ trong :data:`.session`, nó sẽ
có sẵn trên các request tiếp theo. Ở đầu mỗi request, nếu
một người dùng đã đăng nhập, thông tin của họ nên được tải và làm cho
có sẵn cho các view khác.

.. code-block:: python
    :caption: ``flaskr/auth.py``

    @bp.before_app_request
    def load_logged_in_user():
        user_id = session.get('user_id')

        if user_id is None:
            g.user = None
        else:
            g.user = get_db().execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
            ).fetchone()

:meth:`bp.before_app_request() <Blueprint.before_app_request>` đăng ký
một hàm chạy trước view function, bất kể URL nào được
yêu cầu. ``load_logged_in_user`` kiểm tra xem một user id có được lưu trữ trong
:data:`.session` không và lấy dữ liệu của người dùng đó từ cơ sở dữ liệu, lưu trữ nó
trên :data:`g.user <g>`, tồn tại trong suốt thời gian của request. Nếu
không có user id, hoặc nếu id không tồn tại, ``g.user`` sẽ là
``None``.


Đăng xuất
---------

Để đăng xuất, bạn cần xóa user id khỏi :data:`.session`.
Sau đó ``load_logged_in_user`` sẽ không tải người dùng trên các request tiếp theo.

.. code-block:: python
    :caption: ``flaskr/auth.py``

    @bp.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))


Yêu cầu Xác thực trong Các View Khác
------------------------------------

Tạo, chỉnh sửa và xóa bài viết blog sẽ yêu cầu người dùng phải
đăng nhập. Một *decorator* có thể được sử dụng để kiểm tra điều này cho mỗi view nó được
áp dụng.

.. code-block:: python
    :caption: ``flaskr/auth.py``

    def login_required(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                return redirect(url_for('auth.login'))

            return view(**kwargs)

        return wrapped_view

Decorator này trả về một view function mới bao bọc view gốc
nó được áp dụng. Hàm mới kiểm tra xem một người dùng có được tải không và
chuyển hướng đến trang đăng nhập nếu không. Nếu một người dùng được tải, view gốc
được gọi và tiếp tục bình thường. Bạn sẽ sử dụng decorator này khi
viết các view blog.

Endpoint và URL
---------------

Hàm :func:`url_for` tạo URL đến một view dựa trên một tên
và đối số. Tên liên quan đến một view cũng được gọi là
*endpoint*, và theo mặc định nó giống với tên của view
function.

Ví dụ, view ``hello()`` đã được thêm vào app
factory trước đó trong tutorial có tên ``'hello'`` và có thể được
liên kết đến với ``url_for('hello')``. Nếu nó nhận một đối số, mà
bạn sẽ thấy sau, nó sẽ được liên kết đến bằng cách sử dụng
``url_for('hello', who='World')``.

Khi sử dụng một blueprint, tên của blueprint được thêm vào đầu
tên của hàm, vì vậy endpoint cho hàm ``login`` bạn
đã viết ở trên là ``'auth.login'`` vì bạn đã thêm nó vào blueprint ``'auth'``
.

Tiếp tục đến :doc:`templates`.
