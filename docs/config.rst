Xử lý Cấu hình
================

Các ứng dụng cần một loại cấu hình nào đó. Có các cài đặt khác nhau
bạn có thể muốn thay đổi tùy thuộc vào môi trường ứng dụng như
bật tắt chế độ debug, đặt khóa bí mật, và các thứ
cụ thể theo môi trường khác.

Cách Flask được thiết kế thường yêu cầu cấu hình phải
có sẵn khi ứng dụng khởi động. Bạn có thể mã hóa cứng
cấu hình trong mã, điều này đối với nhiều ứng dụng nhỏ không
thực sự tệ lắm, nhưng có những cách tốt hơn.

Độc lập với cách bạn tải cấu hình của mình, có một đối tượng config
có sẵn giữ các giá trị cấu hình đã tải:
Thuộc tính :attr:`~flask.Flask.config` của đối tượng :class:`~flask.Flask`.
Đây là nơi Flask tự đặt các giá trị cấu hình nhất định
và cũng là nơi các tiện ích mở rộng có thể đặt các giá trị cấu hình của chúng. Nhưng
đây cũng là nơi bạn có thể có cấu hình riêng của mình.


Cơ bản về Cấu hình
------------------

:attr:`~flask.Flask.config` thực sự là một lớp con của từ điển (dictionary) và
có thể được sửa đổi giống như bất kỳ từ điển nào::

    app = Flask(__name__)
    app.config['TESTING'] = True

Các giá trị cấu hình nhất định cũng được chuyển tiếp đến
đối tượng :attr:`~flask.Flask` để bạn có thể đọc và ghi chúng từ đó::

    app.testing = True

Để cập nhật nhiều khóa cùng một lúc bạn có thể sử dụng phương thức :meth:`dict.update`::

    app.config.update(
        TESTING=True,
        SECRET_KEY='192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
    )


Chế độ Debug
------------

Giá trị cấu hình :data:`DEBUG` là đặc biệt bởi vì nó có thể hoạt động không nhất quán nếu
thay đổi sau khi ứng dụng đã bắt đầu thiết lập. Để đặt chế độ debug một cách đáng tin cậy, sử dụng
tùy chọn ``--debug`` trên lệnh ``flask`` hoặc ``flask run``. ``flask run`` sẽ sử dụng
trình gỡ lỗi tương tác và trình tải lại theo mặc định trong chế độ debug.

.. code-block:: text

    $ flask --app hello run --debug

Sử dụng tùy chọn này được khuyến nghị. Mặc dù có thể đặt :data:`DEBUG` trong
cấu hình hoặc mã của bạn, điều này không được khuyến khích. Nó không thể được đọc sớm bởi
lệnh ``flask run``, và một số hệ thống hoặc tiện ích mở rộng có thể đã tự cấu hình
dựa trên giá trị trước đó.


Các Giá trị Cấu hình Tích hợp
-----------------------------

Các giá trị cấu hình sau được sử dụng nội bộ bởi Flask:

.. py:data:: DEBUG

    Liệu chế độ debug có được bật hay không. Khi sử dụng ``flask run`` để khởi động máy chủ phát triển,
    một trình gỡ lỗi tương tác sẽ được hiển thị cho các ngoại lệ không được xử lý, và
    máy chủ sẽ được tải lại khi mã thay đổi. Thuộc tính :attr:`~flask.Flask.debug`
    ánh xạ tới khóa cấu hình này. Điều này được đặt bằng biến môi trường ``FLASK_DEBUG``.
    Nó có thể không hoạt động như mong đợi nếu được đặt trong mã.

    **Không bật chế độ debug khi triển khai trong sản xuất.**

    Mặc định: ``False``

.. py:data:: TESTING

    Bật chế độ kiểm thử (testing). Các ngoại lệ được lan truyền thay vì được xử lý bởi
    các trình xử lý lỗi của ứng dụng. Các tiện ích mở rộng cũng có thể thay đổi hành vi của chúng để
    tạo điều kiện kiểm thử dễ dàng hơn. Bạn nên bật cái này trong các bài kiểm thử của riêng bạn.

    Mặc định: ``False``

.. py:data:: PROPAGATE_EXCEPTIONS

    Các ngoại lệ được ném lại thay vì được xử lý bởi các trình xử lý lỗi của
    ứng dụng. Nếu không được đặt, cái này ngầm định là đúng nếu ``TESTING`` hoặc ``DEBUG``
    được bật.

    Mặc định: ``None``

.. py:data:: TRAP_HTTP_EXCEPTIONS

    Nếu không có trình xử lý cho một ngoại lệ loại ``HTTPException``, ném lại nó
    để được xử lý bởi trình gỡ lỗi tương tác thay vì trả về nó như một
    phản hồi lỗi đơn giản.

    Mặc định: ``False``

