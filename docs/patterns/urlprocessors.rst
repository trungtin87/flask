Sử dụng URL Processor
=====================

.. versionadded:: 0.7

Flask 0.7 giới thiệu khái niệm về URL processor. Ý tưởng là bạn
có thể có một loạt tài nguyên với các phần chung trong URL mà bạn
không phải lúc nào cũng muốn cung cấp một cách rõ ràng. Ví dụ bạn có thể có một
loạt URL có mã ngôn ngữ trong đó nhưng bạn không muốn phải
xử lý nó trong mọi hàm đơn lẻ.

URL processor đặc biệt hữu ích khi kết hợp với blueprint. Chúng tôi
sẽ xử lý cả URL processor cụ thể cho ứng dụng ở đây cũng như
các đặc điểm cụ thể của blueprint.

URL Ứng dụng Quốc tế hóa
------------------------

Hãy xem xét một ứng dụng như thế này::

    from flask import Flask, g

    app = Flask(__name__)

    @app.route('/<lang_code>/')
    def index(lang_code):
        g.lang_code = lang_code
        ...

    @app.route('/<lang_code>/about')
    def about(lang_code):
        g.lang_code = lang_code
        ...

Đây là rất nhiều lặp lại vì bạn phải xử lý việc đặt mã ngôn ngữ
trên đối tượng :data:`~flask.g` trong mọi hàm đơn lẻ.
Chắc chắn, một decorator có thể được sử dụng để đơn giản hóa điều này, nhưng nếu bạn muốn
tạo URL từ một hàm sang hàm khác, bạn vẫn phải cung cấp
mã ngôn ngữ một cách rõ ràng, điều này có thể gây phiền toái.

Đối với cái sau, đây là nơi các hàm :func:`~flask.Flask.url_defaults`
xuất hiện. Chúng có thể tự động inject các giá trị vào một cuộc gọi đến
:func:`~flask.url_for`. Mã dưới đây kiểm tra xem
mã ngôn ngữ chưa có trong từ điển các giá trị URL và nếu
endpoint muốn một giá trị có tên ``'lang_code'``::

    @app.url_defaults
    def add_language_code(endpoint, values):
        if 'lang_code' in values or not g.lang_code:
            return
        if app.url_map.is_endpoint_expecting(endpoint, 'lang_code'):
            values['lang_code'] = g.lang_code

Phương thức :meth:`~werkzeug.routing.Map.is_endpoint_expecting` của URL
map có thể được sử dụng để tìm ra xem có hợp lý không khi cung cấp một mã ngôn ngữ
cho endpoint đã cho.

Ngược lại của hàm đó là
:meth:`~flask.Flask.url_value_preprocessor`\\s. Chúng được thực thi ngay
sau khi request được khớp và có thể thực thi mã dựa trên các giá trị
URL. Ý tưởng là chúng lấy thông tin ra khỏi từ điển
values và đặt nó ở nơi khác::

    @app.url_value_preprocessor
    def pull_lang_code(endpoint, values):
        g.lang_code = values.pop('lang_code', None)

Bằng cách đó bạn không còn phải thực hiện gán `lang_code` cho
:data:`~flask.g` trong mọi hàm. Bạn có thể cải thiện thêm điều đó bằng cách
viết decorator của riêng bạn thêm tiền tố URL với mã ngôn ngữ, nhưng
giải pháp đẹp hơn là sử dụng một blueprint. Khi
``'lang_code'`` được pop khỏi từ điển values và nó sẽ không còn
được chuyển tiếp đến view function, giảm mã xuống như thế này::

    from flask import Flask, g

    app = Flask(__name__)

    @app.url_defaults
    def add_language_code(endpoint, values):
        if 'lang_code' in values or not g.lang_code:
            return
        if app.url_map.is_endpoint_expecting(endpoint, 'lang_code'):
            values['lang_code'] = g.lang_code

    @app.url_value_preprocessor
    def pull_lang_code(endpoint, values):
        g.lang_code = values.pop('lang_code', None)

    @app.route('/<lang_code>/')
    def index():
        ...

    @app.route('/<lang_code>/about')
    def about():
        ...

URL Blueprint Quốc tế hóa
-------------------------

Bởi vì các blueprint có thể tự động thêm tiền tố cho tất cả các URL với một chuỗi chung
nên dễ dàng tự động làm điều đó cho mọi hàm. Hơn nữa
các blueprint có thể có URL processor cho mỗi blueprint, loại bỏ rất nhiều
logic khỏi hàm :meth:`~flask.Flask.url_defaults` vì nó không
còn phải kiểm tra xem URL có thực sự quan tâm đến tham số ``'lang_code'``
không nữa::

    from flask import Blueprint, g

    bp = Blueprint('frontend', __name__, url_prefix='/<lang_code>')

    @bp.url_defaults
    def add_language_code(endpoint, values):
        values.setdefault('lang_code', g.lang_code)

    @bp.url_value_preprocessor
    def pull_lang_code(endpoint, values):
        g.lang_code = values.pop('lang_code')

    @bp.route('/')
    def index():
        ...

    @bp.route('/about')
    def about():
        ...
