.. currentmodule:: flask

Template
=========

Bạn đã viết các view xác thực cho ứng dụng của mình, nhưng nếu
bạn đang chạy máy chủ và cố gắng truy cập bất kỳ URL nào, bạn sẽ thấy một
lỗi ``TemplateNotFound``. Đó là vì các view đang gọi
:func:`render_template`, nhưng bạn chưa viết các template.
Các file template sẽ được lưu trữ trong thư mục ``templates`` bên trong
package ``flaskr``.

Template là các file chứa dữ liệu tĩnh cũng như các placeholder
cho dữ liệu động. Một template được render với dữ liệu cụ thể để tạo ra một
tài liệu cuối cùng. Flask sử dụng thư viện template `Jinja`_ để render
template.

Trong ứng dụng của bạn, bạn sẽ sử dụng template để render `HTML`_ sẽ
hiển thị trong trình duyệt của người dùng. Trong Flask, Jinja được cấu hình để
*autoescape* bất kỳ dữ liệu nào được render trong các template HTML. Điều này có nghĩa là
việc render đầu vào của người dùng là an toàn; bất kỳ ký tự nào họ đã nhập có thể
làm rối HTML, chẳng hạn như ``<`` và ``>`` sẽ được *escaped* với
các giá trị *an toàn* trông giống nhau trong trình duyệt nhưng không gây ra các
hiệu ứng không mong muốn.

Jinja trông và hoạt động giống như Python. Các dấu phân cách đặc biệt được sử dụng
để phân biệt cú pháp Jinja với dữ liệu tĩnh trong template.
Bất cứ thứ gì giữa ``{{`` và ``}}`` là một biểu thức sẽ được xuất ra
tài liệu cuối cùng. ``{%`` và ``%}`` biểu thị một câu lệnh điều khiển luồng
như ``if`` và ``for``. Không giống như Python, các khối được biểu thị
bằng các thẻ bắt đầu và kết thúc thay vì thụt lề vì văn bản tĩnh trong
một khối có thể thay đổi thụt lề.

.. _Jinja: https://jinja.palletsprojects.com/templates/
.. _HTML: https://developer.mozilla.org/docs/Web/HTML


Bố cục Cơ sở
------------

Mỗi trang trong ứng dụng sẽ có cùng một bố cục cơ bản xung quanh một
nội dung khác nhau. Thay vì viết toàn bộ cấu trúc HTML trong mỗi
template, mỗi template sẽ *mở rộng* một template cơ sở và ghi đè
các phần cụ thể.

.. code-block:: html+jinja
    :caption: ``flaskr/templates/base.html``

    <!doctype html>
    <title>{% block title %}{% endblock %} - Flaskr</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <nav>
      <h1>Flaskr</h1>
      <ul>
        {% if g.user %}
          <li><span>{{ g.user['username'] }}</span>
          <li><a href="{{ url_for('auth.logout') }}">Log Out</a>
        {% else %}
          <li><a href="{{ url_for('auth.register') }}">Register</a>
          <li><a href="{{ url_for('auth.login') }}">Log In</a>
        {% endif %}
      </ul>
    </nav>
    <section class="content">
      <header>
        {% block header %}{% endblock %}
      </header>
      {% for message in get_flashed_messages() %}
        <div class="flash">{{ message }}</div>
      {% endfor %}
      {% block content %}{% endblock %}
    </section>

:data:`.g` tự động có sẵn trong các template. Dựa trên việc
``g.user`` có được đặt hay không (từ ``load_logged_in_user``), tên người dùng
và một liên kết đăng xuất được hiển thị, hoặc các liên kết để đăng ký và đăng nhập
được hiển thị. :func:`url_for` cũng tự động có sẵn, và được
sử dụng để tạo URL cho các view thay vì viết chúng ra thủ công.

Sau tiêu đề trang, và trước nội dung, template lặp qua
mỗi tin nhắn được trả về bởi :func:`get_flashed_messages`. Bạn đã sử dụng
:func:`flash` trong các view để hiển thị thông báo lỗi, và đây là mã
sẽ hiển thị chúng.

Có ba khối được định nghĩa ở đây sẽ được ghi đè trong các
template khác:

