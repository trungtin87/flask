.. currentmodule:: flask

Blueprint Blog
==============

Bạn sẽ sử dụng các kỹ thuật tương tự mà bạn đã học khi viết
blueprint xác thực để viết blueprint blog. Blog nên
liệt kê tất cả các bài viết, cho phép người dùng đã đăng nhập tạo bài viết, và cho phép
tác giả của một bài viết chỉnh sửa hoặc xóa nó.

Khi bạn triển khai mỗi view, hãy giữ máy chủ phát triển chạy. Khi bạn
lưu các thay đổi của mình, hãy thử truy cập URL trong trình duyệt và kiểm tra chúng
.

Blueprint
---------

Định nghĩa blueprint và đăng ký nó trong application factory.

.. code-block:: python
    :caption: ``flaskr/blog.py``

    from flask import (
        Blueprint, flash, g, redirect, render_template, request, url_for
    )
    from werkzeug.exceptions import abort

    from flaskr.auth import login_required
    from flaskr.db import get_db

    bp = Blueprint('blog', __name__)

Import và đăng ký blueprint từ factory bằng cách sử dụng
:meth:`app.register_blueprint() <Flask.register_blueprint>`. Đặt
mã mới ở cuối hàm factory trước khi trả về ứng dụng.

.. code-block:: python
    :caption: ``flaskr/__init__.py``

    def create_app():
        app = ...
        # existing code omitted

        from . import blog
        app.register_blueprint(blog.bp)
        app.add_url_rule('/', endpoint='index')

        return app


Không giống như blueprint auth, blueprint blog không có
``url_prefix``. Vì vậy view ``index`` sẽ ở ``/``, view ``create``
ở ``/create``, v.v. Blog là tính năng chính của Flaskr,
vì vậy hợp lý khi index blog sẽ là index chính.

Tuy nhiên, endpoint cho view ``index`` được định nghĩa bên dưới sẽ là
``blog.index``. Một số view xác thực đã tham chiếu đến một endpoint
``index`` đơn giản. :meth:`app.add_url_rule() <Flask.add_url_rule>`
liên kết tên endpoint ``'index'`` với url ``/`` để
``url_for('index')`` hoặc ``url_for('blog.index')`` đều hoạt động,
tạo ra cùng một URL ``/`` theo cả hai cách.

Trong một ứng dụng khác, bạn có thể cung cấp cho blueprint blog một
``url_prefix`` và định nghĩa một view ``index`` riêng biệt trong application
factory, tương tự như view ``hello``. Sau đó các endpoint và URL ``index`` và
``blog.index`` sẽ khác nhau.


Index
-----

Index sẽ hiển thị tất cả các bài viết, gần đây nhất trước. Một ``JOIN`` được
sử dụng để thông tin tác giả từ bảng ``user`` có sẵn
trong kết quả.

.. code-block:: python
    :caption: ``flaskr/blog.py``

    @bp.route('/')
    def index():
        db = get_db()
        posts = db.execute(
            'SELECT p.id, title, body, created, author_id, username'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' ORDER BY created DESC'
        ).fetchall()
        return render_template('blog/index.html', posts=posts)

.. code-block:: html+jinja
    :caption: ``flaskr/templates/blog/index.html``

    {% extends 'base.html' %}

    {% block header %}
      <h1>{% block title %}Posts{% endblock %}</h1>
      {% if g.user %}
        <a class="action" href="{{ url_for('blog.create') }}">New</a>
      {% endif %}
    {% endblock %}

    {% block content %}
      {% for post in posts %}
        <article class="post">
          <header>
            <div>
              <h1>{{ post['title'] }}</h1>
              <div class="about">by {{ post['username'] }} on {{ post['created'].strftime('%Y-%m-%d') }}</div>
            </div>
            {% if g.user['id'] == post['author_id'] %}
              <a class="action" href="{{ url_for('blog.update', id=post['id']) }}">Edit</a>
            {% endif %}
          </header>
          <p class="body">{{ post['body'] }}</p>
        </article>
        {% if not loop.last %}
          <hr>
        {% endif %}
      {% endfor %}
    {% endblock %}

