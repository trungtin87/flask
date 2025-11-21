Ứng dụng Mô-đun với Blueprints
==============================

.. currentmodule:: flask

.. versionadded:: 0.7

Flask sử dụng khái niệm *blueprints* để tạo các thành phần ứng dụng và
hỗ trợ các mẫu phổ biến trong một ứng dụng hoặc giữa các ứng dụng.
Blueprints có thể đơn giản hóa đáng kể cách hoạt động của các ứng dụng lớn và cung cấp một
phương tiện trung tâm cho các tiện ích mở rộng Flask đăng ký các hoạt động trên ứng dụng.
Một đối tượng :class:`Blueprint` hoạt động tương tự như một đối tượng ứng dụng :class:`Flask`,
nhưng nó không thực sự là một ứng dụng. Thay vào đó nó là một
*bản thiết kế* (blueprint) về cách xây dựng hoặc mở rộng một ứng dụng.

Tại sao lại là Blueprints?
--------------------------

Blueprints trong Flask được dành cho các trường hợp sau:

* Phân tách một ứng dụng thành một tập hợp các blueprints. Điều này là lý tưởng cho
  các ứng dụng lớn hơn; một dự án có thể khởi tạo một đối tượng ứng dụng,
  khởi tạo một số tiện ích mở rộng, và đăng ký một tập hợp các blueprints.
* Đăng ký một blueprint trên một ứng dụng tại một tiền tố URL và/hoặc tên miền phụ (subdomain).
  Các tham số trong tiền tố URL/tên miền phụ trở thành các đối số view chung
  (với các giá trị mặc định) trên tất cả các hàm view trong blueprint.
* Đăng ký một blueprint nhiều lần trên một ứng dụng với các quy tắc URL khác nhau.
* Cung cấp các bộ lọc template, file tĩnh, template, và các tiện ích khác
  thông qua blueprints. Một blueprint không nhất thiết phải triển khai các ứng dụng
  hoặc hàm view.
* Đăng ký một blueprint trên một ứng dụng cho bất kỳ trường hợp nào trong số này khi
  khởi tạo một tiện ích mở rộng Flask.

Một blueprint trong Flask không phải là một ứng dụng có thể cắm vào (pluggable app) vì nó không thực sự là một
ứng dụng -- nó là một tập hợp các hoạt động có thể được đăng ký trên một
ứng dụng, thậm chí nhiều lần. Tại sao không có nhiều đối tượng ứng dụng?
Bạn có thể làm điều đó (xem :doc:`/patterns/appdispatch`), nhưng các
ứng dụng của bạn sẽ có cấu hình riêng biệt và sẽ được quản lý ở lớp WSGI.

Blueprints thay vào đó cung cấp sự phân tách ở cấp độ Flask, chia sẻ
cấu hình ứng dụng, và có thể thay đổi một đối tượng ứng dụng khi cần thiết với
việc được đăng ký. Nhược điểm là bạn không thể hủy đăng ký một blueprint
khi một ứng dụng đã được tạo mà không phải hủy toàn bộ
đối tượng ứng dụng.

Khái niệm về Blueprints
-----------------------

Khái niệm cơ bản của blueprints là chúng ghi lại các hoạt động để thực thi
khi được đăng ký trên một ứng dụng. Flask liên kết các hàm view với
blueprints khi điều phối các request và tạo URL từ một endpoint
đến endpoint khác.

Blueprint Đầu tiên của Tôi
--------------------------

Đây là những gì một blueprint rất cơ bản trông như thế nào. Trong trường hợp này chúng ta muốn
triển khai một blueprint thực hiện việc render đơn giản các template tĩnh::

    from flask import Blueprint, render_template, abort
    from jinja2 import TemplateNotFound

    simple_page = Blueprint('simple_page', __name__,
                            template_folder='templates')

    @simple_page.route('/', defaults={'page': 'index'})
    @simple_page.route('/<page>')
    def show(page):
        try:
            return render_template(f'pages/{page}.html')
        except TemplateNotFound:
            abort(404)