.. py:data:: TRAP_BAD_REQUEST_ERRORS

    Cố gắng truy cập một khóa không tồn tại từ các dict request như ``args``
    và ``form`` sẽ trả về một trang lỗi 400 Bad Request. Bật cái này để coi
    lỗi như một ngoại lệ không được xử lý thay vào đó để bạn nhận được trình gỡ lỗi
    tương tác. Đây là một phiên bản cụ thể hơn của ``TRAP_HTTP_EXCEPTIONS``. Nếu
    không được đặt, nó được bật trong chế độ debug.

    Mặc định: ``None``

.. py:data:: SECRET_KEY

    Một khóa bí mật sẽ được sử dụng để ký cookie session một cách an toàn
    và có thể được sử dụng cho bất kỳ nhu cầu liên quan đến bảo mật nào khác bởi các tiện ích mở rộng hoặc
    ứng dụng của bạn. Nó nên là một ``bytes`` hoặc ``str`` ngẫu nhiên dài. Ví dụ,
    sao chép đầu ra của cái này vào cấu hình của bạn::

        $ python -c 'import secrets; print(secrets.token_hex())'
        '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'

    **Không tiết lộ khóa bí mật khi đăng câu hỏi hoặc commit mã.**

    Mặc định: ``None``

.. py:data:: SECRET_KEY_FALLBACKS

    Một danh sách các khóa bí mật cũ vẫn có thể được sử dụng để hủy ký (unsigning). Điều này cho phép
    một dự án thực hiện xoay vòng khóa mà không làm mất hiệu lực các session đang hoạt động hoặc
    các bí mật được ký gần đây khác.

    Các khóa nên được xóa sau một khoảng thời gian thích hợp, vì kiểm tra mỗi
    khóa bổ sung thêm một chút chi phí.

    Thứ tự không quan trọng, nhưng việc triển khai mặc định sẽ kiểm tra khóa cuối cùng
    trong danh sách trước, vì vậy có thể hợp lý khi sắp xếp từ cũ nhất đến mới nhất.

    Session cookie an toàn tích hợp của Flask hỗ trợ điều này. Các tiện ích mở rộng sử dụng
    :data:`SECRET_KEY` có thể chưa hỗ trợ điều này.

    Mặc định: ``None``

    .. versionadded:: 3.1

.. py:data:: SESSION_COOKIE_NAME

    Tên của cookie session. Có thể thay đổi trong trường hợp bạn đã có một
    cookie với cùng tên.

    Mặc định: ``'session'``

.. py:data:: SESSION_COOKIE_DOMAIN

    Giá trị của tham số ``Domain`` trên cookie session. Nếu không được đặt, các trình duyệt
    sẽ chỉ gửi cookie đến tên miền chính xác mà nó được đặt từ đó. Ngược lại, chúng
    sẽ gửi nó đến bất kỳ tên miền phụ nào của giá trị đã cho.

    Không đặt giá trị này hạn chế và an toàn hơn là đặt nó.

    Mặc định: ``None``

    .. warning::
        Nếu cái này bị thay đổi sau khi trình duyệt tạo một cookie được tạo với
        một cài đặt, nó có thể dẫn đến một cái khác được tạo ra. Các trình duyệt có thể gửi
        cả hai theo một thứ tự không xác định. Trong trường hợp đó, bạn có thể muốn thay đổi
        :data:`SESSION_COOKIE_NAME` cũng như hoặc nếu không thì làm mất hiệu lực các session cũ.

    .. versionchanged:: 2.3
        Không được đặt theo mặc định, không quay lại ``SERVER_NAME``.

.. py:data:: SESSION_COOKIE_PATH

    Đường dẫn mà cookie session sẽ hợp lệ. Nếu không được đặt, cookie
    sẽ hợp lệ bên dưới ``APPLICATION_ROOT`` hoặc ``/`` nếu cái đó không được đặt.

    Mặc định: ``None``

.. py:data:: SESSION_COOKIE_HTTPONLY

    Các trình duyệt sẽ không cho phép JavaScript truy cập vào các cookie được đánh dấu là "HTTP only"
    để bảo mật.

    Mặc định: ``True``

.. py:data:: SESSION_COOKIE_SECURE

    Các trình duyệt sẽ chỉ gửi cookie với các request qua HTTPS nếu cookie được
    đánh dấu "secure". Ứng dụng phải được phục vụ qua HTTPS để điều này có
    ý nghĩa.

    Mặc định: ``False``

