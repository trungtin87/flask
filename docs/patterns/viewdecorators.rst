View Decorator
==============

Python có một tính năng thực sự thú vị gọi là function decorator. Điều này
cho phép một số điều thực sự gọn gàng cho các ứng dụng web. Bởi vì mỗi view trong
Flask là một hàm, decorator có thể được sử dụng để inject chức năng
bổ sung vào một hoặc nhiều hàm. Decorator :meth:`~flask.Flask.route`
là cái bạn có thể đã sử dụng rồi. Nhưng có các trường hợp sử dụng
để triển khai decorator của riêng bạn. Ví dụ, hãy tưởng tượng bạn có một
view chỉ nên được sử dụng bởi những người đã đăng nhập. Nếu một người dùng
đến trang web và chưa đăng nhập, họ nên được chuyển hướng đến
trang đăng nhập. Đây là một ví dụ tốt về một trường hợp sử dụng mà decorator là một
giải pháp tuyệt vời.

Login Required Decorator
------------------------

Vì vậy, hãy triển khai một decorator như vậy. Một decorator là một hàm
bao bọc và thay thế một hàm khác. Vì hàm gốc bị
thay thế, bạn cần nhớ sao chép thông tin của hàm gốc
sang hàm mới. Sử dụng :func:`functools.wraps` để xử lý điều này cho bạn.

Ví dụ này giả định rằng trang đăng nhập được gọi là ``'login'`` và
người dùng hiện tại được lưu trữ trong ``g.user`` và là ``None`` nếu không có ai
đăng nhập. ::

    from functools import wraps
    from flask import g, request, redirect, url_for

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user is None:
                return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function

Để sử dụng decorator, áp dụng nó như decorator trong cùng cho một view function.
Khi áp dụng các decorator khác, luôn nhớ
rằng decorator :meth:`~flask.Flask.route` là decorator ngoài cùng. ::

    @app.route('/secret_page')
    @login_required
    def secret_page():
        pass

.. note::
    Giá trị ``next`` sẽ tồn tại trong ``request.args`` sau một request ``GET`` cho
    trang đăng nhập. Bạn sẽ phải truyền nó cùng khi gửi request ``POST``
    từ form đăng nhập. Bạn có thể làm điều này với một thẻ input ẩn, sau đó lấy nó
    từ ``request.form`` khi đăng nhập người dùng. ::

        <input type="hidden" value="{{ request.args.get('next', '') }}"/>


Caching Decorator
-----------------

Hãy tưởng tượng bạn có một view function thực hiện một phép tính tốn kém và
vì điều đó bạn muốn cache các kết quả được tạo ra trong một
khoảng thời gian nhất định. Một decorator sẽ rất tốt cho điều đó. Chúng tôi
giả định bạn đã thiết lập một cache như đã đề cập trong :doc:`caching`.

Đây là một hàm cache ví dụ. Nó tạo ra cache key từ một
tiền tố cụ thể (thực sự là một chuỗi định dạng) và đường dẫn hiện tại của
request. Lưu ý rằng chúng ta đang sử dụng một hàm đầu tiên tạo
decorator sau đó decorate hàm. Nghe có vẻ khủng khiếp? Thật không may
nó phức tạp hơn một chút, nhưng mã vẫn nên
dễ đọc.

Hàm được decorate sau đó sẽ hoạt động như sau

1. lấy cache key duy nhất cho request hiện tại dựa trên đường dẫn
   hiện tại.
2. lấy giá trị cho key đó từ cache. Nếu cache trả về
   một cái gì đó chúng ta sẽ trả về giá trị đó.
3. nếu không hàm gốc được gọi và giá trị trả về được
   lưu trữ trong cache cho timeout được cung cấp (theo mặc định 5 phút).

Đây là mã::

    from functools import wraps
    from flask import request

    def cached(timeout=5 * 60, key='view/{}'):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                cache_key = key.format(request.path)
                rv = cache.get(cache_key)
                if rv is not None:
                    return rv
                rv = f(*args, **kwargs)
                cache.set(cache_key, rv, timeout=timeout)
                return rv
            return decorated_function
        return decorator

Lưu ý rằng điều này giả định một đối tượng ``cache`` được khởi tạo có sẵn, xem
:doc:`caching`.


Templating Decorator
--------------------

Một mẫu phổ biến được phát minh bởi các anh chàng TurboGears một thời gian trước là một
templating decorator. Ý tưởng của decorator đó là bạn trả về một
dictionary với các giá trị được truyền cho template từ view function
và template được tự động render. Với điều đó, ba
ví dụ sau làm chính xác điều tương tự::

    @app.route('/')
    def index():
        return render_template('index.html', value=42)

    @app.route('/')
    @templated('index.html')
    def index():
        return dict(value=42)

    @app.route('/')
    @templated()
    def index():
        return dict(value=42)

Như bạn có thể thấy, nếu không có tên template nào được cung cấp, nó sẽ sử dụng endpoint
của URL map với các dấu chấm được chuyển đổi thành dấu gạch chéo + ``'.html'``. Nếu không
tên template được cung cấp sẽ được sử dụng. Khi hàm được decorate trả về,
dictionary được trả về được truyền cho hàm render template. Nếu
``None`` được trả về, một dictionary trống được giả định, nếu một cái gì đó khác ngoài
một dictionary được trả về, chúng ta trả về nó từ hàm không thay đổi. Bằng cách đó
bạn vẫn có thể sử dụng hàm redirect hoặc trả về các chuỗi đơn giản.

Đây là mã cho decorator đó::

    from functools import wraps
    from flask import request, render_template

    def templated(template=None):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                template_name = template
                if template_name is None:
                    template_name = f"{request.endpoint.replace('.', '/')}.html"
                ctx = f(*args, **kwargs)
                if ctx is None:
                    ctx = {}
                elif not isinstance(ctx, dict):
                    return ctx
                return render_template(template_name, **ctx)
            return decorated_function
        return decorator


Endpoint Decorator
------------------

Khi bạn muốn sử dụng hệ thống routing werkzeug để có tính linh hoạt hơn, bạn
cần ánh xạ endpoint như được định nghĩa trong :class:`~werkzeug.routing.Rule`
đến một view function. Điều này có thể thực hiện được với decorator này. Ví dụ::

    from flask import Flask
    from werkzeug.routing import Rule

    app = Flask(__name__)
    app.url_map.add(Rule('/', endpoint='index'))

    @app.endpoint('index')
    def my_index():
        return "Hello world"
