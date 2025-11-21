Phát triển Extension Flask
==========================

Extension là các gói bổ sung tính năng cho một ứng dụng Flask. Mặc dù `PyPI`_ có rất nhiều extension Flask, bạn có thể không tìm thấy một extension phù hợp với nhu cầu của mình. Khi đó, bạn có thể tự tạo một extension và công bố để người khác cũng có thể sử dụng.

Hướng dẫn này sẽ chỉ cho bạn cách tạo một extension Flask, cũng như một số mẫu và yêu cầu phổ biến. Vì extension có thể làm bất cứ điều gì, hướng dẫn này không thể bao quát mọi khả năng.

Cách tốt nhất để học về các extension là xem cách các extension bạn đang dùng được viết, và thảo luận với cộng đồng. Bạn có thể thảo luận ý tưởng thiết kế với mọi người trên `Discord Chat`_ hoặc `GitHub Discussions`_.

Các extension tốt thường có những mẫu chung, để bất kỳ ai đã quen với một extension nào đó cũng sẽ không cảm thấy lạc lõng khi dùng một extension khác. Điều này chỉ có thể đạt được nếu việc cộng tác diễn ra sớm.


Đặt tên
--------

Một extension Flask thường có từ ``flask`` ở đầu hoặc cuối tên, hoặc cả hai. Nếu nó bao bọc một thư viện khác, nên bao gồm tên thư viện trong tên extension. Điều này giúp dễ tìm kiếm và làm rõ mục đích.

Một khuyến nghị chung về đặt tên Python là tên cài đặt (install name) trên PyPI và tên import trong mã nên liên quan với nhau. Tên import thường dùng chữ thường và gạch dưới (``_``). Tên cài đặt có thể dùng chữ thường hoặc chữ hoa, các từ cách nhau bằng dấu gạch ngang (``-``). Nếu nó bao bọc một thư viện khác, nên dùng cùng kiểu chữ như thư viện đó.

Một số ví dụ:

- ``Flask-Name`` được import là ``flask_name``
- ``flask-name-lower`` được import là ``flask_name_lower``
- ``Flask-ComboName`` được import là ``flask_comboname``
- ``Name-Flask`` được import là ``name_flask``


Lớp Extension và Khởi tạo
--------------------------

Mọi extension đều cần một điểm vào để khởi tạo extension với ứng dụng. Mẫu phổ biến nhất là tạo một lớp đại diện cho cấu hình và hành vi của extension, và cung cấp một phương thức ``init_app`` để áp dụng instance của extension vào một instance của Flask.

.. code-block:: python

    class HelloExtension:
        def __init__(self, app=None):
            if app is not None:
                self.init_app(app)

        def init_app(self, app):
            app.before_request(...)

Quan trọng là không lưu trữ ``app`` trong extension (không làm ``self.app = app``). Thời điểm duy nhất extension có thể truy cập trực tiếp vào app là trong ``init_app``; các phần còn lại nên dùng ``flask.current_app``.

Điều này cho phép extension hỗ trợ pattern factory của ứng dụng, tránh vòng lặp import khi import instance của extension ở các module khác, và giúp test với các cấu hình khác nhau dễ dàng hơn.

.. code-block:: python

    hello = HelloExtension()

    def create_app():
        app = Flask(__name__)
        hello.init_app(app)
        return app

Như trên, instance ``hello`` tồn tại độc lập với ứng dụng. Điều này cho phép các module khác trong dự án của bạn có thể ``from project import hello`` và sử dụng extension trong các blueprint trước khi app được tạo.

``Flask.extensions`` là một dict có thể dùng để lưu trữ tham chiếu tới extension trên ứng dụng, hoặc bất kỳ trạng thái nào khác liên quan đến ứng dụng. Hãy nhớ rằng dict này là một không gian tên chung, vì vậy nên dùng một tên duy nhất cho extension, ví dụ tên extension không có tiền tố ``flask``.


Thêm hành vi
------------

Có nhiều cách để một extension thêm hành vi. Các phương thức thiết lập có sẵn trên đối tượng ``Flask`` có thể được dùng trong ``init_app``.

