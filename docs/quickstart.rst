Bắt đầu nhanh
=============

Bạn đang nóng lòng muốn bắt đầu? Trang này cung cấp một giới thiệu tốt về Flask.
Hãy làm theo :doc:`installation` để thiết lập dự án và cài đặt Flask trước.


Một Ứng dụng Tối thiểu
----------------------

Một ứng dụng Flask tối thiểu trông giống như thế này:

.. code-block:: python

    from flask import Flask

    app = Flask(__name__)

    @app.route("/")
    def hello_world():
        return "<p>Hello, World!</p>"

Vậy đoạn mã đó đã làm gì?

1.  Đầu tiên chúng ta import lớp :class:`~flask.Flask`. Một thể hiện của
    lớp này sẽ là ứng dụng WSGI của chúng ta.
2.  Tiếp theo chúng ta tạo một thể hiện của lớp này. Đối số đầu tiên là
    tên của module hoặc package của ứng dụng. ``__name__`` là một
    lối tắt thuận tiện cho việc này, phù hợp cho hầu hết các trường hợp.
    Điều này là cần thiết để Flask biết nơi tìm kiếm các tài nguyên như
    template và file tĩnh.
3.  Sau đó chúng ta sử dụng decorator :meth:`~flask.Flask.route` để cho Flask biết
    URL nào sẽ kích hoạt hàm của chúng ta.
4.  Hàm trả về thông điệp chúng ta muốn hiển thị trong trình duyệt của người dùng.
    Loại nội dung mặc định là HTML, vì vậy HTML trong chuỗi
    sẽ được trình duyệt render.

Lưu nó dưới tên :file:`hello.py` hoặc tương tự. Đảm bảo không đặt tên
ứng dụng của bạn là :file:`flask.py` vì điều này sẽ xung đột với chính Flask.

Để chạy ứng dụng, sử dụng lệnh ``flask`` hoặc
``python -m flask``. Bạn cần cho Flask biết ứng dụng của bạn ở đâu
bằng tùy chọn ``--app``.

.. code-block:: text

    $ flask --app hello run
     * Serving Flask app 'hello'
     * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)

.. admonition:: Hành vi Khám phá Ứng dụng

    Như một lối tắt, nếu file được đặt tên là ``app.py`` hoặc ``wsgi.py``, bạn
    không cần phải sử dụng ``--app``. Xem :doc:`/cli` để biết thêm chi tiết.

Điều này khởi chạy một máy chủ tích hợp rất đơn giản, đủ tốt để
thử nghiệm nhưng có lẽ không phải là thứ bạn muốn sử dụng trong sản xuất. Để biết các tùy chọn
triển khai, xem :doc:`deploying/index`.

Bây giờ hãy truy cập http://127.0.0.1:5000/, và bạn sẽ thấy lời chào hello
world của mình.

Nếu một chương trình khác đã sử dụng cổng 5000, bạn sẽ thấy
``OSError: [Errno 98]`` hoặc ``OSError: [WinError 10013]`` khi
máy chủ cố gắng khởi động. Xem :ref:`address-already-in-use` để biết cách
xử lý điều đó.

.. _public-server:

.. admonition:: Máy chủ Hiển thị ra Bên ngoài

   Nếu bạn chạy máy chủ, bạn sẽ nhận thấy rằng máy chủ chỉ có thể truy cập được
   từ máy tính của riêng bạn, không phải từ bất kỳ máy nào khác trong mạng. Đây là
   mặc định vì trong chế độ debug, người dùng ứng dụng có thể thực thi
   mã Python tùy ý trên máy tính của bạn.

   Nếu bạn đã tắt debugger hoặc tin tưởng người dùng trên mạng của mình,
   bạn có thể làm cho máy chủ khả dụng công khai chỉ bằng cách thêm
   ``--host=0.0.0.0`` vào dòng lệnh::

       $ flask run --host=0.0.0.0

   Điều này bảo hệ điều hành của bạn lắng nghe trên tất cả các IP công cộng.


Chế độ Debug
------------

Lệnh ``flask run`` có thể làm nhiều hơn là chỉ khởi động máy chủ phát triển.
Bằng cách bật chế độ debug, máy chủ sẽ tự động tải lại nếu
mã thay đổi, và sẽ hiển thị một trình gỡ lỗi tương tác trong trình duyệt nếu một
lỗi xảy ra trong quá trình request.

.. image:: _static/debugger.png
    :align: center
    :class: screenshot
    :alt: Trình gỡ lỗi tương tác đang hoạt động.