.. py:data:: SESSION_COOKIE_PARTITIONED

    Các trình duyệt sẽ gửi cookie dựa trên tên miền của tài liệu cấp cao nhất, thay vì
    chỉ tên miền của tài liệu đặt cookie. Điều này ngăn chặn các cookie của bên thứ ba
    được đặt trong iframe khỏi việc "rò rỉ" giữa các trang web riêng biệt.

    Các trình duyệt đang bắt đầu không cho phép các cookie của bên thứ ba không được phân vùng, vì vậy
    bạn cần đánh dấu cookie của mình là được phân vùng nếu bạn mong đợi chúng hoạt động trong các tình huống
    nhúng như vậy.

    Bật cái này ngầm định bật :data:`SESSION_COOKIE_SECURE` cũng như, vì
    nó chỉ hợp lệ khi được phục vụ qua HTTPS.

    Mặc định: ``False``

    .. versionadded:: 3.1

.. py:data:: SESSION_COOKIE_SAMESITE

    Hạn chế cách cookie được gửi với các request từ các trang web bên ngoài. Có thể
    được đặt thành ``'Lax'`` (khuyến nghị) hoặc ``'Strict'``.
    Xem :ref:`security-cookie`.

    Mặc định: ``None``

    .. versionadded:: 1.0

.. py:data:: PERMANENT_SESSION_LIFETIME

    Nếu ``session.permanent`` là đúng, thời gian hết hạn của cookie sẽ được đặt số
    giây này trong tương lai. Có thể là một
    :class:`datetime.timedelta` hoặc một ``int``.

    Việc triển khai cookie mặc định của Flask xác nhận rằng chữ ký mật mã
    không cũ hơn giá trị này.

    Mặc định: ``timedelta(days=31)`` (``2678400`` giây)

.. py:data:: SESSION_REFRESH_EACH_REQUEST

    Kiểm soát xem cookie có được gửi với mỗi phản hồi khi
    ``session.permanent`` là đúng hay không. Gửi cookie mỗi lần (mặc định)
    có thể giữ cho session không bị hết hạn một cách đáng tin cậy hơn, nhưng sử dụng nhiều băng thông hơn.
    Các session không vĩnh viễn không bị ảnh hưởng.

    Mặc định: ``True``

.. py:data:: USE_X_SENDFILE

    Khi phục vụ các file, đặt header ``X-Sendfile`` thay vì phục vụ
    dữ liệu với Flask. Một số máy chủ web, chẳng hạn như Apache, nhận ra điều này và phục vụ
    dữ liệu hiệu quả hơn. Điều này chỉ có ý nghĩa khi sử dụng một máy chủ như vậy.

    Mặc định: ``False``

.. py:data:: SEND_FILE_MAX_AGE_DEFAULT

    Khi phục vụ các file, đặt tuổi thọ tối đa kiểm soát bộ nhớ cache thành số
    giây này. Có thể là một :class:`datetime.timedelta` hoặc một ``int``.
    Ghi đè giá trị này trên cơ sở từng file bằng cách sử dụng
    :meth:`~flask.Flask.get_send_file_max_age` trên ứng dụng hoặc
    blueprint.

    Nếu ``None``, ``send_file`` bảo trình duyệt sử dụng các request
    có điều kiện sẽ được sử dụng thay vì bộ nhớ cache theo thời gian, điều này thường
    được ưu tiên hơn.

    Mặc định: ``None``

.. py:data:: TRUSTED_HOSTS

    Xác thực :attr:`.Request.host` và các thuộc tính khác sử dụng nó so với
    các giá trị tin cậy này. Ném ra một :exc:`~werkzeug.exceptions.SecurityError` nếu
    host không hợp lệ, dẫn đến lỗi 400. Nếu nó là ``None``, tất cả
    các host đều hợp lệ. Mỗi giá trị là một kết quả khớp chính xác, hoặc có thể bắt đầu bằng
    một dấu chấm ``.`` để khớp với bất kỳ tên miền phụ nào.

    Xác thực được thực hiện trong quá trình định tuyến so với giá trị này. Các callback ``before_request`` và
    ``after_request`` vẫn sẽ được gọi.

    Mặc định: ``None``

    .. versionadded:: 3.1

.. py:data:: SERVER_NAME

    Thông báo cho ứng dụng biết host và port nào nó được liên kết.

    Phải được đặt nếu ``subdomain_matching`` được bật, để có thể trích xuất
    tên miền phụ từ request.

    Phải được đặt cho ``url_for`` để tạo các URL bên ngoài bên ngoài một
    request context.

    Mặc định: ``None``

    .. versionchanged:: 3.1
        Không hạn chế các request chỉ đến tên miền này, cho cả
        ``subdomain_matching`` và ``host_matching``.

    .. versionchanged:: 1.0
        Không ngầm định bật ``subdomain_matching``.

    .. versionchanged:: 2.3
        Không ảnh hưởng đến ``SESSION_COOKIE_DOMAIN``.

