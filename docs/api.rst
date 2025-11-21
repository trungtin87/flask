API
===

.. module:: flask

Phần này của tài liệu bao gồm tất cả các giao diện của Flask. Đối với
các phần mà Flask phụ thuộc vào các thư viện bên ngoài, chúng tôi ghi lại những phần quan trọng nhất
ngay tại đây và cung cấp liên kết đến tài liệu chính thức.


Đối tượng Ứng dụng (Application Object)
---------------------------------------

.. autoclass:: Flask
   :members:
   :inherited-members:


Đối tượng Blueprint
-------------------

.. autoclass:: Blueprint
   :members:
   :inherited-members:

Dữ liệu Request Đến
-------------------

.. autoclass:: Request
    :members:
    :inherited-members:
    :exclude-members: json_module

.. data:: request

    Một proxy đến dữ liệu request cho request hiện tại, một thể hiện của
    :class:`.Request`.

    Cái này chỉ khả dụng khi một :doc:`request context </appcontext>` đang
    hoạt động.

    Đây là một proxy. Xem :ref:`context-visibility` để biết thêm thông tin.


Đối tượng Phản hồi (Response Objects)
-------------------------------------

.. autoclass:: flask.Response
    :members:
    :inherited-members:
    :exclude-members: json_module

Sessions
--------

Nếu bạn đã đặt :attr:`Flask.secret_key` (hoặc cấu hình nó từ
:data:`SECRET_KEY`) bạn có thể sử dụng sessions trong các ứng dụng Flask. Một session làm cho
nó có thể ghi nhớ thông tin từ request này sang request khác. Cách Flask
làm điều này là bằng cách sử dụng một cookie đã ký. Người dùng có thể xem nội dung
session, nhưng không thể sửa đổi nó trừ khi họ biết khóa bí mật, vì vậy hãy chắc chắn
đặt nó thành một cái gì đó phức tạp và không thể đoán được.

Để truy cập session hiện tại bạn có thể sử dụng proxy :data:`.session`.

.. data:: session

    Một proxy đến dữ liệu session cho request hiện tại, một thể hiện của
    :class:`.SessionMixin`.

    Cái này chỉ khả dụng khi một :doc:`request context </appcontext>` đang
    hoạt động.

    Đây là một proxy. Xem :ref:`context-visibility` để biết thêm thông tin.

    Đối tượng session hoạt động giống như một dict nhưng theo dõi việc gán và truy cập vào các
    khóa của nó. Nó không thể theo dõi các sửa đổi đối với các giá trị có thể thay đổi, bạn cần đặt
    :attr:`~.SessionMixin.modified` thủ công khi sửa đổi một list, dict, v.v.

    .. code-block:: python

          # thêm vào một danh sách không được phát hiện
          session["numbers"].append(42)
          # vì vậy hãy đánh dấu nó là đã sửa đổi
          session.modified = True

    Session được duy trì qua các request bằng cách sử dụng một cookie. Theo mặc định
    trình duyệt của người dùng sẽ xóa cookie khi nó bị đóng. Đặt
    :attr:`~.SessionMixin.permanent` thành ``True`` để duy trì cookie trong
    :data:`PERMANENT_SESSION_LIFETIME`.


Giao diện Session
-----------------

.. versionadded:: 0.8

Giao diện session cung cấp một cách đơn giản để thay thế triển khai
session mà Flask đang sử dụng.

.. currentmodule:: flask.sessions

.. autoclass:: SessionInterface
   :members:

.. autoclass:: SecureCookieSessionInterface
   :members:

.. autoclass:: SecureCookieSession
   :members:

.. autoclass:: NullSession
   :members:

.. autoclass:: SessionMixin
   :members:

.. admonition:: Lưu ý

    Cấu hình :data:`PERMANENT_SESSION_LIFETIME` có thể là một số nguyên hoặc ``timedelta``.
    Thuộc tính :attr:`~flask.Flask.permanent_session_lifetime` luôn là một
    ``timedelta``.


Test Client
-----------

.. currentmodule:: flask.testing

.. autoclass:: FlaskClient
   :members:


Test CLI Runner
---------------

.. currentmodule:: flask.testing

.. autoclass:: FlaskCliRunner
    :members:


Toàn cục Ứng dụng (Application Globals)
---------------------------------------

.. currentmodule:: flask

Để chia sẻ dữ liệu chỉ hợp lệ cho một request từ một hàm sang
hàm khác, một biến toàn cục là không đủ tốt vì nó sẽ bị hỏng trong
các môi trường đa luồng. Flask cung cấp cho bạn một đối tượng đặc biệt
đảm bảo nó chỉ hợp lệ cho request đang hoạt động và sẽ trả về
các giá trị khác nhau cho mỗi request. Tóm lại: nó làm đúng
việc, giống như nó làm cho :data:`.request` và :data:`.session`.

.. data:: g

    Một proxy đến một đối tượng namespace được sử dụng để lưu trữ dữ liệu trong một request đơn lẻ hoặc
    app context. Một thể hiện của :attr:`.Flask.app_ctx_globals_class`, mặc định
    là :class:`._AppCtxGlobals`.

    Đây là một nơi tốt để lưu trữ tài nguyên trong một request. Ví dụ, một
    hàm :meth:`~.Flask.before_request` có thể tải một đối tượng người dùng từ một
    session id, sau đó đặt ``g.user`` để được sử dụng trong hàm view.

    Cái này chỉ khả dụng khi một :doc:`app context </appcontext>` đang hoạt động.

    Đây là một proxy. Xem :ref:`context-visibility` để biết thêm thông tin.

    .. versionchanged:: 0.10
        Gắn với application context thay vì request context.

.. autoclass:: flask.ctx._AppCtxGlobals
    :members:


Các Hàm và Lớp Hữu ích
----------------------

.. data:: current_app

    Một proxy đến ứng dụng :class:`.Flask` đang xử lý request hiện tại hoặc
    hoạt động khác.

    Điều này hữu ích để truy cập ứng dụng mà không cần import nó, hoặc nếu
    nó không thể được import, chẳng hạn như khi sử dụng mẫu application factory hoặc
    trong blueprints và extensions.

    Cái này chỉ khả dụng khi một :doc:`app context </appcontext>` đang hoạt động.

    Đây là một proxy. Xem :ref:`context-visibility` để biết thêm thông tin.

.. autofunction:: has_request_context

.. autofunction:: copy_current_request_context

.. autofunction:: has_app_context

.. autofunction:: url_for

.. autofunction:: abort

.. autofunction:: redirect

.. autofunction:: make_response

.. autofunction:: after_this_request

.. autofunction:: send_file

.. autofunction:: send_from_directory


Message Flashing
----------------

.. autofunction:: flash

.. autofunction:: get_flashed_messages


Hỗ trợ JSON
-----------

.. module:: flask.json

Flask sử dụng module :mod:`json` tích hợp của Python để xử lý JSON theo
mặc định. Việc triển khai JSON có thể được thay đổi bằng cách gán một
nhà cung cấp khác cho :attr:`flask.Flask.json_provider_class` hoặc
:attr:`flask.Flask.json`. Các hàm được cung cấp bởi ``flask.json`` sẽ
sử dụng các phương thức trên ``app.json`` nếu một app context đang hoạt động.

Bộ lọc ``|tojson`` của Jinja được cấu hình để sử dụng nhà cung cấp JSON của ứng dụng.
Bộ lọc đánh dấu đầu ra với ``|safe``. Sử dụng nó để render dữ liệu bên trong
thẻ HTML ``<script>``.

.. sourcecode:: html+jinja

    <script>
        const names = {{ names|tojson }};
        renderChart(names, {{ axis_data|tojson }});
    </script>

.. autofunction:: jsonify

.. autofunction:: dumps

.. autofunction:: dump

.. autofunction:: loads

.. autofunction:: load

.. autoclass:: flask.json.provider.JSONProvider
    :members:
    :member-order: bysource

.. autoclass:: flask.json.provider.DefaultJSONProvider
    :members:
    :member-order: bysource

.. automodule:: flask.json.tag