Một mẫu phổ biến là dùng ``app.before_request`` để khởi tạo một số dữ liệu hoặc kết nối ở đầu mỗi request, và ``app.teardown_request`` để dọn dẹp sau khi request kết thúc. Dữ liệu này có thể được lưu trên ``flask.g``.

Một cách tiếp cận lười hơn là cung cấp một phương thức khởi tạo và cache dữ liệu hoặc kết nối. Ví dụ, một ``ext.get_db`` có thể tạo kết nối cơ sở dữ liệu lần đầu được gọi, để các view không dùng DB không tạo kết nối.

Ngoài việc thực hiện một số công việc trước và sau mỗi view, extension có thể muốn thêm một số view riêng. Trong trường hợp này, bạn có thể định nghĩa một ``Blueprint`` rồi gọi ``app.register_blueprint`` trong ``init_app`` để thêm blueprint vào app.


Kỹ thuật cấu hình
-----------------

Extension có thể có nhiều cấp độ và nguồn cấu hình. Bạn nên cân nhắc phần nào của extension thuộc về mỗi cấp độ.

- Cấu hình cho mỗi instance của ứng dụng, thông qua ``app.config``. Đây là cấu hình có thể thay đổi cho mỗi deployment.
- Cấu hình cho mỗi instance của extension, thông qua các đối số ``__init__``. Thông thường ảnh hưởng đến cách extension hoạt động và không nên thay đổi cho mỗi deployment.
- Cấu hình cho mỗi instance của extension, thông qua các thuộc tính instance và phương thức decorator.
- Cấu hình toàn cục qua thuộc tính lớp. Thay đổi một thuộc tính lớp như ``Ext.connection_class`` có thể tùy chỉnh hành vi mặc định mà không cần subclass.
- Kế thừa lớp và ghi đè phương thức, thuộc tính. Đây là công cụ mạnh mẽ cho việc tùy chỉnh nâng cao.

Flask tự sử dụng tất cả những kỹ thuật này. Bạn quyết định cấu hình nào phù hợp cho extension dựa trên nhu cầu và những gì bạn muốn hỗ trợ.


Dữ liệu trong một request
--------------------------

Khi viết một ứng dụng Flask, đối tượng ``flask.g`` được dùng để lưu thông tin trong suốt một request. Ví dụ, tutorial ``database`` lưu kết nối SQLite vào ``g.db``. Extension cũng có thể dùng ``g`` nhưng cần cẩn thận. Vì ``g`` là một namespace toàn cục, extension phải dùng các tên duy nhất không gây xung đột với dữ liệu người dùng. Ví dụ, dùng tên extension làm tiền tố, hoặc dùng một namespace.

.. code-block:: python

    # một tiền tố nội bộ với tên extension
    g._hello_user_id = 2

    # hoặc một namespace
    from types import SimpleNamespace
    g._hello = SimpleNamespace()
    g._hello.user_id = 2

Dữ liệu trong ``g`` tồn tại trong một context ứng dụng. Context này hoạt động trong một request, lệnh CLI, hoặc khối ``with app.app_context()``. Nếu bạn lưu thứ gì đó cần được đóng lại, hãy dùng ``app.teardown_appcontext`` để đảm bảo nó được đóng khi context kết thúc. Nếu chỉ cần tồn tại trong một request, hãy dùng ``app.teardown_request``.


Views và Models
---------------

Views của extension có thể muốn tương tác với các model trong database, hoặc các extension hoặc dữ liệu khác. Ví dụ, một extension ``Flask-SimpleBlog`` có thể làm việc với Flask-SQLAlchemy để cung cấp model ``Post`` và các view để tạo và đọc bài viết.

Model ``Post`` cần kế thừa ``db.Model`` của Flask-SQLAlchemy, nhưng chỉ có sẵn khi bạn đã tạo một instance của extension, không phải khi định nghĩa view. Vì vậy, view cần cách truy cập model sau khi model được tạo.

Một phương pháp là tạo model trong ``__init__`` và sau đó truyền model cho view khi tạo view.