.. py:data:: APPLICATION_ROOT

    Thông báo cho ứng dụng biết đường dẫn nào nó được gắn dưới bởi ứng dụng /
    máy chủ web. Điều này được sử dụng để tạo URL bên ngoài ngữ cảnh của một
    request (bên trong một request, bộ điều phối chịu trách nhiệm thiết lập
    ``SCRIPT_NAME`` thay vào đó; xem :doc:`/patterns/appdispatch`
    để biết các ví dụ về cấu hình điều phối).

    Sẽ được sử dụng cho đường dẫn cookie session nếu ``SESSION_COOKIE_PATH`` không được
    đặt.

    Mặc định: ``'/'``

.. py:data:: PREFERRED_URL_SCHEME

    Sử dụng lược đồ này để tạo các URL bên ngoài khi không ở trong một request context.

    Mặc định: ``'http'``

.. py:data:: MAX_CONTENT_LENGTH

    Số byte tối đa sẽ được đọc trong request này. Nếu
    giới hạn này bị vượt quá, một lỗi 413 :exc:`~werkzeug.exceptions.RequestEntityTooLarge`
    được ném ra. Nếu nó được đặt thành ``None``, không có giới hạn nào được thực thi ở cấp độ
    ứng dụng Flask. Tuy nhiên, nếu nó là ``None`` và request không có
    header ``Content-Length`` và máy chủ WSGI không chỉ ra rằng nó
    chấm dứt luồng, thì không có dữ liệu nào được đọc để tránh một luồng vô hạn.

    Mỗi request mặc định theo cấu hình này. Nó có thể được đặt trên một
    :attr:`.Request.max_content_length` cụ thể để áp dụng giới hạn cho view
    cụ thể đó. Điều này nên được đặt một cách thích hợp dựa trên nhu cầu cụ thể của ứng dụng hoặc view.

    Mặc định: ``None``

    .. versionadded:: 0.6

.. py:data:: MAX_FORM_MEMORY_SIZE

    Kích thước tối đa tính bằng byte mà bất kỳ trường form không phải file nào có thể có trong một
    body ``multipart/form-data``. Nếu giới hạn này bị vượt quá, một lỗi 413
    :exc:`~werkzeug.exceptions.RequestEntityTooLarge` được ném ra. Nếu nó
    được đặt thành ``None``, không có giới hạn nào được thực thi ở cấp độ ứng dụng Flask.

    Mỗi request mặc định theo cấu hình này. Nó có thể được đặt trên một
    :attr:`.Request.max_form_memory_parts` cụ thể để áp dụng giới hạn cho view
    cụ thể đó. Điều này nên được đặt một cách thích hợp dựa trên nhu cầu cụ thể của ứng dụng hoặc view.

    Mặc định: ``500_000``

    .. versionadded:: 3.1

.. py:data:: MAX_FORM_PARTS

    Số lượng trường tối đa có thể có trong một
    body ``multipart/form-data``. Nếu giới hạn này bị vượt quá, một lỗi 413
    :exc:`~werkzeug.exceptions.RequestEntityTooLarge` được ném ra. Nếu nó
    được đặt thành ``None``, không có giới hạn nào được thực thi ở cấp độ ứng dụng Flask.

    Mỗi request mặc định theo cấu hình này. Nó có thể được đặt trên một
    :attr:`.Request.max_form_parts` cụ thể để áp dụng giới hạn cho view cụ thể đó.
    Điều này nên được đặt một cách thích hợp dựa trên nhu cầu cụ thể của ứng dụng hoặc view.

    Mặc định: ``1_000``

    .. versionadded:: 3.1

.. py:data:: TEMPLATES_AUTO_RELOAD

    Tải lại các template khi chúng thay đổi. Nếu không được đặt, nó sẽ được bật trong
    chế độ debug.

    Mặc định: ``None``

.. py:data:: EXPLAIN_TEMPLATE_LOADING

    Ghi log thông tin gỡ lỗi theo dõi cách một file template được tải. Điều này có thể
    hữu ích để tìm ra lý do tại sao một template không được tải hoặc file sai
    dường như được tải.

    Mặc định: ``False``

.. py:data:: MAX_COOKIE_SIZE

    Cảnh báo nếu các header cookie lớn hơn số byte này. Mặc định là
    ``4093``. Các cookie lớn hơn có thể bị các trình duyệt bỏ qua một cách âm thầm. Đặt thành
    ``0`` để tắt cảnh báo.

.. py:data:: PROVIDE_AUTOMATIC_OPTIONS

    Đặt thành ``False`` để tắt việc tự động thêm các phản hồi OPTIONS.
    Điều này có thể được ghi đè trên mỗi route bằng cách thay đổi thuộc tính
    ``provide_automatic_options``.

.. versionadded:: 0.4
   ``LOGGER_NAME``

.. versionadded:: 0.5
   ``SERVER_NAME``