.. warning::

    Trình gỡ lỗi cho phép thực thi mã Python tùy ý từ
    trình duyệt. Nó được bảo vệ bởi một mã PIN, nhưng vẫn đại diện cho một rủi ro
    bảo mật lớn. Không chạy máy chủ phát triển hoặc trình gỡ lỗi trong một
    môi trường sản xuất.

Để bật chế độ debug, sử dụng tùy chọn ``--debug``.

.. code-block:: text

    $ flask --app hello run --debug
     * Serving Flask app 'hello'
     * Debug mode: on
     * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
     * Restarting with stat
     * Debugger is active!
     * Debugger PIN: nnn-nnn-nnn

Xem thêm:

-   :doc:`/server` và :doc:`/cli` để biết thông tin về việc chạy trong chế độ debug.
-   :doc:`/debugging` để biết thông tin về việc sử dụng trình gỡ lỗi tích hợp
    và các trình gỡ lỗi khác.
-   :doc:`/logging` và :doc:`/errorhandling` để ghi log lỗi và hiển thị
    các trang lỗi đẹp mắt.


Escape HTML
-----------

Khi trả về HTML (loại phản hồi mặc định trong Flask), bất kỳ
giá trị nào do người dùng cung cấp được render trong đầu ra phải được escape để bảo vệ
khỏi các cuộc tấn công injection. Các template HTML được render bằng Jinja, được giới thiệu
sau, sẽ tự động làm điều này.

:func:`~markupsafe.escape`, được hiển thị ở đây, có thể được sử dụng thủ công. Nó bị
lược bỏ trong hầu hết các ví dụ cho ngắn gọn, nhưng bạn phải luôn nhận thức được
cách bạn đang sử dụng dữ liệu không tin cậy.

.. code-block:: python

    from flask import request
    from markupsafe import escape

    @app.route("/hello")
    def hello():
        name = request.args.get("name", "Flask")
        return f"Hello, {escape(name)}!"

Nếu một người dùng gửi ``/hello?name=<script>alert("bad")</script>``, việc escape khiến
nó được render dưới dạng văn bản, thay vì chạy script trong trình duyệt của người dùng.


Định tuyến (Routing)
--------------------

Các ứng dụng web hiện đại sử dụng các URL có ý nghĩa để giúp người dùng. Người dùng có nhiều khả năng
thích một trang và quay lại nếu trang đó sử dụng một URL có ý nghĩa mà họ có thể
nhớ và sử dụng để truy cập trực tiếp vào một trang.

Sử dụng decorator :meth:`~flask.Flask.route` để liên kết một hàm với một URL. ::

    @app.route('/')
    def index():
        return 'Index Page'

    @app.route('/hello')
    def hello():
        return 'Hello, World'

Bạn có thể làm nhiều hơn nữa! Bạn có thể làm cho các phần của URL trở nên động và gắn nhiều
quy tắc vào một hàm.

Quy tắc Biến
````````````

Bạn có thể thêm các phần biến vào một URL bằng cách đánh dấu các phần bằng
``<variable_name>``. Hàm của bạn sau đó nhận ``<variable_name>``
như một đối số từ khóa. Tùy chọn, bạn có thể sử dụng một bộ chuyển đổi để chỉ định loại
của đối số như ``<converter:variable_name>``. ::

    from markupsafe import escape

    @app.route('/user/<username>')
    def show_user_profile(username):
        # hiển thị hồ sơ người dùng cho người dùng đó
        return f'User {escape(username)}'

    @app.route('/post/<int:post_id>')
    def show_post(post_id):
        # hiển thị bài đăng với id đã cho, id là một số nguyên
        return f'Post {post_id}'

    @app.route('/path/<path:subpath>')
    def show_subpath(subpath):
        # hiển thị đường dẫn con sau /path/
        return f'Subpath {escape(subpath)}'

Các loại bộ chuyển đổi:

========== ==========================================
``string`` (mặc định) chấp nhận bất kỳ văn bản nào không có dấu gạch chéo
``int``    chấp nhận các số nguyên dương
``float``  chấp nhận các giá trị dấu phẩy động dương
``path``   giống như ``string`` nhưng cũng chấp nhận các dấu gạch chéo
``uuid``   chấp nhận các chuỗi UUID
========== ==========================================