#.  ``{% block title %}`` sẽ thay đổi tiêu đề hiển thị trong
    tab và tiêu đề cửa sổ của trình duyệt.

#.  ``{% block header %}`` tương tự như ``title`` nhưng sẽ thay đổi
    tiêu đề hiển thị trên trang.

#.  ``{% block content %}`` là nơi nội dung của mỗi trang đi, chẳng hạn
    như form đăng nhập hoặc một bài viết blog.

Template cơ sở nằm trực tiếp trong thư mục ``templates``. Để giữ
các template khác được tổ chức, các template cho một blueprint sẽ được đặt trong một
thư mục có cùng tên với blueprint.


Đăng ký
-------

.. code-block:: html+jinja
    :caption: ``flaskr/templates/auth/register.html``

    {% extends 'base.html' %}

    {% block header %}
      <h1>{% block title %}Register{% endblock %}</h1>
    {% endblock %}

    {% block content %}
      <form method="post">
        <label for="username">Username</label>
        <input name="username" id="username" required>
        <label for="password">Password</label>
        <input type="password" name="password" id="password" required>
        <input type="submit" value="Register">
      </form>
    {% endblock %}

``{% extends 'base.html' %}`` cho Jinja biết rằng template này nên
thay thế các khối từ template cơ sở. Tất cả nội dung được render phải
xuất hiện bên trong các thẻ ``{% block %}`` ghi đè các khối từ template
cơ sở.

Một mẫu hữu ích được sử dụng ở đây là đặt ``{% block title %}`` bên trong
``{% block header %}``. Điều này sẽ đặt khối title và sau đó xuất
giá trị của nó vào khối header, để cả cửa sổ và trang
chia sẻ cùng một tiêu đề mà không cần viết nó hai lần.

Các thẻ ``input`` đang sử dụng thuộc tính ``required`` ở đây. Điều này cho
trình duyệt biết không gửi form cho đến khi các trường đó được điền vào. Nếu
người dùng đang sử dụng một trình duyệt cũ hơn không hỗ trợ thuộc tính đó,
hoặc nếu họ đang sử dụng một cái gì đó khác ngoài trình duyệt để thực hiện request, bạn
vẫn muốn xác thực dữ liệu trong view Flask. Điều quan trọng là
luôn xác thực đầy đủ dữ liệu trên máy chủ, ngay cả khi client cũng
thực hiện một số xác thực.


Đăng nhập
---------

Điều này giống hệt với template đăng ký ngoại trừ tiêu đề và
nút gửi.

.. code-block:: html+jinja
    :caption: ``flaskr/templates/auth/login.html``

    {% extends 'base.html' %}

    {% block header %}
      <h1>{% block title %}Log In{% endblock %}</h1>
    {% endblock %}

    {% block content %}
      <form method="post">
        <label for="username">Username</label>
        <input name="username" id="username" required>
        <label for="password">Password</label>
        <input type="password" name="password" id="password" required>
        <input type="submit" value="Log In">
      </form>
    {% endblock %}


Đăng ký Người dùng
------------------

Bây giờ các template xác thực đã được viết, bạn có thể đăng ký một
người dùng. Hãy chắc chắn rằng máy chủ vẫn đang chạy (``flask run`` nếu không),
sau đó truy cập http://127.0.0.1:5000/auth/register.

Thử nhấp vào nút "Register" mà không điền vào form và xem
rằng trình duyệt hiển thị thông báo lỗi. Thử xóa các thuộc tính ``required``
khỏi template ``register.html`` và nhấp "Register"
lại. Thay vì trình duyệt hiển thị lỗi, trang sẽ tải lại và
lỗi từ :func:`flash` trong view sẽ được hiển thị.

Điền tên người dùng và mật khẩu và bạn sẽ được chuyển hướng đến trang đăng nhập
. Thử nhập tên người dùng không chính xác, hoặc tên người dùng chính xác và
mật khẩu không chính xác. Nếu bạn đăng nhập, bạn sẽ nhận được lỗi vì chưa có
view ``index`` để chuyển hướng đến.

Tiếp tục đến :doc:`static`.