.. versionadded:: 0.6
   ``MAX_CONTENT_LENGTH``

.. versionadded:: 0.7
   ``PROPAGATE_EXCEPTIONS``, ``PRESERVE_CONTEXT_ON_EXCEPTION``

.. versionadded:: 0.8
   ``TRAP_BAD_REQUEST_ERRORS``, ``TRAP_HTTP_EXCEPTIONS``,
   ``APPLICATION_ROOT``, ``SESSION_COOKIE_DOMAIN``,
   ``SESSION_COOKIE_PATH``, ``SESSION_COOKIE_HTTPONLY``,
   ``SESSION_COOKIE_SECURE``

.. versionadded:: 0.9
   ``PREFERRED_URL_SCHEME``

.. versionadded:: 0.10
   ``JSON_AS_ASCII``, ``JSON_SORT_KEYS``, ``JSONIFY_PRETTYPRINT_REGULAR``

.. versionadded:: 0.11
   ``SESSION_REFRESH_EACH_REQUEST``, ``TEMPLATES_AUTO_RELOAD``,
   ``LOGGER_HANDLER_POLICY``, ``EXPLAIN_TEMPLATE_LOADING``

.. versionchanged:: 1.0
    ``LOGGER_NAME`` và ``LOGGER_HANDLER_POLICY`` đã bị xóa. Xem
    :doc:`/logging` để biết thông tin về cấu hình.

    Đã thêm :data:`ENV` để phản ánh biến môi trường :envvar:`FLASK_ENV`.

    Đã thêm :data:`SESSION_COOKIE_SAMESITE` để kiểm soát tùy chọn
    ``SameSite`` của cookie session.

    Đã thêm :data:`MAX_COOKIE_SIZE` để kiểm soát cảnh báo từ Werkzeug.

.. versionchanged:: 2.2
    Đã xóa ``PRESERVE_CONTEXT_ON_EXCEPTION``.

.. versionchanged:: 2.3
    ``JSON_AS_ASCII``, ``JSON_SORT_KEYS``, ``JSONIFY_MIMETYPE``, và
    ``JSONIFY_PRETTYPRINT_REGULAR`` đã bị xóa. Nhà cung cấp ``app.json`` mặc định có
    các thuộc tính tương đương thay thế.

.. versionchanged:: 2.3
    ``ENV`` đã bị xóa.

.. versionadded:: 3.10
    Đã thêm :data:`PROVIDE_AUTOMATIC_OPTIONS` để kiểm soát việc mặc định
    thêm các phản hồi OPTIONS được tạo tự động.


Cấu hình từ File Python
-----------------------

Cấu hình trở nên hữu ích hơn nếu bạn có thể lưu trữ nó trong một file riêng biệt, lý tưởng nhất là
nằm bên ngoài package ứng dụng thực tế. Bạn có thể triển khai ứng dụng của mình, sau đó
cấu hình riêng cho việc triển khai cụ thể.

Một mẫu phổ biến là thế này::

    app = Flask(__name__)
    app.config.from_object('yourapplication.default_settings')
    app.config.from_envvar('YOURAPPLICATION_SETTINGS')

Đầu tiên tải cấu hình từ module
`yourapplication.default_settings` và sau đó ghi đè các giá trị
với nội dung của file mà biến môi trường :envvar:`YOURAPPLICATION_SETTINGS`
trỏ tới. Biến môi trường này có thể được đặt
trong shell trước khi khởi động máy chủ:

.. tabs::

   .. group-tab:: Bash

      .. code-block:: text

         $ export YOURAPPLICATION_SETTINGS=/path/to/settings.cfg
         $ flask run
          * Running on http://127.0.0.1:5000/

   .. group-tab:: Fish

      .. code-block:: text

         $ set -x YOURAPPLICATION_SETTINGS /path/to/settings.cfg
         $ flask run
          * Running on http://127.0.0.1:5000/

   .. group-tab:: CMD

      .. code-block:: text

         > set YOURAPPLICATION_SETTINGS=\path\to\settings.cfg
         > flask run
          * Running on http://127.0.0.1:5000/

   .. group-tab:: Powershell

      .. code-block:: text

         > $env:YOURAPPLICATION_SETTINGS = "\path\to\settings.cfg"
         > flask run
          * Running on http://127.0.0.1:5000/

Bản thân các file cấu hình là các file Python thực tế. Chỉ các giá trị
viết hoa mới thực sự được lưu trữ trong đối tượng config sau này. Vì vậy hãy chắc chắn
sử dụng các chữ cái viết hoa cho các khóa cấu hình của bạn.

Dưới đây là một ví dụ về file cấu hình::

    # Cấu hình ví dụ
    SECRET_KEY = '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'

