Cấu trúc và Vòng đời Ứng dụng
==============================

Flask làm cho việc viết một ứng dụng web khá dễ dàng. Nhưng có khá nhiều
phần khác nhau trong một ứng dụng và cho mỗi request mà nó xử lý. Biết những gì xảy ra
trong quá trình thiết lập ứng dụng, phục vụ, và xử lý request sẽ giúp bạn biết những gì
có thể trong Flask và cách cấu trúc ứng dụng của bạn.


Thiết lập Ứng dụng
------------------

Bước đầu tiên trong việc tạo một ứng dụng Flask là tạo đối tượng ứng dụng. Mỗi
ứng dụng Flask là một instance của class :class:`.Flask`, thu thập tất cả
cấu hình, extension, và view.

.. code-block:: python

    from flask import Flask

    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="dev",
    )
    app.config.from_prefixed_env()

    @app.route("/")
    def index():
        return "Hello, World!"

Đây được gọi là "giai đoạn thiết lập ứng dụng", đó là mã bạn viết nằm ngoài
bất kỳ view function hoặc handler nào khác. Nó có thể được chia thành các module và
sub-package khác nhau, nhưng tất cả mã mà bạn muốn là một phần của ứng dụng của bạn phải được import
để nó được đăng ký.

Tất cả thiết lập ứng dụng phải được hoàn thành trước khi bạn bắt đầu phục vụ ứng dụng của mình và
xử lý request. Điều này là vì các máy chủ WSGI chia công việc giữa nhiều worker, hoặc
có thể được phân phối trên nhiều máy. Nếu cấu hình thay đổi trong một worker,
không có cách nào cho Flask đảm bảo tính nhất quán giữa các worker khác.

Flask cố gắng giúp các nhà phát triển bắt một số vấn đề thứ tự thiết lập này bằng cách hiển thị một
lỗi nếu các phương thức liên quan đến thiết lập được gọi sau khi các request được xử lý. Trong trường hợp đó
bạn sẽ thấy lỗi này:

    The setup method 'route' can no longer be called on the application. It has already
    handled its first request, any changes will not be applied consistently.
    Make sure all imports, decorators, functions, etc. needed to set up the application
    are done before running it.

Tuy nhiên, Flask không thể phát hiện tất cả các trường hợp thiết lập không đúng thứ tự. Nói chung
, đừng làm bất cứ điều gì để sửa đổi đối tượng ``Flask`` app và đối tượng ``Blueprint``
từ trong các view function chạy trong các request. Điều này bao gồm:

-   Thêm route, view function, và các request handler khác với ``@app.route``,
    ``@app.errorhandler``, ``@app.before_request``, v.v.
-   Đăng ký blueprint.
-   Tải cấu hình với ``app.config``.
-   Thiết lập môi trường template Jinja với ``app.jinja_env``.
-   Đặt một session interface, thay vì cookie itsdangerous mặc định.
-   Đặt một JSON provider với ``app.json``, thay vì provider mặc định.
-   Tạo và khởi tạo Flask extension.


Phục vụ Ứng dụng
----------------

Flask là một framework ứng dụng WSGI. Nửa còn lại của WSGI là máy chủ WSGI. Trong
quá trình phát triển, Flask, thông qua Werkzeug, cung cấp một máy chủ WSGI phát triển với
lệnh CLI ``flask run``. Khi bạn hoàn thành phát triển, hãy sử dụng một máy chủ production
để phục vụ ứng dụng của bạn, xem :doc:`deploying/index`.

Bất kể bạn đang sử dụng máy chủ nào, nó sẽ tuân theo spec WSGI :pep:`3333`. Máy chủ
WSGI sẽ được cho biết cách truy cập đối tượng ứng dụng Flask của bạn, là ứng dụng WSGI
. Sau đó nó sẽ bắt đầu lắng nghe các HTTP request, dịch dữ liệu request
thành một WSGI environ, và gọi ứng dụng WSGI với dữ liệu đó. Ứng dụng WSGI
sẽ trả về dữ liệu được dịch thành một HTTP response.

#.  Trình duyệt hoặc client khác thực hiện HTTP request.
#.  Máy chủ WSGI nhận request.
#.  Máy chủ WSGI chuyển đổi dữ liệu HTTP thành dict WSGI ``environ``.
#.  Máy chủ WSGI gọi ứng dụng WSGI với ``environ``.
#.  Flask, ứng dụng WSGI, thực hiện tất cả xử lý nội bộ của nó để route request
    đến một view function, xử lý lỗi, v.v.
#.  Flask dịch giá trị trả về của View function thành dữ liệu phản hồi WSGI, truyền nó cho máy chủ WSGI
    .
#.  Máy chủ WSGI tạo và gửi một HTTP response.
#.  Client nhận HTTP response.


Middleware
~~~~~~~~~~

Ứng dụng WSGI ở trên là một callable hoạt động theo một cách nhất định. Middleware
là một ứng dụng WSGI wrap một ứng dụng WSGI khác. Đó là một khái niệm tương tự như
decorator Python. Middleware ngoài cùng sẽ được gọi bởi máy chủ. Nó có thể sửa đổi
dữ liệu được truyền cho nó, sau đó gọi ứng dụng WSGI (hoặc middleware khác) mà nó
wrap, và cứ thế. Và nó có thể lấy giá trị trả về của cuộc gọi đó và sửa đổi nó thêm.

