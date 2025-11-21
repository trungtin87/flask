Template
=========

Flask tận dụng Jinja làm template engine của nó. Bạn rõ ràng tự do sử dụng
một template engine khác, nhưng bạn vẫn phải cài đặt Jinja để chạy
chính Flask. Yêu cầu này là cần thiết để cho phép các extension phong phú.
Một extension có thể phụ thuộc vào sự hiện diện của Jinja.

Phần này chỉ cung cấp một giới thiệu rất nhanh về cách Jinja
được tích hợp vào Flask. Nếu bạn muốn thông tin về cú pháp
của chính template engine, hãy truy cập `Tài liệu Jinja Template
chính thức <https://jinja.palletsprojects.com/templates/>`_ để biết
thêm thông tin.

Thiết lập Jinja
---------------

Trừ khi được tùy chỉnh, Jinja được cấu hình bởi Flask như sau:

-   autoescaping được bật cho tất cả các template kết thúc bằng ``.html``,
    ``.htm``, ``.xml``, ``.xhtml``, cũng như ``.svg`` khi sử dụng
    :func:`~flask.templating.render_template`.
-   autoescaping được bật cho tất cả các chuỗi khi sử dụng
    :func:`~flask.templating.render_template_string`.
-   một template có khả năng opt in/out autoescaping với
    thẻ ``{% autoescape %}``.
-   Flask chèn một vài hàm và helper toàn cục vào
    context Jinja, bổ sung cho các giá trị có sẵn theo
    mặc định.

Context Tiêu chuẩn
------------------

Các biến toàn cục sau có sẵn trong các template Jinja
theo mặc định:

.. data:: config
   :noindex:

   Đối tượng cấu hình hiện tại (:data:`flask.Flask.config`)

   .. versionadded:: 0.6

   .. versionchanged:: 0.10
      Điều này hiện luôn có sẵn, ngay cả trong các template được import.

.. data:: request
   :noindex:

   Đối tượng request hiện tại (:class:`flask.request`). Biến này
   không có sẵn nếu template được render mà không có request
   context hoạt động.

.. data:: session
   :noindex:

   Đối tượng session hiện tại (:class:`flask.session`). Biến này
   không có sẵn nếu template được render mà không có request
   context hoạt động.

.. data:: g
   :noindex:

   Đối tượng liên kết request cho các biến toàn cục (:data:`flask.g`). Biến
   này không có sẵn nếu template được render mà không có
   request context hoạt động.

.. function:: url_for
   :noindex:

   Hàm :func:`flask.url_for`.

.. function:: get_flashed_messages
   :noindex:

   Hàm :func:`flask.get_flashed_messages`.

.. admonition:: Hành vi Context Jinja

   Các biến này được thêm vào context của các biến, chúng không phải là
   biến toàn cục. Sự khác biệt là theo mặc định chúng sẽ không
   xuất hiện trong context của các template được import. Điều này một phần do
   các cân nhắc về hiệu suất, một phần để giữ mọi thứ rõ ràng.

   Điều này có nghĩa gì đối với bạn? Nếu bạn có một macro bạn muốn import,
   cần truy cập đối tượng request, bạn có hai khả năng:

   1.   bạn truyền rõ ràng request cho macro làm tham số, hoặc
        thuộc tính của đối tượng request mà bạn quan tâm.
   2.   bạn import macro "with context".

   Import với context trông như thế này:

   .. sourcecode:: jinja

      {% from '_helpers.html' import my_macro with context %}


Kiểm soát Autoescaping
-----------------------

Autoescaping là khái niệm tự động escape các ký tự đặc biệt
cho bạn. Các ký tự đặc biệt theo nghĩa của HTML (hoặc XML, và do đó XHTML)
là ``&``, ``>``, ``<``, ``"`` cũng như ``'``. Bởi vì các ký tự này
mang ý nghĩa cụ thể trong các tài liệu riêng của chúng, bạn phải thay thế chúng
bằng cái gọi là "entity" nếu bạn muốn sử dụng chúng cho văn bản. Không làm như vậy
sẽ không chỉ gây ra sự thất vọng của người dùng do không thể sử dụng các
ký tự này trong văn bản, mà còn có thể dẫn đến các vấn đề bảo mật. (xem
:ref:`security-xss`)

Tuy nhiên đôi khi bạn sẽ cần tắt autoescaping trong các template.
Điều này có thể là trường hợp nếu bạn muốn chèn HTML một cách rõ ràng vào các trang, ví dụ
nếu chúng đến từ một hệ thống tạo HTML an toàn như một
bộ chuyển đổi markdown sang HTML.

Có ba cách để thực hiện điều đó:

-   Trong mã Python, wrap chuỗi HTML trong một đối tượng :class:`~markupsafe.Markup`
    trước khi truyền nó cho template. Đây nói chung là
    cách được khuyến nghị.
-   Bên trong template, sử dụng filter ``|safe`` để đánh dấu rõ ràng một
    chuỗi là HTML an toàn (``{{ myvariable|safe }}``)