Hãy chắc chắn tải cấu hình từ rất sớm, để các tiện ích mở rộng có
khả năng truy cập cấu hình khi khởi động. Cũng có các phương thức khác
trên đối tượng config để tải từ các file riêng lẻ. Để có một
tham khảo đầy đủ, hãy đọc tài liệu của đối tượng :class:`~flask.Config`.


Cấu hình từ File Dữ liệu
------------------------

Cũng có thể tải cấu hình từ một file ở định dạng
bạn chọn bằng cách sử dụng :meth:`~flask.Config.from_file`. Ví dụ để tải
từ một file TOML:

.. code-block:: python

    import tomllib
    app.config.from_file("config.toml", load=tomllib.load, text=False)

Hoặc từ một file JSON:

.. code-block:: python

    import json
    app.config.from_file("config.json", load=json.load)


Cấu hình từ Biến Môi trường
---------------------------

Ngoài việc trỏ đến các file cấu hình bằng cách sử dụng các biến
môi trường, bạn có thể thấy hữu ích (hoặc cần thiết) để kiểm soát các
giá trị cấu hình của mình trực tiếp từ môi trường. Flask có thể được
hướng dẫn tải tất cả các biến môi trường bắt đầu bằng một tiền tố
cụ thể vào config bằng cách sử dụng :meth:`~flask.Config.from_prefixed_env`.

Các biến môi trường có thể được đặt trong shell trước khi khởi động
máy chủ:

.. tabs::

   .. group-tab:: Bash

      .. code-block:: text

         $ export FLASK_SECRET_KEY="5f352379324c22463451387a0aec5d2f"
         $ export FLASK_MAIL_ENABLED=false
         $ flask run
          * Running on http://127.0.0.1:5000/

   .. group-tab:: Fish

      .. code-block:: text

         $ set -x FLASK_SECRET_KEY "5f352379324c22463451387a0aec5d2f"
         $ set -x FLASK_MAIL_ENABLED false
         $ flask run
          * Running on http://127.0.0.1:5000/

   .. group-tab:: CMD

      .. code-block:: text

         > set FLASK_SECRET_KEY="5f352379324c22463451387a0aec5d2f"
         > set FLASK_MAIL_ENABLED=false
         > flask run
          * Running on http://127.0.0.1:5000/

   .. group-tab:: Powershell

      .. code-block:: text

         > $env:FLASK_SECRET_KEY = "5f352379324c22463451387a0aec5d2f"
         > $env:FLASK_MAIL_ENABLED = "false"
         > flask run
          * Running on http://127.0.0.1:5000/

Các biến sau đó có thể được tải và truy cập thông qua config với một khóa
bằng tên biến môi trường không có tiền tố, tức là

.. code-block:: python

    app.config.from_prefixed_env()
    app.config["SECRET_KEY"]  # Là "5f352379324c22463451387a0aec5d2f"

Tiền tố là ``FLASK_`` theo mặc định. Điều này có thể cấu hình được thông qua
đối số ``prefix`` của :meth:`~flask.Config.from_prefixed_env`.

Các giá trị sẽ được phân tích cú pháp để cố gắng chuyển đổi chúng thành một loại cụ thể hơn
là chuỗi. Theo mặc định :func:`json.loads` được sử dụng, vì vậy bất kỳ giá trị JSON hợp lệ nào
đều có thể, bao gồm danh sách và dict. Điều này có thể cấu hình được thông qua
đối số ``loads`` của :meth:`~flask.Config.from_prefixed_env`.

Khi thêm một giá trị boolean với phân tích cú pháp JSON mặc định, chỉ "true"
và "false", chữ thường, là các giá trị hợp lệ. Hãy nhớ rằng bất kỳ
chuỗi không rỗng nào đều được coi là ``True`` bởi Python.

Có thể đặt các khóa trong các từ điển lồng nhau bằng cách tách các
khóa bằng dấu gạch dưới kép (``__``). Bất kỳ khóa trung gian nào không
tồn tại trên dict cha sẽ được khởi tạo thành một dict rỗng.

.. code-block:: text

    $ export FLASK_MYAPI__credentials__username=user123

.. code-block:: python

    app.config["MYAPI"]["credentials"]["username"]  # Là "user123"

Trên Windows, các khóa biến môi trường luôn viết hoa, do đó
ví dụ trên sẽ kết thúc là ``MYAPI__CREDENTIALS__USERNAME``.

Để có thêm nhiều tính năng tải cấu hình hơn, bao gồm hợp nhất và
hỗ trợ Windows không phân biệt chữ hoa chữ thường, hãy thử một thư viện chuyên dụng như
Dynaconf_, bao gồm tích hợp với Flask.

.. _Dynaconf: https://www.dynaconf.com/


Các Thực hành Tốt nhất về Cấu hình
----------------------------------