Khi bạn liên kết một hàm với sự trợ giúp của decorator ``@simple_page.route``,
blueprint sẽ ghi lại ý định đăng ký hàm ``show`` trên ứng dụng khi nó được đăng ký sau này.
Ngoài ra nó sẽ thêm tiền tố vào endpoint của hàm với
tên của blueprint đã được đưa cho hàm tạo :class:`Blueprint`
(trong trường hợp này cũng là ``simple_page``). Tên của blueprint
không sửa đổi URL, chỉ endpoint.

Đăng ký Blueprints
------------------

Vậy làm thế nào để bạn đăng ký blueprint đó? Như thế này::

    from flask import Flask
    from yourapplication.simple_page import simple_page

    app = Flask(__name__)
    app.register_blueprint(simple_page)

Nếu bạn kiểm tra các quy tắc đã đăng ký trên ứng dụng, bạn sẽ tìm thấy
những cái này::

    >>> app.url_map
    Map([<Rule '/static/<filename>' (HEAD, OPTIONS, GET) -> static>,
     <Rule '/<page>' (HEAD, OPTIONS, GET) -> simple_page.show>,
     <Rule '/' (HEAD, OPTIONS, GET) -> simple_page.show>])

Cái đầu tiên rõ ràng là từ chính ứng dụng cho các file tĩnh.
Hai cái còn lại là cho hàm `show` của blueprint ``simple_page``.
Như bạn có thể thấy, chúng cũng được thêm tiền tố với tên của
blueprint và được phân tách bằng một dấu chấm (``.``).

Tuy nhiên Blueprints cũng có thể được gắn tại các vị trí khác nhau::

    app.register_blueprint(simple_page, url_prefix='/pages')

Và chắc chắn rồi, đây là các quy tắc được tạo ra::

    >>> app.url_map
    Map([<Rule '/static/<filename>' (HEAD, OPTIONS, GET) -> static>,
     <Rule '/pages/<page>' (HEAD, OPTIONS, GET) -> simple_page.show>,
     <Rule '/pages/' (HEAD, OPTIONS, GET) -> simple_page.show>])

Trên hết bạn có thể đăng ký blueprints nhiều lần mặc dù không phải mọi
blueprint đều có thể phản hồi đúng cách với điều đó. Thực tế nó phụ thuộc vào cách
blueprint được triển khai nếu nó có thể được gắn nhiều hơn một lần.

Lồng Blueprints (Nesting Blueprints)
------------------------------------

Có thể đăng ký một blueprint trên một blueprint khác.

.. code-block:: python

    parent = Blueprint('parent', __name__, url_prefix='/parent')
    child = Blueprint('child', __name__, url_prefix='/child')
    parent.register_blueprint(child)
    app.register_blueprint(parent)

Blueprint con sẽ nhận được tên của cha làm tiền tố cho tên của nó,
và các URL con sẽ được thêm tiền tố với tiền tố URL của cha.

.. code-block:: python

    url_for('parent.child.create')
    /parent/child/create

Ngoài ra blueprint con sẽ nhận được tên miền phụ (subdomain) của cha,
với tên miền phụ của chúng làm tiền tố nếu có, tức là

.. code-block:: python

    parent = Blueprint('parent', __name__, subdomain='parent')
    child = Blueprint('child', __name__, subdomain='child')
    parent.register_blueprint(child)
    app.register_blueprint(parent)

    url_for('parent.child.create', _external=True)
    "child.parent.domain.tld"

Các hàm trước request (before request), v.v. cụ thể cho blueprint được đăng ký với
cha sẽ kích hoạt cho con. Nếu một con không có trình xử lý lỗi
có thể xử lý một ngoại lệ nhất định, trình xử lý của cha sẽ được thử.


Tài nguyên Blueprint
--------------------