Từ quan điểm của máy chủ WSGI, có một ứng dụng WSGI, ứng dụng mà nó gọi
trực tiếp. Thông thường, Flask là ứng dụng "thực" ở cuối chuỗi
middleware. Nhưng ngay cả Flask cũng có thể gọi các ứng dụng WSGI khác, mặc dù đó là một
trường hợp sử dụng nâng cao, không phổ biến.

Một middleware phổ biến mà bạn sẽ thấy được sử dụng với Flask là
:class:`~werkzeug.middleware.proxy_fix.ProxyFix` của Werkzeug, sửa đổi request để trông
như thể nó đến trực tiếp từ một client ngay cả khi nó đi qua các HTTP proxy trên đường đi.
Có các middleware khác có thể xử lý phục vụ file tĩnh, xác thực, v.v.


Cách một Request được Xử lý
----------------------------

Đối với chúng ta, phần thú vị của các bước trên là khi Flask được gọi bởi máy chủ WSGI
(hoặc middleware). Tại thời điểm đó, nó sẽ làm khá nhiều việc để xử lý request và
tạo phản hồi. Ở mức cơ bản nhất, nó sẽ khớp URL với một view function, gọi
view function, và truyền giá trị trả về trở lại máy chủ. Nhưng có nhiều
phần hơn mà bạn có thể sử dụng để tùy chỉnh hành vi của nó.

#.  Máy chủ WSGI gọi đối tượng Flask, gọi :meth:`.Flask.wsgi_app`.
#.  Một đối tượng :class:`.AppContext` được tạo. Điều này chuyển đổi dict WSGI ``environ``
    thành một đối tượng :class:`.Request`.
#.  :doc:`App context <appcontext>` được push, làm cho
    :data:`.current_app`, :data:`.g`, :data:`.request`, và :data:`.session`
    có sẵn.
#.  Signal :data:`.appcontext_pushed` được gửi.
#.  URL được khớp với các quy tắc URL được đăng ký với decorator :meth:`~.Flask.route`
    trong quá trình thiết lập ứng dụng. Nếu không có kết quả khớp, lỗi - thường là 404,
    405, hoặc redirect - được lưu trữ để xử lý sau.
#.  Signal :data:`.request_started` được gửi.
#.  Bất kỳ hàm nào được decorate với :meth:`~.Flask.url_value_preprocessor` được gọi.
#.  Bất kỳ hàm nào được decorate với :meth:`~.Flask.before_request` được gọi. Nếu bất kỳ
    hàm nào trong số này trả về một giá trị, nó được coi là phản hồi ngay lập tức.
#.  Nếu URL không khớp với một route vài bước trước, lỗi đó được đưa ra bây giờ.
#.  View function được decorate với :meth:`~.Flask.route` liên kết với URL khớp
    được gọi và trả về một giá trị để sử dụng làm phản hồi.
#.  Nếu bất kỳ bước nào cho đến nay đưa ra một exception, và có một hàm được decorate với :meth:`~.Flask.errorhandler`
    khớp với class exception hoặc mã lỗi HTTP, nó được
    gọi để xử lý lỗi và trả về một phản hồi.
#.  Bất cứ điều gì trả về một giá trị phản hồi - một before request function, view, hoặc một
    error handler, giá trị đó được chuyển đổi thành một đối tượng :class:`.Response`.
#.  Bất kỳ hàm nào được decorate với :func:`~.after_this_request` được gọi, có thể sửa đổi
    đối tượng phản hồi. Sau đó chúng được xóa.
#.  Bất kỳ hàm nào được decorate với :meth:`~.Flask.after_request` được gọi, có thể sửa đổi
    đối tượng phản hồi.
#.  Session được lưu, duy trì bất kỳ dữ liệu session nào được sửa đổi bằng cách sử dụng
    :attr:`~.Flask.session_interface` của ứng dụng.
#.  Signal :data:`.request_finished` được gửi.
#.  Nếu bất kỳ bước nào cho đến nay đưa ra một exception, và nó không được xử lý bởi một error handler
    function, nó được xử lý bây giờ. Các HTTP exception được coi là phản hồi với
    mã trạng thái tương ứng của chúng, các exception khác được chuyển đổi thành phản hồi 500 chung.
    Signal :data:`.got_request_exception` được gửi.
#.  Trạng thái, header, và body của đối tượng phản hồi được trả về cho máy chủ WSGI.
#.  Bất kỳ hàm nào được decorate với :meth:`~.Flask.teardown_request` được gọi.
#.  Signal :data:`.request_tearing_down` được gửi.
#.  Bất kỳ hàm nào được decorate với :meth:`~.Flask.teardown_appcontext` được gọi.
#.  Signal :data:`.appcontext_tearing_down` được gửi.
#.  App context được popped, :data:`.current_app`, :data:`.g`, :data:`.request`,
    và :data:`.session` không còn có sẵn nữa.
#.  Signal :data:`.appcontext_popped` được gửi.

Khi thực thi một lệnh CLI hoặc app context đơn giản không có dữ liệu request, cùng một
thứ tự các bước được tuân theo, bỏ qua các bước tham chiếu đến request.

Một :class:`Blueprint` có thể thêm handler cho các sự kiện này cụ thể cho
blueprint. Các handler cho một blueprint sẽ chạy nếu blueprint
sở hữu route khớp với request.

Có thậm chí nhiều decorator và điểm tùy chỉnh hơn thế này, nhưng không phải là một phần
của mỗi vòng đời request. Chúng cụ thể hơn cho một số điều nhất định bạn có thể sử dụng trong
một request, chẳng hạn như template, xây dựng URL, hoặc xử lý dữ liệu JSON. Xem phần còn lại của
tài liệu này, cũng như :doc:`api` để khám phá thêm.