URL Duy nhất / Hành vi Chuyển hướng
```````````````````````````````````

Hai quy tắc sau khác nhau ở việc sử dụng dấu gạch chéo ở cuối. ::

    @app.route('/projects/')
    def projects():
        return 'The project page'

    @app.route('/about')
    def about():
        return 'The about page'

URL chính tắc cho endpoint ``projects`` có một dấu gạch chéo ở cuối.
Nó tương tự như một thư mục trong hệ thống tệp. Nếu bạn truy cập URL mà không có
dấu gạch chéo ở cuối (``/projects``), Flask chuyển hướng bạn đến URL chính tắc
với dấu gạch chéo ở cuối (``/projects/``).

URL chính tắc cho endpoint ``about`` không có dấu gạch chéo ở cuối.
Nó tương tự như tên đường dẫn của một tệp. Truy cập URL với một
dấu gạch chéo ở cuối (``/about/``) tạo ra lỗi 404 "Not Found". Điều này giúp
giữ cho các URL là duy nhất cho các tài nguyên này, giúp các công cụ tìm kiếm tránh
lập chỉ mục cùng một trang hai lần.


.. _url-building:

Xây dựng URL
````````````

Để xây dựng một URL đến một hàm cụ thể, sử dụng hàm :func:`~flask.url_for`.
Nó chấp nhận tên của hàm làm đối số đầu tiên và bất kỳ số lượng
đối số từ khóa nào, mỗi đối số tương ứng với một phần biến của quy tắc URL.
Các phần biến không xác định được thêm vào URL dưới dạng tham số truy vấn.

Tại sao bạn lại muốn xây dựng URL bằng cách sử dụng hàm đảo ngược URL
:func:`~flask.url_for` thay vì mã hóa cứng chúng vào template của bạn?

1. Đảo ngược thường mô tả rõ ràng hơn là mã hóa cứng các URL.
2. Bạn có thể thay đổi URL của mình trong một lần thay vì cần nhớ để
   thay đổi thủ công các URL được mã hóa cứng.
3. Xây dựng URL xử lý việc escape các ký tự đặc biệt một cách minh bạch.
4. Các đường dẫn được tạo luôn là tuyệt đối, tránh hành vi không mong muốn
   của các đường dẫn tương đối trong trình duyệt.
5. Nếu ứng dụng của bạn được đặt bên ngoài thư mục gốc URL, ví dụ, trong
   ``/myapplication`` thay vì ``/``, :func:`~flask.url_for` xử lý đúng
   điều đó cho bạn.

Ví dụ, ở đây chúng ta sử dụng phương thức :meth:`~flask.Flask.test_request_context`
để thử nghiệm :func:`~flask.url_for`. :meth:`~flask.Flask.test_request_context`
bảo Flask hành xử như thể nó đang xử lý một request ngay cả khi chúng ta sử dụng một
Python shell. Xem :doc:`/appcontext`.

.. code-block:: python

    from flask import url_for

    @app.route('/')
    def index():
        return 'index'

    @app.route('/login')
    def login():
        return 'login'

    @app.route('/user/<username>')
    def profile(username):
        return f'{username}\'s profile'

    with app.test_request_context():
        print(url_for('index'))
        print(url_for('login'))
        print(url_for('login', next='/'))
        print(url_for('profile', username='John Doe'))

.. code-block:: text

    /
    /login
    /login?next=/
    /user/John%20Doe


Phương thức HTTP
````````````````

Các ứng dụng web sử dụng các phương thức HTTP khác nhau khi truy cập URL. Bạn nên
làm quen với các phương thức HTTP khi làm việc với Flask. Theo mặc định,
một route chỉ trả lời các request ``GET``. Bạn có thể sử dụng đối số ``methods``
của decorator :meth:`~flask.Flask.route` để xử lý các phương thức HTTP khác nhau.
::

    from flask import request

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            return do_the_login()
        else:
            return show_the_login_form()

Ví dụ trên giữ tất cả các phương thức cho route trong một hàm,
điều này có thể hữu ích nếu mỗi phần sử dụng một số dữ liệu chung.

Bạn cũng có thể tách các view cho các phương thức khác nhau thành các hàm
khác nhau. Flask cung cấp một lối tắt để trang trí các route như vậy với
:meth:`~flask.Flask.get`, :meth:`~flask.Flask.post`, v.v. cho mỗi
phương thức HTTP phổ biến.

.. code-block:: python

    @app.get('/login')
    def login_get():
        return show_the_login_form()

    @app.post('/login')
    def login_post():
        return do_the_login()

Nếu ``GET`` hiện diện, Flask tự động thêm hỗ trợ cho phương thức ``HEAD``
và xử lý các request ``HEAD`` theo `HTTP RFC`_. Tương tự,
``OPTIONS`` được tự động triển khai cho bạn.

.. _HTTP RFC: https://www.ietf.org/rfc/rfc2068.txt

File Tĩnh
---------

Các ứng dụng web động cũng cần các file tĩnh. Đó thường là nơi
các file CSS và JavaScript đến từ. Lý tưởng nhất là máy chủ web của bạn được
cấu hình để phục vụ chúng cho bạn, nhưng trong quá trình phát triển Flask cũng có thể làm điều đó.
Chỉ cần tạo một thư mục có tên :file:`static` trong package của bạn hoặc bên cạnh
module của bạn và nó sẽ có sẵn tại ``/static`` trên ứng dụng.

Để tạo URL cho các file tĩnh, sử dụng tên endpoint đặc biệt ``'static'``::

    url_for('static', filename='style.css')

File phải được lưu trữ trên hệ thống tệp dưới dạng :file:`static/style.css`.

Render Template
---------------

Tạo HTML từ bên trong Python không vui chút nào, và thực sự khá
phiền toái vì bạn phải tự thực hiện việc escape HTML để giữ
cho ứng dụng an toàn. Vì lý do đó, Flask cấu hình công cụ template `Jinja
<https://palletsprojects.com/p/jinja/>`_ cho bạn một cách tự động.