-   Tạm thời tắt hệ thống autoescape hoàn toàn.

Để tắt hệ thống autoescape trong các template, bạn có thể sử dụng khối ``{%
autoescape %}``:

.. sourcecode:: html+jinja

    {% autoescape false %}
        <p>autoescaping is disabled here
        <p>{{ will_not_be_escaped }}
    {% endautoescape %}

Bất cứ khi nào bạn làm điều này, hãy rất cẩn thận về các biến bạn đang
sử dụng trong khối này.

.. _registering-filters:

Đăng ký Filter, Test, và Global
--------------------------------

Ứng dụng Flask và blueprint cung cấp decorator và phương thức để đăng ký
filter, test, và hàm toàn cục của riêng bạn để sử dụng trong các template Jinja. Tất cả chúng đều tuân theo
cùng một mẫu, vì vậy các ví dụ sau chỉ thảo luận về filter.

Decorate một hàm với :meth:`~.Flask.template_filter` để đăng ký nó làm một
template filter.

.. code-block:: python

    @app.template_filter
    def reverse(s):
        return reversed(s)

.. code-block:: jinja

    {% for item in data | reverse %}
    {% endfor %}

Theo mặc định, nó sẽ sử dụng tên của hàm làm tên của filter, nhưng
điều đó có thể được thay đổi bằng cách truyền một tên cho decorator.

.. code-block:: python

    @app.template_filter("reverse")
    def reverse_filter(s):
        return reversed(s)

Một filter có thể được đăng ký riêng biệt bằng cách sử dụng :meth:`~.Flask.add_template_filter`.
Tên là tùy chọn và sẽ sử dụng tên hàm nếu không được cung cấp.

.. code-block:: python

    def reverse_filter(s):
        return reversed(s)

    app.add_template_filter(reverse_filter, "reverse")

Đối với template test, sử dụng decorator :meth:`~.Flask.template_test` hoặc
phương thức :meth:`~.Flask.add_template_test`. Đối với các hàm toàn cục template, sử dụng
decorator :meth:`~.Flask.template_global` hoặc phương thức :meth:`~.Flask.add_template_global`
.

Các phương thức tương tự cũng tồn tại trên :class:`.Blueprint`, được tiền tố với ``app_`` để
chỉ ra rằng các hàm được đăng ký sẽ có sẵn cho tất cả các template, không
chỉ khi rendering từ trong blueprint.

Môi trường Jinja cũng có sẵn dưới dạng :attr:`~.Flask.jinja_env`. Nó có thể được
sửa đổi trực tiếp, như bạn sẽ làm khi sử dụng Jinja bên ngoài Flask.


Context Processor
-----------------

Để chèn các biến mới tự động vào context của một template,
các context processor tồn tại trong Flask. Context processor chạy trước khi
template được render và có khả năng chèn các giá trị mới vào
context template. Một context processor là một hàm trả về một
dictionary. Các khóa và giá trị của dictionary này sau đó được hợp nhất với
context template, cho tất cả các template trong ứng dụng::

    @app.context_processor
    def inject_user():
        return dict(user=g.user)

Context processor ở trên làm cho một biến có tên `user` có sẵn trong
template với giá trị của `g.user`. Ví dụ này không thú vị lắm
vì `g` có sẵn trong các template, nhưng nó cung cấp một
ý tưởng về cách điều này hoạt động.

Các biến không giới hạn ở các giá trị; một context processor cũng có thể làm cho
các hàm có sẵn cho các template (vì Python cho phép truyền xung quanh
các hàm)::

    @app.context_processor
    def utility_processor():
        def format_price(amount, currency="€"):
            return f"{amount:.2f}{currency}"
        return dict(format_price=format_price)

Context processor ở trên làm cho hàm `format_price` có sẵn cho tất cả
các template::

    {{ format_price(0.33) }}

Bạn cũng có thể xây dựng `format_price` làm một template filter (xem
:ref:`registering-filters`), nhưng điều này chứng minh cách truyền các hàm trong một
context processor.

Streaming
---------

Có thể hữu ích khi không render toàn bộ template thành một chuỗi hoàn chỉnh
, thay vào đó render nó dưới dạng một stream, yielding các chuỗi tăng dần nhỏ hơn
. Điều này có thể được sử dụng để streaming HTML theo từng chunk để tăng tốc
tải trang ban đầu, hoặc để tiết kiệm bộ nhớ khi rendering một template
rất lớn.

Template engine Jinja hỗ trợ rendering một template từng
phần, trả về một iterator của các chuỗi. Flask cung cấp
các hàm :func:`~flask.stream_template` và :func:`~flask.stream_template_string`
để làm cho điều này dễ sử dụng hơn.

.. code-block:: python

    from flask import stream_template

    @app.get("/timeline")
    def timeline():
        return stream_template("timeline.html")

Các hàm này tự động áp dụng
wrapper :func:`~flask.stream_with_context` nếu một request đang hoạt động, để
nó vẫn có sẵn trong template.