Render Template
---------------

.. currentmodule:: flask

.. autofunction:: render_template

.. autofunction:: render_template_string

.. autofunction:: stream_template

.. autofunction:: stream_template_string

.. autofunction:: get_template_attribute

Cấu hình
--------

.. autoclass:: Config
   :members:


Stream Helpers
--------------

.. autofunction:: stream_with_context

Các Nội bộ Hữu ích
------------------

.. autoclass:: flask.ctx.AppContext
   :members:

.. data:: flask.globals.app_ctx

    Một proxy đến :class:`.AppContext` đang hoạt động.

    Đây là một đối tượng nội bộ cần thiết cho cách Flask xử lý các request.
    Truy cập cái này không cần thiết trong hầu hết các trường hợp. Rất có thể bạn muốn
    :data:`.current_app`, :data:`.g`, :data:`.request`, và :data:`.session` thay vào đó.

    Cái này chỉ khả dụng khi một :doc:`request context </appcontext>` đang
    hoạt động.

    Đây là một proxy. Xem :ref:`context-visibility` để biết thêm thông tin.

.. class:: flask.ctx.RequestContext

    .. deprecated:: 3.2
        Hợp nhất với :class:`AppContext`. Alias này sẽ bị xóa trong Flask 4.0.

.. data:: flask.globals.request_ctx

    .. deprecated:: 3.2
        Hợp nhất với :data:`.app_ctx`. Alias này sẽ bị xóa trong Flask 4.0.

.. autoclass:: flask.blueprints.BlueprintSetupState
   :members:

.. _core-signals-list:

Signals
-------

Signals được cung cấp bởi thư viện `Blinker`_. Xem :doc:`signals` để biết giới thiệu.

.. _blinker: https://blinker.readthedocs.io/

.. data:: template_rendered

   Signal này được gửi khi một template đã được render thành công.
   Signal được gọi với thể hiện của template là `template`
   và context là dictionary (tên là `context`).

   Ví dụ subscriber::

        def log_template_renders(sender, template, context, **extra):
            sender.logger.debug('Rendering template "%s" with context %s',
                                template.name or 'string template',
                                context)

        from flask import template_rendered
        template_rendered.connect(log_template_renders, app)

.. data:: flask.before_render_template
   :noindex:

   Signal này được gửi trước quá trình render template.
   Signal được gọi với thể hiện của template là `template`
   và context là dictionary (tên là `context`).

   Ví dụ subscriber::

        def log_template_renders(sender, template, context, **extra):
            sender.logger.debug('Rendering template "%s" with context %s',
                                template.name or 'string template',
                                context)

        from flask import before_render_template
        before_render_template.connect(log_template_renders, app)

.. data:: request_started

   Signal này được gửi khi request context được thiết lập, trước khi
   bất kỳ xử lý request nào xảy ra. Bởi vì request context đã được
   ràng buộc, subscriber có thể truy cập request với các proxy toàn cục
   tiêu chuẩn như :class:`~flask.request`.

   Ví dụ subscriber::

        def log_request(sender, **extra):
            sender.logger.debug('Request context is set up')

        from flask import request_started
        request_started.connect(log_request, app)

.. data:: request_finished

   Signal này được gửi ngay trước khi phản hồi được gửi đến client.
   Nó được truyền phản hồi sẽ được gửi có tên là `response`.

   Ví dụ subscriber::

        def log_response(sender, response, **extra):
            sender.logger.debug('Request context is about to close down. '
                                'Response: %s', response)

        from flask import request_finished
        request_finished.connect(log_response, app)

.. data:: got_request_exception

    Signal này được gửi khi một ngoại lệ không được xử lý xảy ra trong quá trình
    xử lý request, bao gồm cả khi debugging. Ngoại lệ được
    truyền cho subscriber dưới dạng ``exception``.

    Signal này không được gửi cho
    :exc:`~werkzeug.exceptions.HTTPException`, hoặc các ngoại lệ khác mà
    có trình xử lý lỗi đã đăng ký, trừ khi ngoại lệ được ném ra từ
    một trình xử lý lỗi.

    Ví dụ này cho thấy cách thực hiện một số ghi log bổ sung nếu một
    ``SecurityException`` lý thuyết được ném ra:

    .. code-block:: python

        from flask import got_request_exception

        def log_security_exception(sender, exception, **extra):
            if not isinstance(exception, SecurityException):
                return

            security_logger.exception(
                f"SecurityException at {request.url!r}",
                exc_info=exception,
            )

        got_request_exception.connect(log_security_exception, app)