Blueprints cũng có thể cung cấp tài nguyên. Đôi khi bạn có thể muốn
giới thiệu một blueprint chỉ cho các tài nguyên mà nó cung cấp.

Thư mục Tài nguyên Blueprint
````````````````````````````

Giống như các ứng dụng thông thường, blueprints được coi là được chứa
trong một thư mục. Mặc dù nhiều blueprints có thể bắt nguồn từ cùng một thư mục,
điều đó không nhất thiết phải là trường hợp và thường không được khuyến nghị.

Thư mục được suy ra từ đối số thứ hai đến :class:`Blueprint` thường
là `__name__`. Đối số này chỉ định module hoặc package Python logic nào
tương ứng với blueprint. Nếu nó trỏ đến một package Python thực tế
thì package đó (là một thư mục trên hệ thống tệp) là
thư mục tài nguyên. Nếu nó là một module, package mà module được chứa trong đó
sẽ là thư mục tài nguyên. Bạn có thể truy cập thuộc tính
:attr:`Blueprint.root_path` để xem thư mục tài nguyên là gì::

    >>> simple_page.root_path
    '/Users/username/TestProject/yourapplication'

Để mở nhanh các nguồn từ thư mục này bạn có thể sử dụng hàm
:meth:`~Blueprint.open_resource`::

    with simple_page.open_resource('static/style.css') as f:
        code = f.read()

File Tĩnh
`````````

Một blueprint có thể hiển thị một thư mục với các file tĩnh bằng cách cung cấp đường dẫn
đến thư mục trên hệ thống tệp với đối số ``static_folder``.
Nó là một đường dẫn tuyệt đối hoặc tương đối đến vị trí của blueprint::

    admin = Blueprint('admin', __name__, static_folder='static')

Theo mặc định phần ngoài cùng bên phải của đường dẫn là nơi nó được hiển thị trên
web. Điều này có thể được thay đổi với đối số ``static_url_path``. Bởi vì
thư mục được gọi là ``static`` ở đây nó sẽ có sẵn tại
``url_prefix`` của blueprint + ``/static``. Nếu blueprint
có tiền tố ``/admin``, URL tĩnh sẽ là ``/admin/static``.

Endpoint được đặt tên là ``blueprint_name.static``. Bạn có thể tạo URL
đến nó với :func:`url_for` giống như bạn làm với thư mục tĩnh của
ứng dụng::

    url_for('admin.static', filename='style.css')

Tuy nhiên, nếu blueprint không có ``url_prefix``, thì không thể
truy cập thư mục tĩnh của blueprint. Điều này là do
URL sẽ là ``/static`` trong trường hợp này, và route ``/static`` của ứng dụng
được ưu tiên. Không giống như các thư mục template, các thư mục tĩnh của blueprint
không được tìm kiếm nếu file không tồn tại trong thư mục tĩnh của ứng dụng.

Templates
`````````

Nếu bạn muốn blueprint hiển thị các template bạn có thể làm điều đó bằng cách cung cấp
tham số `template_folder` cho hàm tạo :class:`Blueprint`::

    admin = Blueprint('admin', __name__, template_folder='templates')

Đối với các file tĩnh, đường dẫn có thể là tuyệt đối hoặc tương đối đến thư mục
tài nguyên của blueprint.

Thư mục template được thêm vào đường dẫn tìm kiếm của các template nhưng với độ ưu tiên thấp hơn
so với thư mục template của ứng dụng thực tế. Bằng cách đó bạn có thể
dễ dàng ghi đè các template mà một blueprint cung cấp trong ứng dụng thực tế.
Điều này cũng có nghĩa là nếu bạn không muốn một template blueprint bị vô tình
ghi đè, hãy đảm bảo rằng không có template blueprint hoặc ứng dụng thực tế nào khác
có cùng đường dẫn tương đối. Khi nhiều blueprints cung cấp cùng một đường dẫn template
tương đối, blueprint đầu tiên được đăng ký sẽ được ưu tiên hơn các blueprint khác.