Template có thể được sử dụng để tạo bất kỳ loại file văn bản nào. Đối với các ứng dụng web, bạn sẽ
chủ yếu tạo các trang HTML, nhưng bạn cũng có thể tạo markdown, văn bản thuần túy cho
email, và bất cứ thứ gì khác.

Để tham khảo về HTML, CSS, và các API web khác, hãy sử dụng `MDN Web Docs`_.

.. _MDN Web Docs: https://developer.mozilla.org/

Để render một template bạn có thể sử dụng phương thức :func:`~flask.render_template`.
Tất cả những gì bạn phải làm là cung cấp tên của template và các
biến bạn muốn truyền cho công cụ template dưới dạng đối số từ khóa.
Dưới đây là một ví dụ đơn giản về cách render một template::

    from flask import render_template

    @app.route('/hello/')
    @app.route('/hello/<name>')
    def hello(name=None):
        return render_template('hello.html', person=name)

Flask sẽ tìm kiếm các template trong thư mục :file:`templates`. Vì vậy nếu ứng dụng
của bạn là một module, thư mục này nằm cạnh module đó, nếu nó là một
package thì nó thực sự nằm bên trong package của bạn:

**Trường hợp 1**: một module::

    /application.py
    /templates
        /hello.html

**Trường hợp 2**: một package::

    /application
        /__init__.py
        /templates
            /hello.html

Đối với các template, bạn có thể sử dụng toàn bộ sức mạnh của template Jinja. Hãy truy cập
`Tài liệu Template Jinja chính thức
<https://jinja.palletsprojects.com/templates/>`_ để biết thêm thông tin.

Dưới đây là một ví dụ template:

.. sourcecode:: html+jinja

    <!doctype html>
    <title>Hello from Flask</title>
    {% if person %}
      <h1>Hello {{ person }}!</h1>
    {% else %}
      <h1>Hello, World!</h1>
    {% endif %}