.. data:: request_tearing_down

   Signal này được gửi khi request đang bị hủy. Cái này luôn được
   gọi, ngay cả khi một ngoại lệ được gây ra. Hiện tại các hàm lắng nghe
   signal này được gọi sau các trình xử lý teardown thông thường, nhưng điều này
   không phải là thứ bạn có thể dựa vào.

   Ví dụ subscriber::

        def close_db_connection(sender, **extra):
            session.close()

        from flask import request_tearing_down
        request_tearing_down.connect(close_db_connection, app)

   Kể từ Flask 0.9, cái này cũng sẽ được truyền một đối số từ khóa `exc`
   có tham chiếu đến ngoại lệ đã gây ra teardown nếu
   có một cái.

.. data:: appcontext_tearing_down

   Signal này được gửi khi app context đang bị hủy. Cái này luôn được
   gọi, ngay cả khi một ngoại lệ được gây ra. Hiện tại các hàm lắng nghe
   signal này được gọi sau các trình xử lý teardown thông thường, nhưng điều này
   không phải là thứ bạn có thể dựa vào.

   Ví dụ subscriber::

        def close_db_connection(sender, **extra):
            session.close()

        from flask import appcontext_tearing_down
        appcontext_tearing_down.connect(close_db_connection, app)

   Cái này cũng sẽ được truyền một đối số từ khóa `exc` có tham chiếu
   đến ngoại lệ đã gây ra teardown nếu có một cái.

.. data:: appcontext_pushed

   Signal này được gửi khi một application context được đẩy (pushed). Người gửi
   là ứng dụng. Điều này thường hữu ích cho unittests để
   tạm thời móc nối thông tin vào. Ví dụ nó có thể được sử dụng để
   đặt một tài nguyên sớm vào đối tượng `g`.

   Ví dụ sử dụng::

        from contextlib import contextmanager
        from flask import appcontext_pushed

        @contextmanager
        def user_set(app, user):
            def handler(sender, **kwargs):
                g.user = user
            with appcontext_pushed.connected_to(handler, app):
                yield

   Và trong mã test::

        def test_user_me(self):
            with user_set(app, 'john'):
                c = app.test_client()
                resp = c.get('/users/me')
                assert resp.data == 'username=john'

   .. versionadded:: 0.10

.. data:: appcontext_popped

   Signal này được gửi khi một application context bị pop. Người gửi
   là ứng dụng. Điều này thường đi đôi với
   signal :data:`appcontext_tearing_down`.

   .. versionadded:: 0.10

.. data:: message_flashed

   Signal này được gửi khi ứng dụng đang flash một tin nhắn. Các
   tin nhắn được gửi dưới dạng đối số từ khóa `message` và danh mục dưới dạng
   `category`.

   Ví dụ subscriber::

        recorded = []
        def record(sender, message, category, **extra):
            recorded.append((message, category))

        from flask import message_flashed
        message_flashed.connect(record, app)

   .. versionadded:: 0.10


Class-Based Views
-----------------

.. versionadded:: 0.7

.. currentmodule:: None

.. autoclass:: flask.views.View
   :members:

.. autoclass:: flask.views.MethodView
   :members:

.. _url-route-registrations:

Đăng ký Route URL
-----------------

Nói chung có ba cách để định nghĩa các quy tắc cho hệ thống định tuyến:

1.  Bạn có thể sử dụng decorator :meth:`flask.Flask.route`.
2.  Bạn có thể sử dụng hàm :meth:`flask.Flask.add_url_rule`.
3.  Bạn có thể truy cập trực tiếp hệ thống định tuyến Werkzeug cơ bản
    được hiển thị dưới dạng :attr:`flask.Flask.url_map`.