.. code-block:: python

    class PostAPI(MethodView):
        def __init__(self, model):
            self.model = model

        def get(self, id):
            post = self.model.query.get(id)
            return jsonify(post.to_dict())

    class BlogExtension:
        def __init__(self, db):
            class Post(db.Model):
                id = db.Column(db.Integer, primary_key=True)
                title = db.Column(db.String, nullable=False)
            self.post_model = Post

        def init_app(self, app):
            api_view = PostAPI.as_view(model=self.post_model)
            app.add_url_rule('/posts/<int:id>', view_func=api_view)

    db = SQLAlchemy()
    blog = BlogExtension(db)
    db.init_app(app)
    blog.init_app(app)

Một kỹ thuật khác là định nghĩa một subclass của ``Post`` mà người dùng có thể tùy chỉnh, và sau đó gán nó cho ``blog.post_model``.

Như bạn thấy, việc này có thể phức tạp. Không có giải pháp hoàn hảo cho mọi trường hợp, nhưng các chiến lược trên thường đủ cho hầu hết các extension.

Bạn luôn có thể hỏi trên `Discord Chat`_ hoặc `GitHub Discussions`_ nếu cần trợ giúp thiết kế.


Hướng dẫn Extension Đề xuất
----------------------------

Flask từng có khái niệm "approved extensions", nơi các maintainer của Flask đánh giá chất lượng, hỗ trợ và khả năng tương thích của extension trước khi liệt kê. Dù danh sách này đã khó duy trì, các hướng dẫn vẫn hữu ích cho các extension hiện nay, giúp hệ sinh thái Flask duy trì tính nhất quán và tương thích.

1.  Một extension cần có maintainer. Khi maintainer muốn rời bỏ dự án, cần tìm maintainer mới và chuyển quyền truy cập repo, PyPI, tài liệu, v.v. Tổ chức `Pallets-Eco`_ trên GitHub cho phép bảo trì cộng đồng với sự giám sát của các maintainer Pallets.
2.  Quy tắc đặt tên là *Flask-ExtensionName* hoặc *ExtensionName-Flask*. Nó phải cung cấp đúng một package hoặc module tên ``flask_extension_name``.
3.  Extension phải sử dụng giấy phép nguồn mở. Cộng đồng Python thường ưu tiên BSD hoặc MIT. Nó phải công khai và có sẵn.
4.  API của extension phải có các đặc điểm:
    - Hỗ trợ nhiều ứng dụng chạy trong cùng một process Python. Dùng ``current_app`` thay vì ``self.app``, lưu cấu hình và trạng thái cho mỗi instance.
    - Có thể dùng pattern factory để tạo ứng dụng. Dùng pattern ``ext.init_app()``.
5.  Từ một bản clone của repo, extension và các phụ thuộc của nó phải có thể cài đặt ở chế độ editable bằng ``pip install -e .``.
6.  Phải có các test có thể chạy bằng công cụ chung như ``tox -e py``, ``nox -s test`` hoặc ``pytest``. Nếu không dùng ``tox``, các phụ thuộc test phải được chỉ định trong file requirements. Các test phải nằm trong distribution sdist.
7.  Một liên kết tới tài liệu hoặc website dự án phải có trong metadata PyPI hoặc README. Tài liệu nên dùng theme Flask từ `Official Pallets Themes`_.
8.  Các phụ thuộc của extension không nên có upper bounds hoặc giả định phiên bản cụ thể, nhưng nên có lower bounds để chỉ ra mức hỗ trợ tối thiểu, ví dụ ``sqlalchemy>=1.4``.
9.  Cần chỉ định các phiên bản Python được hỗ trợ bằng ``python_requires=">=3.x"``. Chính sách của Pallets là hỗ trợ mọi phiên bản Python chưa qua 6 tháng kể từ ngày kết thúc vòng đời (EOL). Xem lịch EOL của Python.

.. _PyPI: https://pypi.org/search/?c=Framework%3A%3A+Flask
.. _Discord Chat: https://discord.gg/pallets
.. _GitHub Discussions: https://github.com/pallets/flask/discussions
.. _Official Pallets Themes: https://pypi.org/project/Pallets-Sphinx-Themes/
.. _Pallets-Eco: https://github.com/pallets-eco
.. _EOL calendar: https://devguide.python.org/versions/