Bên trong template bạn cũng có quyền truy cập vào các đối tượng :data:`~flask.Flask.config`,
:class:`~flask.request`, :class:`~flask.session` và :class:`~flask.g` [#]_
cũng như các hàm :func:`~flask.url_for` và :func:`~flask.get_flashed_messages`.

Template đặc biệt hữu ích nếu sử dụng kế thừa. Nếu bạn muốn
biết cách nó hoạt động, xem :doc:`patterns/templateinheritance`. Về cơ bản
kế thừa template giúp có thể giữ các phần tử nhất định trên mỗi
trang (như header, navigation và footer).

Tự động escape được bật, vì vậy nếu ``person`` chứa HTML nó sẽ được escape
tự động. Nếu bạn có thể tin tưởng một biến và bạn biết rằng nó sẽ là
HTML an toàn (ví dụ vì nó đến từ một module chuyển đổi wiki
markup sang HTML) bạn có thể đánh dấu nó là an toàn bằng cách sử dụng lớp
:class:`~markupsafe.Markup` hoặc bằng cách sử dụng bộ lọc ``|safe`` trong
template. Hãy truy cập tài liệu Jinja 2 để biết thêm ví dụ.

Dưới đây là giới thiệu cơ bản về cách lớp :class:`~markupsafe.Markup` hoạt động::

    >>> from markupsafe import Markup
    >>> Markup('<strong>Hello %s!</strong>') % '<blink>hacker</blink>'
    Markup('<strong>Hello &lt;blink&gt;hacker&lt;/blink&gt;!</strong>')
    >>> Markup.escape('<blink>hacker</blink>')
    Markup('&lt;blink&gt;hacker&lt;/blink&gt;')
    >>> Markup('<em>Marked up</em> &raquo; HTML').striptags()
    'Marked up » HTML'

.. versionchanged:: 0.5

   Tự động escape không còn được bật cho tất cả các template. Các phần mở rộng
   sau cho template kích hoạt tự động escape: ``.html``, ``.htm``,
   ``.xml``, ``.xhtml``. Các template được tải từ một chuỗi sẽ bị
   tắt tự động escape.

.. [#] Không chắc đối tượng :class:`~flask.g` đó là gì? Nó là thứ mà trong đó
   bạn có thể lưu trữ thông tin cho nhu cầu riêng của mình. Xem tài liệu
   cho :class:`flask.g` và :doc:`patterns/sqlite3`.


Truy cập Dữ liệu Request
------------------------

Đối với các ứng dụng web, điều quan trọng là phản ứng với dữ liệu mà client gửi đến
máy chủ. Trong Flask thông tin này được cung cấp bởi đối tượng toàn cục :data:`.request`,
là một thể hiện của :class:`.Request`. Đối tượng này có nhiều
thuộc tính và phương thức để làm việc với dữ liệu request đến, nhưng đây là một
tổng quan rộng. Đầu tiên nó cần được import.

.. code-block:: python

    from flask import request

Nếu bạn có chút kinh nghiệm với Python bạn có thể tự hỏi làm thế nào đối tượng đó
có thể là toàn cục khi Flask xử lý nhiều request cùng một lúc. Câu trả lời là
:data:`.request` thực sự là một proxy, trỏ đến bất kỳ request nào đang
được xử lý bởi một worker nhất định, được quản lý nội bộ bởi Flask
và Python. Xem :doc:`/appcontext` để biết thêm thông tin.

Phương thức request hiện tại có sẵn trong thuộc tính :attr:`~.Request.method`.
Để truy cập dữ liệu form (dữ liệu được truyền trong một request ``POST`` hoặc ``PUT``),
sử dụng thuộc tính :attr:`~flask.Request.form`, hoạt động giống như một
dict.

.. code-block:: python

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None

        if request.method == "POST":
            if valid_login(request.form["username"], request.form["password"]):
                return store_login(request.form["username"])
            else:
                error = "Invalid username or password"

        # Được thực thi nếu phương thức request là GET hoặc thông tin đăng nhập không hợp lệ.
        return render_template("login.html", error=error)

Nếu khóa không tồn tại trong ``form``, một :exc:`KeyError` đặc biệt được ném ra. Bạn
có thể bắt nó như một ``KeyError`` bình thường, nếu không nó sẽ trả về một trang lỗi HTTP 400
Bad Request. Bạn cũng có thể sử dụng phương thức
:meth:`~werkzeug.datastructures.MultiDict.get` để lấy một giá trị mặc định
thay vì lỗi.

Để truy cập các tham số được gửi trong URL (``?key=value``), sử dụng
thuộc tính :attr:`~.Request.args`. Lỗi khóa hoạt động giống như ``form``,
trả về phản hồi 400 nếu không bắt được.

.. code-block:: python

    searchword = request.args.get('key', '')

Để có danh sách đầy đủ các phương thức và thuộc tính của đối tượng request, xem tài liệu
:class:`~.Request`.


Tải lên File
````````````

Bạn có thể xử lý các file được tải lên với Flask một cách dễ dàng. Chỉ cần đảm bảo không
quên đặt thuộc tính ``enctype="multipart/form-data"`` trên form HTML
của bạn, nếu không trình duyệt sẽ không truyền file của bạn đi.

Các file được tải lên được lưu trữ trong bộ nhớ hoặc tại một vị trí tạm thời trên
hệ thống tệp. Bạn có thể truy cập các file đó bằng cách xem thuộc tính
:attr:`~flask.request.files` trên đối tượng request. Mỗi
file được tải lên được lưu trữ trong từ điển đó. Nó hoạt động giống như một
đối tượng :class:`file` Python tiêu chuẩn, nhưng nó cũng có một phương thức
:meth:`~werkzeug.datastructures.FileStorage.save` cho phép
bạn lưu file đó trên hệ thống tệp của máy chủ.
Dưới đây là một ví dụ đơn giản cho thấy cách nó hoạt động::

    from flask import request

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            f = request.files['the_file']
            f.save('/var/www/uploads/uploaded_file.txt')
        ...

Nếu bạn muốn biết file được đặt tên như thế nào trên client trước khi nó được
tải lên ứng dụng của bạn, bạn có thể truy cập thuộc tính
:attr:`~werkzeug.datastructures.FileStorage.filename`.
Tuy nhiên hãy nhớ rằng giá trị này có thể bị giả mạo
vì vậy đừng bao giờ tin tưởng giá trị đó. Nếu bạn muốn sử dụng tên file
của client để lưu file trên máy chủ, hãy chuyển nó qua hàm
:func:`~werkzeug.utils.secure_filename` mà
Werkzeug cung cấp cho bạn::

    from werkzeug.utils import secure_filename

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            file = request.files['the_file']
            file.save(f"/var/www/uploads/{secure_filename(file.filename)}")
        ...

Để có một số ví dụ tốt hơn, xem :doc:`patterns/fileuploads`.

Cookies
```````

Để truy cập cookies bạn có thể sử dụng thuộc tính :attr:`~flask.Request.cookies`.
Để đặt cookies bạn có thể sử dụng phương thức
:attr:`~flask.Response.set_cookie` của các đối tượng response. Thuộc tính
:attr:`~flask.Request.cookies` của các đối tượng request là một
từ điển với tất cả các cookies mà client truyền đi. Nếu bạn muốn sử dụng
sessions, đừng sử dụng cookies trực tiếp mà thay vào đó hãy sử dụng
:ref:`sessions` trong Flask giúp thêm một số bảo mật trên cookies cho bạn.

Đọc cookies::

    from flask import request

    @app.route('/')
    def index():
        username = request.cookies.get('username')
        # sử dụng cookies.get(key) thay vì cookies[key] để không nhận
        # KeyError nếu cookie bị thiếu.

Lưu trữ cookies::

    from flask import make_response

    @app.route('/')
    def index():
        resp = make_response(render_template(...))
        resp.set_cookie('username', 'the username')
        return resp

Lưu ý rằng cookies được đặt trên các đối tượng response. Vì bạn thường
chỉ trả về chuỗi từ các hàm view, Flask sẽ chuyển đổi chúng thành
các đối tượng response cho bạn. Nếu bạn muốn làm điều đó một cách rõ ràng, bạn có thể sử dụng
hàm :meth:`~flask.make_response` và sau đó sửa đổi nó.

Đôi khi bạn có thể muốn đặt một cookie tại một điểm mà đối tượng response
chưa tồn tại. Điều này có thể thực hiện được bằng cách sử dụng mẫu
:doc:`patterns/deferredcallbacks`.

Về điều này cũng xem :ref:`about-responses`.

Chuyển hướng và Lỗi
-------------------

Để chuyển hướng người dùng đến một endpoint khác, sử dụng hàm :func:`~flask.redirect`;
để hủy một request sớm với một mã lỗi, sử dụng hàm
:func:`~flask.abort`::

    from flask import abort, redirect, url_for

    @app.route('/')
    def index():
        return redirect(url_for('login'))

    @app.route('/login')
    def login():
        abort(401)
        this_is_never_executed()

Đây là một ví dụ khá vô nghĩa vì người dùng sẽ được chuyển hướng từ
index đến một trang mà họ không thể truy cập (401 nghĩa là truy cập bị từ chối) nhưng nó
cho thấy cách nó hoạt động.

Theo mặc định một trang lỗi đen trắng được hiển thị cho mỗi mã lỗi. Nếu
bạn muốn tùy chỉnh trang lỗi, bạn có thể sử dụng decorator
:meth:`~flask.Flask.errorhandler`::

    from flask import render_template

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('page_not_found.html'), 404

Lưu ý ``404`` sau cuộc gọi :func:`~flask.render_template`. Điều này
bảo Flask rằng mã trạng thái của trang đó nên là 404 nghĩa là
không tìm thấy. Theo mặc định 200 được giả định, dịch ra là: mọi thứ đều ổn.

Xem :doc:`errorhandling` để biết thêm chi tiết.

.. _about-responses:

Về Phản hồi (Responses)
-----------------------

Giá trị trả về từ một hàm view được tự động chuyển đổi thành
một đối tượng response cho bạn. Nếu giá trị trả về là một chuỗi nó được
chuyển đổi thành một đối tượng response với chuỗi đó làm thân phản hồi, một
mã trạng thái ``200 OK`` và một mimetype :mimetype:`text/html`. Nếu
giá trị trả về là một dict hoặc list, :func:`jsonify` được gọi để tạo ra một
phản hồi. Logic mà Flask áp dụng để chuyển đổi giá trị trả về thành
các đối tượng response như sau:

1.  Nếu một đối tượng response đúng loại được trả về, nó được trả về trực tiếp
    từ view.
2.  Nếu nó là một chuỗi, một đối tượng response được tạo với dữ liệu đó và
    các tham số mặc định.
3.  Nếu nó là một iterator hoặc generator trả về chuỗi hoặc bytes, nó được
    xử lý như một phản hồi streaming.
4.  Nếu nó là một dict hoặc list, một đối tượng response được tạo sử dụng
    :func:`~flask.json.jsonify`.
5.  Nếu một tuple được trả về, các mục trong tuple có thể cung cấp thêm
    thông tin. Các tuple như vậy phải ở dạng
    ``(response, status)``, ``(response, headers)``, hoặc
    ``(response, status, headers)``. Giá trị ``status`` sẽ ghi đè
    mã trạng thái và ``headers`` có thể là một list hoặc dictionary của
    các giá trị header bổ sung.
6.  Nếu không có cái nào hoạt động, Flask sẽ giả định giá trị trả về là một
    ứng dụng WSGI hợp lệ và chuyển đổi nó thành một đối tượng response.

Nếu bạn muốn nắm giữ đối tượng response kết quả bên trong view
bạn có thể sử dụng hàm :func:`~flask.make_response`.

Hãy tưởng tượng bạn có một view như thế này::

    from flask import render_template

    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html'), 404

Bạn chỉ cần bọc biểu thức trả về với
:func:`~flask.make_response` và lấy đối tượng response để sửa đổi nó, sau đó
trả về nó::

    from flask import make_response

    @app.errorhandler(404)
    def not_found(error):
        resp = make_response(render_template('error.html'), 404)
        resp.headers['X-Something'] = 'A value'
        return resp


API với JSON
````````````

Một định dạng phản hồi phổ biến khi viết API là JSON. Rất dễ để bắt đầu
viết một API như vậy với Flask. Nếu bạn trả về một ``dict`` hoặc
``list`` từ một view, nó sẽ được chuyển đổi thành một phản hồi JSON.

.. code-block:: python

    @app.route("/me")
    def me_api():
        user = get_current_user()
        return {
            "username": user.username,
            "theme": user.theme,
            "image": url_for("user_image", filename=user.image),
        }

    @app.route("/users")
    def users_api():
        users = get_all_users()
        return [user.to_json() for user in users]

Đây là một lối tắt để truyền dữ liệu đến hàm
:func:`~flask.json.jsonify`, hàm này sẽ tuần tự hóa bất kỳ loại dữ liệu JSON
được hỗ trợ nào. Điều đó có nghĩa là tất cả dữ liệu trong dict hoặc list phải
có thể tuần tự hóa thành JSON.

Đối với các loại phức tạp như mô hình cơ sở dữ liệu, bạn sẽ muốn sử dụng một
thư viện tuần tự hóa để chuyển đổi dữ liệu thành các loại JSON hợp lệ trước.
Có rất nhiều thư viện tuần tự hóa và tiện ích mở rộng API Flask
được duy trì bởi cộng đồng hỗ trợ các ứng dụng phức tạp hơn.


.. _sessions:

Sessions
--------

Ngoài đối tượng request còn có một đối tượng thứ hai được gọi là
:class:`~flask.session` cho phép bạn lưu trữ thông tin cụ thể cho một
người dùng từ request này sang request tiếp theo. Điều này được triển khai trên cookies
cho bạn và ký các cookies bằng mật mã. Điều này có nghĩa là
người dùng có thể xem nội dung của cookie của bạn nhưng không thể sửa đổi nó,
trừ khi họ biết khóa bí mật được sử dụng để ký.

Để sử dụng sessions bạn phải đặt một khóa bí mật. Dưới đây là cách
sessions hoạt động::

    from flask import session

    # Đặt khóa bí mật thành một số byte ngẫu nhiên. Giữ cái này thực sự bí mật!
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

    @app.route('/')
    def index():
        if 'username' in session:
            return f'Logged in as {session["username"]}'
        return 'You are not logged in'

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        return '''
            <form method="post">
                <p><input type=text name=username>
                <p><input type=submit value=Login>
            </form>
        '''

    @app.route('/logout')
    def logout():
        # xóa username khỏi session nếu nó ở đó
        session.pop('username', None)
        return redirect(url_for('index'))

.. admonition:: Cách tạo khóa bí mật tốt

    Một khóa bí mật nên ngẫu nhiên nhất có thể. Hệ điều hành của bạn có
    các cách để tạo dữ liệu khá ngẫu nhiên dựa trên một trình tạo ngẫu nhiên
    mật mã. Sử dụng lệnh sau để nhanh chóng tạo một giá trị cho
    :attr:`Flask.secret_key` (hoặc :data:`SECRET_KEY`)::

        $ python -c 'import secrets; print(secrets.token_hex())'
        '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'

Một lưu ý về sessions dựa trên cookie: Flask sẽ lấy các giá trị bạn đặt vào
đối tượng session và tuần tự hóa chúng thành một cookie. Nếu bạn thấy một số
giá trị không tồn tại qua các request, cookies thực sự đã được bật, và bạn
không nhận được thông báo lỗi rõ ràng, hãy kiểm tra kích thước của cookie trong
phản hồi trang của bạn so với kích thước được hỗ trợ bởi trình duyệt web.

Ngoài các sessions dựa trên phía client mặc định, nếu bạn muốn xử lý
sessions ở phía máy chủ thay vào đó, có một số
tiện ích mở rộng Flask hỗ trợ điều này.

Message Flashing
----------------

Các ứng dụng và giao diện người dùng tốt đều là về phản hồi. Nếu người dùng
không nhận được đủ phản hồi họ có thể sẽ ghét
ứng dụng. Flask cung cấp một cách thực sự đơn giản để đưa ra phản hồi cho một
người dùng với hệ thống flashing. Hệ thống flashing về cơ bản làm cho nó
có thể ghi lại một tin nhắn ở cuối một request và truy cập nó vào request tiếp theo
(và chỉ request tiếp theo). Điều này thường được kết hợp với một layout
template để hiển thị tin nhắn.

Để flash một tin nhắn sử dụng phương thức :func:`~flask.flash`, để nắm giữ các
tin nhắn bạn có thể sử dụng :func:`~flask.get_flashed_messages` cũng
có sẵn trong các template. Xem :doc:`patterns/flashing` để có một ví dụ
đầy đủ.

Ghi log (Logging)
-----------------

.. versionadded:: 0.3

Đôi khi bạn có thể ở trong tình huống phải xử lý dữ liệu mà
lẽ ra phải đúng, nhưng thực tế lại không. Ví dụ bạn có thể có
một số mã phía client gửi một request HTTP đến máy chủ
nhưng nó rõ ràng bị định dạng sai. Điều này có thể do người dùng can thiệp
vào dữ liệu, hoặc mã client bị lỗi. Hầu hết thời gian là ổn
để trả lời với ``400 Bad Request`` trong tình huống đó, nhưng đôi khi
điều đó sẽ không được và mã phải tiếp tục hoạt động.

Bạn vẫn có thể muốn ghi log rằng có điều gì đó đáng ngờ đã xảy ra. Đây là nơi
các logger trở nên hữu ích. Kể từ Flask 0.3 một logger được cấu hình sẵn cho bạn
để sử dụng.

Dưới đây là một số ví dụ gọi log::

    app.logger.debug('A value for debugging')
    app.logger.warning('A warning occurred (%d apples)', 42)
    app.logger.error('An error occurred')

:attr:`~flask.Flask.logger` đính kèm là một :class:`~logging.Logger`
logging tiêu chuẩn, vì vậy hãy truy cập tài liệu :mod:`logging` chính thức
để biết thêm thông tin.

Xem :doc:`errorhandling`.


Hooking vào WSGI Middleware
---------------------------

Để thêm WSGI middleware vào ứng dụng Flask của bạn, hãy bọc thuộc tính
``wsgi_app`` của ứng dụng. Ví dụ, để áp dụng middleware
:class:`~werkzeug.middleware.proxy_fix.ProxyFix` của Werkzeug để chạy
phía sau Nginx:

.. code-block:: python

    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)

Bọc ``app.wsgi_app`` thay vì ``app`` có nghĩa là ``app`` vẫn
trỏ vào ứng dụng Flask của bạn, không phải vào middleware, vì vậy bạn có thể
tiếp tục sử dụng và cấu hình ``app`` trực tiếp.

Sử dụng Tiện ích mở rộng Flask
------------------------------

Các tiện ích mở rộng là các gói giúp bạn hoàn thành các tác vụ phổ biến. Ví dụ,
Flask-SQLAlchemy cung cấp hỗ trợ SQLAlchemy giúp nó đơn giản
và dễ sử dụng với Flask.

Để biết thêm về các tiện ích mở rộng Flask, xem :doc:`extensions`.

Triển khai lên Máy chủ Web
--------------------------

Sẵn sàng triển khai ứng dụng Flask mới của bạn? Xem :doc:`deploying/index`.