Các phần biến trong route có thể được chỉ định bằng dấu ngoặc nhọn
(``/user/<username>``). Theo mặc định một phần biến trong URL chấp nhận bất kỳ
chuỗi nào không có dấu gạch chéo tuy nhiên một bộ chuyển đổi khác có thể được chỉ định
bằng cách sử dụng ``<converter:name>``.

Các phần biến được truyền cho hàm view dưới dạng đối số từ khóa.

Các bộ chuyển đổi sau có sẵn:

=========== ===============================================
`string`    chấp nhận bất kỳ văn bản nào không có dấu gạch chéo (mặc định)
`int`       chấp nhận số nguyên
`float`     giống như `int` nhưng cho các giá trị dấu phẩy động
`path`      giống như mặc định nhưng cũng chấp nhận dấu gạch chéo
`any`       khớp với một trong các mục được cung cấp
`uuid`      chấp nhận chuỗi UUID
=========== ===============================================

Các bộ chuyển đổi tùy chỉnh có thể được định nghĩa bằng cách sử dụng :attr:`flask.Flask.url_map`.

Dưới đây là một số ví dụ::

    @app.route('/')
    def index():
        pass

    @app.route('/<username>')
    def show_user(username):
        pass

    @app.route('/post/<int:post_id>')
    def show_post(post_id):
        pass

Một chi tiết quan trọng cần ghi nhớ là cách Flask xử lý các dấu gạch chéo
ở cuối. Ý tưởng là giữ cho mỗi URL là duy nhất vì vậy các quy tắc sau
được áp dụng:

1. Nếu một quy tắc kết thúc bằng một dấu gạch chéo và được yêu cầu không có dấu gạch chéo bởi
   người dùng, người dùng sẽ tự động được chuyển hướng đến cùng một trang với
   dấu gạch chéo ở cuối được đính kèm.
2. Nếu một quy tắc không kết thúc bằng một dấu gạch chéo ở cuối và người dùng yêu cầu
   trang với một dấu gạch chéo ở cuối, một lỗi 404 not found được ném ra.

Điều này nhất quán với cách các máy chủ web xử lý các file tĩnh. Điều này
cũng giúp có thể sử dụng các mục tiêu liên kết tương đối một cách an toàn.

Bạn cũng có thể định nghĩa nhiều quy tắc cho cùng một hàm. Tuy nhiên chúng phải
duy nhất. Các giá trị mặc định cũng có thể được chỉ định. Ví dụ dưới đây là một
định nghĩa cho một URL chấp nhận một trang tùy chọn::

    @app.route('/users/', defaults={'page': 1})
    @app.route('/users/page/<int:page>')
    def show_users(page):
        pass

Điều này chỉ định rằng ``/users/`` sẽ là URL cho trang một và
``/users/page/N`` sẽ là URL cho trang ``N``.

Nếu một URL chứa một giá trị mặc định, nó sẽ được chuyển hướng đến dạng đơn giản hơn
của nó với một chuyển hướng 301. Trong ví dụ trên, ``/users/page/1`` sẽ
được chuyển hướng đến ``/users/``. Nếu route của bạn xử lý các request ``GET`` và ``POST``,
hãy đảm bảo route mặc định chỉ xử lý ``GET``, vì các chuyển hướng
không thể bảo toàn dữ liệu form. ::

   @app.route('/region/', defaults={'id': 1})
   @app.route('/region/<int:id>', methods=['GET', 'POST'])
   def region(id):
      pass

Dưới đây là các tham số mà :meth:`~flask.Flask.route` và
:meth:`~flask.Flask.add_url_rule` chấp nhận. Sự khác biệt duy nhất là
với tham số route, hàm view được định nghĩa với decorator
thay vì tham số `view_func`.

=============== ==========================================================
`rule`          quy tắc URL dưới dạng chuỗi
`endpoint`      endpoint cho quy tắc URL đã đăng ký. Bản thân Flask
                giả định rằng tên của hàm view là tên
                của endpoint nếu không được nêu rõ ràng.
