Xác thực Form với WTForms
=========================

Khi bạn phải làm việc với dữ liệu form được gửi bởi một view trình duyệt, mã
nhanh chóng trở nên rất khó đọc. Có các thư viện được thiết kế
để làm cho quá trình này dễ quản lý hơn. Một trong số đó là `WTForms`_ mà chúng tôi
sẽ xử lý ở đây. Nếu bạn thấy mình trong tình huống có nhiều
form, bạn có thể muốn thử nó.

Khi bạn làm việc với WTForms, bạn phải định nghĩa các form của mình dưới dạng class
trước. Tôi khuyên bạn nên chia ứng dụng thành nhiều module
(:doc:`packages`) cho điều đó và thêm một module riêng biệt cho các
form.

.. admonition:: Tận dụng tối đa WTForms với một Extension

   Extension `Flask-WTF`_ mở rộng mẫu này và thêm một
   vài helper nhỏ giúp làm việc với form và Flask thú vị hơn
   . Bạn có thể lấy nó từ `PyPI
   <https://pypi.org/project/Flask-WTF/>`_.

.. _Flask-WTF: https://flask-wtf.readthedocs.io/

Các Form
--------

Đây là một form ví dụ cho một trang đăng ký điển hình::

    from wtforms import Form, BooleanField, StringField, PasswordField, validators

    class RegistrationForm(Form):
        username = StringField('Username', [validators.Length(min=4, max=25)])
        email = StringField('Email Address', [validators.Length(min=6, max=35)])
        password = PasswordField('New Password', [
            validators.DataRequired(),
            validators.EqualTo('confirm', message='Passwords must match')
        ])
        confirm = PasswordField('Repeat Password')
        accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])

Trong View
----------

Trong view function, việc sử dụng form này trông như thế này::

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm(request.form)
        if request.method == 'POST' and form.validate():
            user = User(form.username.data, form.email.data,
                        form.password.data)
            db_session.add(user)
            flash('Thanks for registering')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

Lưu ý chúng ta đang ngụ ý rằng view đang sử dụng SQLAlchemy ở đây
(:doc:`sqlalchemy`), nhưng tất nhiên đó không phải là một yêu cầu. Điều chỉnh
mã khi cần thiết.

Những điều cần nhớ:

1. tạo form từ giá trị :attr:`~flask.request.form` nếu
   dữ liệu được gửi qua phương thức HTTP ``POST`` và
   :attr:`~flask.request.args` nếu dữ liệu được gửi dưới dạng ``GET``.
2. để xác thực dữ liệu, gọi phương thức :func:`~wtforms.form.Form.validate`
   , sẽ trả về ``True`` nếu dữ liệu xác thực, ``False``
   nếu không.
3. để truy cập các giá trị riêng lẻ từ form, truy cập `form.<NAME>.data`.

Form trong Template
-------------------

Bây giờ đến phía template. Khi bạn truyền form cho các template, bạn có thể
dễ dàng render chúng ở đó. Hãy xem template ví dụ sau để thấy
điều này dễ dàng như thế nào. WTForms đã làm một nửa việc tạo form cho chúng ta rồi.
Để làm cho nó đẹp hơn nữa, chúng ta có thể viết một macro render một field với
label và danh sách các lỗi nếu có.

Đây là một template :file:`_formhelpers.html` ví dụ với một macro như vậy:

.. sourcecode:: html+jinja

    {% macro render_field(field) %}
      <dt>{{ field.label }}
      <dd>{{ field(**kwargs)|safe }}
      {% if field.errors %}
        <ul class=errors>
        {% for error in field.errors %}
          <li>{{ error }}</li>
        {% endfor %}
        </ul>
      {% endif %}
      </dd>
    {% endmacro %}

Macro này chấp nhận một vài đối số từ khóa được chuyển tiếp đến
hàm field của WTForm, hàm này render field cho chúng ta. Các đối số từ
khóa sẽ được chèn dưới dạng thuộc tính HTML. Vì vậy, ví dụ, bạn có thể
gọi ``render_field(form.username, class='username')`` để thêm một class vào
phần tử input. Lưu ý rằng WTForms trả về các chuỗi Python tiêu chuẩn,
vì vậy chúng ta phải bảo Jinja rằng dữ liệu này đã được thoát HTML với
bộ lọc ``|safe``.

Đây là template :file:`register.html` cho hàm chúng ta đã sử dụng ở trên, sử
dụng lợi thế của template :file:`_formhelpers.html`:

.. sourcecode:: html+jinja

    {% from "_formhelpers.html" import render_field %}
    <form method=post>
      <dl>
        {{ render_field(form.username) }}
        {{ render_field(form.email) }}
        {{ render_field(form.password) }}
        {{ render_field(form.confirm) }}
        {{ render_field(form.accept_tos) }}
      </dl>
      <p><input type=submit value=Register>
    </form>

Để biết thêm thông tin về WTForms, hãy truy cập `trang web WTForms
`_.

.. _WTForms: https://wtforms.readthedocs.io/
.. _WTForms website: https://wtforms.readthedocs.io/