Nhược điểm với cách tiếp cận được đề cập trước đó là nó làm cho việc kiểm thử
khó hơn một chút. Không có giải pháp 100% duy nhất cho vấn đề này nói
chung, nhưng có một vài điều bạn có thể ghi nhớ để cải thiện
trải nghiệm đó:

1.  Tạo ứng dụng của bạn trong một hàm và đăng ký blueprints trên đó.
    Bằng cách đó bạn có thể tạo nhiều thể hiện của ứng dụng của mình với
    các cấu hình khác nhau được đính kèm giúp việc kiểm thử đơn vị dễ dàng hơn
    nhiều. Bạn có thể sử dụng điều này để truyền vào cấu hình khi cần thiết.

2.  Không viết mã cần cấu hình tại thời điểm import. Nếu bạn
    tự giới hạn mình chỉ truy cập cấu hình trong request bạn có thể
    cấu hình lại đối tượng sau đó khi cần thiết.

3.  Hãy chắc chắn tải cấu hình từ rất sớm, để
    các tiện ích mở rộng có thể truy cập cấu hình khi gọi ``init_app``.


.. _config-dev-prod:

Phát triển / Sản xuất
---------------------

Hầu hết các ứng dụng cần nhiều hơn một cấu hình. Nên có ít nhất
các cấu hình riêng biệt cho máy chủ sản xuất và cái được sử dụng
trong quá trình phát triển. Cách dễ nhất để xử lý điều này là sử dụng một cấu hình
mặc định luôn được tải và là một phần của kiểm soát phiên bản, và một
cấu hình riêng biệt ghi đè các giá trị khi cần thiết như đã đề cập
trong ví dụ trên::

    app = Flask(__name__)
    app.config.from_object('yourapplication.default_settings')
    app.config.from_envvar('YOURAPPLICATION_SETTINGS')

Sau đó bạn chỉ cần thêm một file :file:`config.py` riêng biệt và export
``YOURAPPLICATION_SETTINGS=/path/to/config.py`` và bạn đã hoàn tất. Tuy nhiên
cũng có những cách thay thế. Ví dụ bạn có thể sử dụng imports hoặc
subclassing.

Điều rất phổ biến trong thế giới Django là làm cho việc import rõ ràng trong
file config bằng cách thêm ``from yourapplication.default_settings
import *`` vào đầu file và sau đó ghi đè các thay đổi bằng tay.
Bạn cũng có thể kiểm tra một biến môi trường như
``YOURAPPLICATION_MODE`` và đặt nó thành `production`, `development` v.v.
và import các file được mã hóa cứng khác nhau dựa trên đó.

Một mẫu thú vị cũng là sử dụng các lớp và kế thừa cho
cấu hình::

    class Config(object):
        TESTING = False

    class ProductionConfig(Config):
        DATABASE_URI = 'mysql://user@localhost/foo'

    class DevelopmentConfig(Config):
        DATABASE_URI = "sqlite:////tmp/foo.db"

    class TestingConfig(Config):
        DATABASE_URI = 'sqlite:///:memory:'
        TESTING = True

Để kích hoạt một cấu hình như vậy bạn chỉ cần gọi vào
:meth:`~flask.Config.from_object`::

    app.config.from_object('configmodule.ProductionConfig')

Lưu ý rằng :meth:`~flask.Config.from_object` không khởi tạo đối tượng
lớp. Nếu bạn cần khởi tạo lớp, chẳng hạn như để truy cập một thuộc tính,
thì bạn phải làm như vậy trước khi gọi :meth:`~flask.Config.from_object`::

    from configmodule import ProductionConfig
    app.config.from_object(ProductionConfig())

    # Ngoài ra, import qua chuỗi:
    from werkzeug.utils import import_string
    cfg = import_string('configmodule.ProductionConfig')()
    app.config.from_object(cfg)

Khởi tạo đối tượng cấu hình cho phép bạn sử dụng ``@property`` trong
các lớp cấu hình của bạn::

    class Config(object):
        """Cấu hình cơ sở, sử dụng máy chủ cơ sở dữ liệu staging."""
        TESTING = False
        DB_SERVER = '192.168.1.56'

        @property
        def DATABASE_URI(self):  # Lưu ý: viết hoa toàn bộ
            return f"mysql://user@{self.DB_SERVER}/foo"

    class ProductionConfig(Config):
        """Sử dụng máy chủ cơ sở dữ liệu sản xuất."""
        DB_SERVER = '192.168.19.32'

    class DevelopmentConfig(Config):
        DB_SERVER = 'localhost'

    class TestingConfig(Config):
        DB_SERVER = 'localhost'
        DATABASE_URI = 'sqlite:///:memory:'

Có nhiều cách khác nhau và tùy thuộc vào bạn cách bạn muốn quản lý
các file cấu hình của mình. Tuy nhiên đây là một danh sách các khuyến nghị tốt:

-   Giữ một cấu hình mặc định trong kiểm soát phiên bản. Hoặc điền vào
    config với cấu hình mặc định này hoặc import nó trong các file
    cấu hình của riêng bạn trước khi ghi đè các giá trị.
-   Sử dụng một biến môi trường để chuyển đổi giữa các cấu hình.
    Điều này có thể được thực hiện từ bên ngoài trình thông dịch Python và làm cho
    việc phát triển và triển khai dễ dàng hơn nhiều vì bạn có thể nhanh chóng và
    dễ dàng chuyển đổi giữa các cấu hình khác nhau mà không cần phải chạm vào
    mã chút nào. Nếu bạn thường xuyên làm việc trên các dự án khác nhau bạn có thể
    thậm chí tạo script của riêng bạn để sourcing kích hoạt một virtualenv
    và export cấu hình phát triển cho bạn.
-   Sử dụng một công cụ như `fabric`_ để đẩy mã và cấu hình riêng biệt
    đến (các) máy chủ sản xuất.

.. _fabric: https://www.fabfile.org/


.. _instance-folders:

Thư mục Instance
----------------

.. versionadded:: 0.8

Flask 0.8 giới thiệu các thư mục instance. Flask trong một thời gian dài đã làm cho nó
có thể tham chiếu đến các đường dẫn tương đối đến thư mục của ứng dụng trực tiếp
(thông qua :attr:`Flask.root_path`). Đây cũng là cách nhiều nhà phát triển tải
các cấu hình được lưu trữ bên cạnh ứng dụng. Tuy nhiên thật không may điều này
chỉ hoạt động tốt nếu các ứng dụng không phải là các package trong trường hợp đó đường dẫn gốc
tham chiếu đến nội dung của package.

Với Flask 0.8 một thuộc tính mới được giới thiệu:
:attr:`Flask.instance_path`. Nó tham chiếu đến một khái niệm mới gọi là
“thư mục instance”. Thư mục instance được thiết kế để không nằm dưới
kiểm soát phiên bản và cụ thể cho việc triển khai. Đó là nơi hoàn hảo để
thả những thứ thay đổi khi chạy hoặc các file cấu hình.

Bạn có thể cung cấp rõ ràng đường dẫn của thư mục instance khi
tạo ứng dụng Flask hoặc bạn có thể để Flask tự động phát hiện
thư mục instance. Để cấu hình rõ ràng sử dụng tham số `instance_path`::

    app = Flask(__name__, instance_path='/path/to/instance/folder')

Vui lòng ghi nhớ rằng đường dẫn này *phải* là tuyệt đối khi được cung cấp.

Nếu tham số `instance_path` không được cung cấp các vị trí mặc định sau
được sử dụng:

-   Module chưa cài đặt::

        /myapp.py
        /instance

-   Package chưa cài đặt::

        /myapp
            /__init__.py
        /instance

-   Module hoặc package đã cài đặt::

        $PREFIX/lib/pythonX.Y/site-packages/myapp
        $PREFIX/var/myapp-instance

    ``$PREFIX`` là tiền tố cài đặt Python của bạn. Đây có thể là
    ``/usr`` hoặc đường dẫn đến virtualenv của bạn. Bạn có thể in giá trị của
    ``sys.prefix`` để xem tiền tố được đặt thành gì.

Vì đối tượng config cung cấp khả năng tải các file cấu hình từ
tên file tương đối, chúng tôi đã làm cho nó có thể thay đổi việc tải qua tên file
thành tương đối với đường dẫn instance nếu muốn. Hành vi của các đường dẫn
tương đối trong các file cấu hình có thể được chuyển đổi giữa “tương đối với thư mục gốc
ứng dụng” (mặc định) sang “tương đối với thư mục instance” thông qua
công tắc `instance_relative_config` cho hàm tạo ứng dụng::

    app = Flask(__name__, instance_relative_config=True)

Dưới đây là một ví dụ đầy đủ về cách cấu hình Flask để tải trước cấu hình
từ một module và sau đó ghi đè cấu hình từ một file trong thư mục
instance nếu nó tồn tại::

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('yourapplication.default_settings')
    app.config.from_pyfile('application.cfg', silent=True)

Đường dẫn đến thư mục instance có thể được tìm thấy thông qua
:attr:`Flask.instance_path`. Flask cũng cung cấp một lối tắt để mở một
file từ thư mục instance với :meth:`Flask.open_instance_resource`.

Ví dụ sử dụng cho cả hai::

    filename = os.path.join(app.instance_path, 'application.cfg')
    with open(filename) as f:
        config = f.read()

    # hoặc qua open_instance_resource:
    with app.open_instance_resource('application.cfg') as f:
        config = f.read()