Khi một người dùng đã đăng nhập, khối ``header`` thêm một liên kết đến view
``create``. Khi người dùng là tác giả của một bài viết, họ sẽ thấy một
liên kết "Edit" đến view ``update`` cho bài viết đó. ``loop.last`` là một
biến đặc biệt có sẵn bên trong `vòng lặp for Jinja`_. Nó được sử dụng để
hiển thị một dòng sau mỗi bài viết ngoại trừ bài cuối cùng, để tách biệt chúng
một cách trực quan.

.. _Jinja for loops: https://jinja.palletsprojects.com/templates/#for


Tạo
---

View ``create`` hoạt động giống như view ``register`` của auth. Hoặc
form được hiển thị, hoặc dữ liệu đã đăng được xác thực và bài viết được
thêm vào cơ sở dữ liệu hoặc một lỗi được hiển thị.

Decorator ``login_required`` mà bạn đã viết trước đó được sử dụng trên các view
blog. Một người dùng phải đăng nhập để truy cập các view này, nếu không họ
sẽ được chuyển hướng đến trang đăng nhập.

.. code-block:: python
    :caption: ``flaskr/blog.py``

    @bp.route('/create', methods=('GET', 'POST'))
    @login_required
    def create():
        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']
            error = None

            if not title:
                error = 'Title is required.'

            if error is not None:
                flash(error)
            else:
                db = get_db()
                db.execute(
                    'INSERT INTO post (title, body, author_id)'
                    ' VALUES (?, ?, ?)',
                    (title, body, g.user['id'])
                )
                db.commit()
                return redirect(url_for('blog.index'))

        return render_template('blog/create.html')

.. code-block:: html+jinja
    :caption: ``flaskr/templates/blog/create.html``

    {% extends 'base.html' %}

    {% block header %}
      <h1>{% block title %}New Post{% endblock %}</h1>
    {% endblock %}

    {% block content %}
      <form method="post">
        <label for="title">Title</label>
        <input name="title" id="title" value="{{ request.form['title'] }}" required>
        <label for="body">Body</label>
        <textarea name="body" id="body">{{ request.form['body'] }}</textarea>
        <input type="submit" value="Save">
      </form>
    {% endblock %}


Cập nhật
--------

Cả view ``update`` và ``delete`` đều cần lấy một ``post``
theo ``id`` và kiểm tra xem tác giả có khớp với người dùng đã đăng nhập không. Để tránh
trùng lặp mã, bạn có thể viết một hàm để lấy ``post`` và gọi
nó từ mỗi view.

.. code-block:: python
    :caption: ``flaskr/blog.py``

    def get_post(id, check_author=True):
        post = get_db().execute(
            'SELECT p.id, title, body, created, author_id, username'
            ' FROM post p JOIN user u ON p.author_id = u.id'
            ' WHERE p.id = ?',
            (id,)
        ).fetchone()

        if post is None:
            abort(404, f"Post id {id} doesn't exist.")

        if check_author and post['author_id'] != g.user['id']:
            abort(403)

        return post

:func:`abort` sẽ đưa ra một exception đặc biệt trả về một mã trạng thái HTTP
. Nó nhận một tin nhắn tùy chọn để hiển thị với lỗi, nếu không một
tin nhắn mặc định được sử dụng. ``404`` có nghĩa là "Not Found", và ``403`` có nghĩa là
"Forbidden". (``401`` có nghĩa là "Unauthorized", nhưng bạn chuyển hướng đến
trang đăng nhập thay vì trả về trạng thái đó.)

Đối số ``check_author`` được định nghĩa để hàm có thể được
sử dụng để lấy một ``post`` mà không cần kiểm tra tác giả. Điều này sẽ hữu ích
nếu bạn viết một view để hiển thị một bài viết riêng lẻ trên một trang, nơi người dùng
không quan trọng vì họ không sửa đổi bài viết.