`view_func`     hàm để gọi khi phục vụ một request đến
                endpoint được cung cấp. Nếu cái này không được cung cấp người ta có thể
                chỉ định hàm sau đó bằng cách lưu trữ nó trong
                từ điển :attr:`~flask.Flask.view_functions` với
                endpoint làm khóa.
`defaults`      Một từ điển với các giá trị mặc định cho quy tắc này. Xem
                ví dụ trên để biết cách các giá trị mặc định hoạt động.
`subdomain`     chỉ định quy tắc cho subdomain trong trường hợp khớp
                subdomain đang được sử dụng. Nếu không được chỉ định
                subdomain mặc định được giả định.
`**options`     các tùy chọn được chuyển tiếp đến đối tượng
                :class:`~werkzeug.routing.Rule` cơ bản. Một thay đổi đối với
                Werkzeug là xử lý các tùy chọn phương thức. methods là một danh sách
                các phương thức mà quy tắc này nên được giới hạn (``GET``, ``POST``
                v.v.). Theo mặc định một quy tắc chỉ lắng nghe ``GET`` (và
                ngầm định ``HEAD``). Bắt đầu với Flask 0.6, ``OPTIONS`` được
                thêm ngầm định và xử lý bởi xử lý request
                tiêu chuẩn. Chúng phải được chỉ định dưới dạng đối số từ khóa.
=============== ==========================================================


Tùy chọn Hàm View
-----------------

Đối với việc sử dụng nội bộ, các hàm view có thể có một số thuộc tính được đính kèm để
tùy chỉnh hành vi mà hàm view thường không có quyền kiểm soát.
Các thuộc tính sau có thể được cung cấp tùy chọn để ghi đè
một số mặc định cho :meth:`~flask.Flask.add_url_rule` hoặc hành vi chung:

-   `__name__`: Tên của một hàm theo mặc định được sử dụng làm endpoint. Nếu
    endpoint được cung cấp rõ ràng giá trị này được sử dụng. Ngoài ra cái này
    sẽ được thêm tiền tố với tên của blueprint theo mặc định mà
    không thể tùy chỉnh từ chính hàm đó.

-   `methods`: Nếu methods không được cung cấp khi quy tắc URL được thêm vào,
    Flask sẽ tìm trên chính đối tượng hàm view xem có thuộc tính `methods`
    tồn tại hay không. Nếu có, nó sẽ lấy thông tin cho các
    phương thức từ đó.

-   `provide_automatic_options`: nếu thuộc tính này được đặt Flask sẽ
    buộc bật hoặc tắt việc triển khai tự động của
    phản hồi HTTP ``OPTIONS``. Điều này có thể hữu ích khi làm việc với
    các decorator muốn tùy chỉnh phản hồi ``OPTIONS`` trên cơ sở từng view.

-   `required_methods`: nếu thuộc tính này được đặt, Flask sẽ luôn thêm
    các phương thức này khi đăng ký một quy tắc URL ngay cả khi các phương thức đã được
    ghi đè rõ ràng trong cuộc gọi ``route()``.

Ví dụ đầy đủ::

    def index():
        if request.method == 'OPTIONS':
            # xử lý tùy chọn tùy chỉnh ở đây
            ...
        return 'Hello World!'
    index.provide_automatic_options = False
    index.methods = ['GET', 'OPTIONS']

    app.add_url_rule('/', index)

.. versionadded:: 0.8
   Chức năng `provide_automatic_options` đã được thêm vào.

Giao diện Dòng lệnh (Command Line Interface)
--------------------------------------------

.. currentmodule:: flask.cli

.. autoclass:: FlaskGroup
   :members:

.. autoclass:: AppGroup
   :members:

.. autoclass:: ScriptInfo
   :members:

.. autofunction:: load_dotenv

.. autofunction:: with_appcontext

.. autofunction:: pass_script_info

   Đánh dấu một hàm để một thể hiện của :class:`ScriptInfo` được truyền
   làm đối số đầu tiên cho callback click.

.. autodata:: run_command

.. autodata:: shell_command
