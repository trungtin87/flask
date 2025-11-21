Application Factories
=====================

Nếu bạn đã sử dụng các package và blueprint cho ứng dụng của mình
(:doc:`/blueprints`) thì có một vài cách thực sự hay để cải thiện hơn nữa
trải nghiệm. Một mẫu phổ biến là tạo đối tượng ứng dụng khi
blueprint được import. Nhưng nếu bạn di chuyển việc tạo đối tượng này
vào một hàm, bạn có thể tạo nhiều instance của ứng dụng này sau đó.

Vậy tại sao bạn lại muốn làm điều này?

1.  Kiểm thử (Testing). Bạn có thể có các instance của ứng dụng với các
    cài đặt khác nhau để kiểm thử mọi trường hợp.
2.  Nhiều instance. Hãy tưởng tượng bạn muốn chạy các phiên bản khác nhau của
    cùng một ứng dụng. Tất nhiên bạn có thể có nhiều instance với
    các cấu hình khác nhau được thiết lập trong máy chủ web của mình, nhưng nếu bạn sử dụng factory,
    bạn có thể có nhiều instance của cùng một ứng dụng chạy trong
    cùng một quy trình ứng dụng, điều này có thể rất tiện lợi.

Vậy bạn sẽ thực sự triển khai điều đó như thế nào?

Factory Cơ bản
--------------

Ý tưởng là thiết lập ứng dụng trong một hàm. Như thế này::

    def create_app(config_filename):
        app = Flask(__name__)
        app.config.from_pyfile(config_filename)

        from yourapplication.model import db
        db.init_app(app)

        from yourapplication.views.admin import admin
        from yourapplication.views.frontend import frontend
        app.register_blueprint(admin)
        app.register_blueprint(frontend)

        return app

Nhược điểm là bạn không thể sử dụng đối tượng ứng dụng trong các blueprint
tại thời điểm import. Tuy nhiên, bạn có thể sử dụng nó từ bên trong một request. Làm thế nào để bạn
truy cập vào ứng dụng với cấu hình? Sử dụng
:data:`~flask.current_app`::

    from flask import current_app, Blueprint, render_template
    admin = Blueprint('admin', __name__, url_prefix='/admin')

    @admin.route('/')
    def index():
        return render_template(current_app.config['INDEX_TEMPLATE'])

Ở đây chúng ta tra cứu tên của một template trong cấu hình.

Factory & Extension
-------------------

Tốt hơn là nên tạo các extension và app factory của bạn sao cho
đối tượng extension không bị ràng buộc ban đầu với ứng dụng.

Sử dụng `Flask-SQLAlchemy <https://flask-sqlalchemy.palletsprojects.com/>`_,
làm ví dụ, bạn không nên làm điều gì đó theo những dòng này::

    def create_app(config_filename):
        app = Flask(__name__)
        app.config.from_pyfile(config_filename)

        db = SQLAlchemy(app)

Mà thay vào đó, trong model.py (hoặc tương đương)::

    db = SQLAlchemy()

và trong application.py (hoặc tương đương) của bạn::

    def create_app(config_filename):
        app = Flask(__name__)
        app.config.from_pyfile(config_filename)

        from yourapplication.model import db
        db.init_app(app)

Sử dụng mẫu thiết kế này, không có trạng thái cụ thể của ứng dụng nào được lưu trữ trên
đối tượng extension, vì vậy một đối tượng extension có thể được sử dụng cho nhiều ứng dụng.
Để biết thêm thông tin về thiết kế của các extension, hãy tham khảo :doc:`/extensiondev`.

Sử dụng Ứng dụng
----------------

Để chạy một ứng dụng như vậy, bạn có thể sử dụng lệnh :command:`flask`:

.. code-block:: text

    $ flask --app hello run

Flask sẽ tự động phát hiện factory nếu nó được đặt tên là
``create_app`` hoặc ``make_app`` trong ``hello``. Bạn cũng có thể truyền các đối số
cho factory như thế này:

.. code-block:: text

    $ flask --app 'hello:create_app(local_auth=True)' run

Sau đó factory ``create_app`` trong ``hello`` được gọi với đối số
từ khóa ``local_auth=True``. Xem :doc:`/cli` để biết thêm chi tiết.

Cải tiến Factory
----------------

Hàm factory ở trên không thông minh lắm, nhưng bạn có thể cải thiện nó.
Các thay đổi sau đây rất đơn giản để thực hiện:

1.  Làm cho nó có thể truyền vào các giá trị cấu hình cho unit test để
    bạn không phải tạo các file cấu hình trên hệ thống file.
2.  Gọi một hàm từ một blueprint khi ứng dụng đang thiết lập để
    bạn có một nơi để sửa đổi các thuộc tính của ứng dụng (như
    hook vào các trình xử lý trước/sau request, v.v.)
3.  Thêm vào các middleware WSGI khi ứng dụng đang được tạo nếu cần thiết.
