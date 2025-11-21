Message Flashing
================

Các ứng dụng và giao diện người dùng tốt đều xoay quanh phản hồi. Nếu người dùng
không nhận được đủ phản hồi, họ có thể sẽ ghét
ứng dụng. Flask cung cấp một cách thực sự đơn giản để đưa ra phản hồi cho
người dùng với hệ thống flashing. Hệ thống flashing về cơ bản làm cho nó
có thể ghi lại một tin nhắn ở cuối một request và truy cập nó ở request
tiếp theo và chỉ request tiếp theo. Điều này thường được kết hợp với một layout
template thực hiện điều này. Lưu ý rằng các trình duyệt và đôi khi các máy chủ web thực thi
giới hạn về kích thước cookie. Điều này có nghĩa là các tin nhắn flashing quá
lớn cho session cookie sẽ khiến message flashing thất bại một cách âm thầm.

Simple Flashing
---------------

Vì vậy, đây là một ví dụ đầy đủ::

    from flask import Flask, flash, redirect, render_template, \
         request, url_for

    app = Flask(__name__)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            if request.form['username'] != 'admin' or \
                    request.form['password'] != 'secret':
                error = 'Invalid credentials'
            else:
                flash('You were successfully logged in')
                return redirect(url_for('index'))
        return render_template('login.html', error=error)

Và đây là template :file:`layout.html` thực hiện phép thuật:

.. sourcecode:: html+jinja

   <!doctype html>
   <title>My Application</title>
   {% with messages = get_flashed_messages() %}
     {% if messages %}
       <ul class=flashes>
       {% for message in messages %}
         <li>{{ message }}</li>
       {% endfor %}
       </ul>
     {% endif %}
   {% endwith %}
   {% block body %}{% endblock %}

Đây là template :file:`index.html` kế thừa từ :file:`layout.html`:

.. sourcecode:: html+jinja

   {% extends "layout.html" %}
   {% block body %}
     <h1>Overview</h1>
     <p>Do you want to <a href="{{ url_for('login') }}">log in?</a>
   {% endblock %}

Và đây là template :file:`login.html` cũng kế thừa từ
:file:`layout.html`:

.. sourcecode:: html+jinja

   {% extends "layout.html" %}
   {% block body %}
     <h1>Login</h1>
     {% if error %}
       <p class=error><strong>Error:</strong> {{ error }}
     {% endif %}
     <form method=post>
       <dl>
         <dt>Username:
         <dd><input type=text name=username value="{{
             request.form.username }}">
         <dt>Password:
         <dd><input type=password name=password>
       </dl>
       <p><input type=submit value=Login>
     </form>
   {% endblock %}

Flashing Với Categories
-----------------------

.. versionadded:: 0.3

Cũng có thể cung cấp các category khi flash một tin nhắn.
Category mặc định nếu không có gì được cung cấp là ``'message'``. Các category
thay thế có thể được sử dụng để cung cấp cho người dùng phản hồi tốt hơn. Ví dụ
các thông báo lỗi có thể được hiển thị với nền màu đỏ.

Để flash một tin nhắn với một category khác, chỉ cần sử dụng đối số thứ hai
cho hàm :func:`~flask.flash`::

    flash('Invalid password provided', 'error')

Bên trong template, sau đó bạn phải bảo hàm
:func:`~flask.get_flashed_messages` cũng trả về các
category. Vòng lặp trông hơi khác trong tình huống đó:

.. sourcecode:: html+jinja

   {% with messages = get_flashed_messages(with_categories=true) %}
     {% if messages %}
       <ul class=flashes>
       {% for category, message in messages %}
         <li class="{{ category }}">{{ message }}</li>
       {% endfor %}
       </ul>
     {% endif %}
   {% endwith %}

Đây chỉ là một ví dụ về cách render các tin nhắn flashed này. Một người
cũng có thể sử dụng category để thêm một tiền tố chẳng hạn như
``<strong>Error:</strong>`` vào tin nhắn.

Lọc Flash Messages
------------------

.. versionadded:: 0.9

Tùy chọn bạn có thể truyền một danh sách các category để lọc kết quả của
:func:`~flask.get_flashed_messages`. Điều này hữu ích nếu bạn muốn
render từng category trong một khối riêng biệt.

.. sourcecode:: html+jinja

    {% with errors = get_flashed_messages(category_filter=["error"]) %}
    {% if errors %}
    <div class="alert-message block-message error">
      <a class="close" href="#">×</a>
      <ul>
        {%- for msg in errors %}
        <li>{{ msg }}</li>
        {% endfor -%}
      </ul>
    </div>
    {% endif %}
    {% endwith %}