Vì vậy nếu bạn có một blueprint trong thư mục ``yourapplication/admin`` và bạn
muốn render template ``'admin/index.html'`` và bạn đã cung cấp
``templates`` làm `template_folder` bạn sẽ phải tạo một file như
thế này: :file:`yourapplication/admin/templates/admin/index.html`. Lý do
cho thư mục ``admin`` thêm là để tránh template của chúng ta bị ghi đè
bởi một template có tên ``index.html`` trong thư mục template của ứng dụng thực tế.

Để nhắc lại điều này: nếu bạn có một blueprint tên là ``admin`` và bạn
muốn render một template gọi là :file:`index.html` cụ thể cho blueprint này,
ý tưởng tốt nhất là bố trí các template của bạn như thế này::

    yourpackage/
        blueprints/
            admin/
                templates/
                    admin/
                        index.html
                __init__.py

Và sau đó khi bạn muốn render template, sử dụng :file:`admin/index.html` làm
tên để tra cứu template. Nếu bạn gặp vấn đề khi tải
đúng template hãy bật biến cấu hình ``EXPLAIN_TEMPLATE_LOADING``
sẽ hướng dẫn Flask in ra các bước nó trải qua
để xác định vị trí các template trên mỗi cuộc gọi ``render_template``.

Xây dựng URL
------------

Nếu bạn muốn liên kết từ trang này sang trang khác bạn có thể sử dụng
hàm :func:`url_for` giống như bạn thường làm chỉ là bạn
thêm tiền tố vào endpoint URL với tên của blueprint và một dấu chấm (``.``)::

    url_for('admin.index')

Ngoài ra nếu bạn đang ở trong một hàm view của một blueprint hoặc một template được render
và bạn muốn liên kết đến một endpoint khác của cùng một blueprint,
bạn có thể sử dụng các chuyển hướng tương đối bằng cách chỉ thêm tiền tố vào endpoint với một dấu chấm::

    url_for('.index')

Điều này sẽ liên kết đến ``admin.index`` chẳng hạn trong trường hợp request hiện tại
được điều phối đến bất kỳ endpoint blueprint admin nào khác.


Trình xử lý Lỗi Blueprint
-------------------------

Blueprints hỗ trợ decorator ``errorhandler`` giống như đối tượng ứng dụng :class:`Flask`,
vì vậy thật dễ dàng để tạo các trang lỗi tùy chỉnh cụ thể cho Blueprint.

Dưới đây là một ví dụ cho ngoại lệ "404 Page Not Found"::

    @simple_page.errorhandler(404)
    def page_not_found(e):
        return render_template('pages/404.html')

Hầu hết các trình xử lý lỗi sẽ chỉ hoạt động như mong đợi; tuy nhiên, có một lưu ý
liên quan đến các trình xử lý cho các ngoại lệ 404 và 405. Các trình xử lý lỗi này chỉ được
gọi từ một câu lệnh ``raise`` thích hợp hoặc một cuộc gọi đến ``abort`` trong một
hàm view khác của blueprint; chúng không được gọi bởi, ví dụ, một truy cập URL không hợp lệ.
Điều này là do blueprint không "sở hữu" một không gian URL nhất định, vì vậy
thể hiện ứng dụng không có cách nào biết trình xử lý lỗi blueprint nào nó
nên chạy nếu được cung cấp một URL không hợp lệ. Nếu bạn muốn thực thi các chiến lược
xử lý khác nhau cho các lỗi này dựa trên tiền tố URL, chúng có thể được định nghĩa
ở cấp ứng dụng bằng cách sử dụng đối tượng proxy ``request``::

    @app.errorhandler(404)
    @app.errorhandler(405)
    def _handle_api_error(ex):
        if request.path.startswith('/api/'):
            return jsonify(error=str(ex)), ex.code
        else:
            return ex

Xem :doc:`/errorhandling`.