.. code-block:: python
    :caption: ``flaskr/blog.py``

    @bp.route('/<int:id>/update', methods=('GET', 'POST'))
    @login_required
    def update(id):
        post = get_post(id)

        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']
            error = None

            if not title:
                error = 'Title is required.'

            if error is not None:
                flash(error)
            else:
                db = get_db()
                db.execute(
                    'UPDATE post SET title = ?, body = ?'
                    ' WHERE id = ?',
                    (title, body, id)
                )
                db.commit()
                return redirect(url_for('blog.index'))

        return render_template('blog/update.html', post=post)

Không giống như các view bạn đã viết cho đến nay, hàm ``update`` nhận
một đối số, ``id``. Điều đó tương ứng với ``<int:id>`` trong route.
Một URL thực sẽ trông giống như ``/1/update``. Flask sẽ bắt ``1``,
đảm bảo nó là một :class:`int`, và truyền nó làm đối số ``id``. Nếu bạn
không chỉ định ``int:`` và thay vào đó làm ``<id>``, nó sẽ là một chuỗi.
Để tạo một URL đến trang cập nhật, :func:`url_for` cần được truyền
``id`` để nó biết điền gì vào:
``url_for('blog.update', id=post['id'])``. Điều này cũng có trong
file ``index.html`` ở trên.

Các view ``create`` và ``update`` trông rất giống nhau. Sự khác biệt chính
là view ``update`` sử dụng một đối tượng ``post`` và một
truy vấn ``UPDATE`` thay vì ``INSERT``. Với một số tái cấu trúc thông minh,
bạn có thể sử dụng một view và template cho cả hai hành động, nhưng cho
tutorial, rõ ràng hơn khi giữ chúng riêng biệt.

.. code-block:: html+jinja
    :caption: ``flaskr/templates/blog/update.html``

    {% extends 'base.html' %}

    {% block header %}
      <h1>{% block title %}Edit "{{ post['title'] }}"{% endblock %}</h1>
    {% endblock %}

    {% block content %}
      <form method="post">
        <label for="title">Title</label>
        <input name="title" id="title"
          value="{{ request.form['title'] or post['title'] }}" required>
        <label for="body">Body</label>
        <textarea name="body" id="body">{{ request.form['body'] or post['body'] }}</textarea>
        <input type="submit" value="Save">
      </form>
      <hr>
      <form action="{{ url_for('blog.delete', id=post['id']) }}" method="post">
        <input class="danger" type="submit" value="Delete" onclick="return confirm('Are you sure?');">
      </form>
    {% endblock %}

Template này có hai form. Form đầu tiên đăng dữ liệu đã chỉnh sửa đến
trang hiện tại (``/<id>/update``). Form khác chỉ chứa một nút
và chỉ định một thuộc tính ``action`` đăng đến view delete
thay thế. Nút sử dụng một số JavaScript để hiển thị hộp thoại xác nhận
trước khi gửi.

Mẫu ``{{ request.form['title'] or post['title'] }}`` được sử dụng để
chọn dữ liệu nào xuất hiện trong form. Khi form chưa được
gửi, dữ liệu ``post`` gốc xuất hiện, nhưng nếu dữ liệu form không hợp lệ
được đăng, bạn muốn hiển thị điều đó để người dùng có thể sửa lỗi, vì vậy
``request.form`` được sử dụng thay thế. :data:`.request` là một biến khác
tự động có sẵn trong các template.


Xóa
---

View delete không có template riêng, nút delete là một phần
của ``update.html`` và đăng đến URL ``/<id>/delete``. Vì không có
template, nó sẽ chỉ xử lý phương thức ``POST`` và sau đó chuyển hướng
đến view ``index``.

.. code-block:: python
    :caption: ``flaskr/blog.py``

    @bp.route('/<int:id>/delete', methods=('POST',))
    @login_required
    def delete(id):
        get_post(id)
        db = get_db()
        db.execute('DELETE FROM post WHERE id = ?', (id,))
        db.commit()
        return redirect(url_for('blog.index'))

Chúc mừng, bạn đã hoàn thành việc viết ứng dụng của mình! Hãy dành một chút
thời gian để thử mọi thứ trong trình duyệt. Tuy nhiên, vẫn còn nhiều việc
cần làm trước khi dự án hoàn thành.

Tiếp tục đến :doc:`install`.
