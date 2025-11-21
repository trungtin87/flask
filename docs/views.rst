Class-based Views
=================

.. currentmodule:: flask.views

Trang này giới thiệu việc sử dụng các lớp :class:`View` và :class:`MethodView`
để viết các view dựa trên lớp (class-based views).

Một class-based view là một lớp hoạt động như một hàm view. Bởi vì nó
là một lớp, các thể hiện khác nhau của lớp có thể được tạo ra với
các đối số khác nhau, để thay đổi hành vi của view. Điều này cũng được
biết đến như là các view chung (generic), có thể tái sử dụng, hoặc có thể cắm (pluggable).

Một ví dụ về nơi điều này hữu ích là định nghĩa một lớp tạo ra một
API dựa trên model cơ sở dữ liệu mà nó được khởi tạo cùng.

Để có hành vi API phức tạp hơn và tùy chỉnh, hãy xem xét các
tiện ích mở rộng API khác nhau cho Flask.


View Tái sử dụng Cơ bản
-----------------------

Hãy cùng đi qua một ví dụ chuyển đổi một hàm view thành một lớp
view. Chúng ta bắt đầu với một hàm view truy vấn một danh sách người dùng sau đó
render một template để hiển thị danh sách.

.. code-block:: python

    @app.route("/users/")
    def user_list():
        users = User.query.all()
        return render_template("users.html", users=users)

Điều này hoạt động cho model người dùng, nhưng giả sử bạn cũng có nhiều model hơn
cần các trang danh sách. Bạn sẽ cần viết một hàm view khác cho
mỗi model, mặc dù điều duy nhất thay đổi là model
và tên template.

Thay vào đó, bạn có thể viết một lớp con :class:`View` sẽ truy vấn một model
và render một template. Là bước đầu tiên, chúng ta sẽ chuyển đổi view thành một
lớp mà không có bất kỳ tùy chỉnh nào.

.. code-block:: python

    from flask.views import View

    class UserList(View):
        def dispatch_request(self):
            users = User.query.all()
            return render_template("users.html", objects=users)

    app.add_url_rule("/users/", view_func=UserList.as_view("user_list"))

Phương thức :meth:`View.dispatch_request` tương đương với hàm
view. Gọi phương thức :meth:`View.as_view` sẽ tạo ra một hàm
view có thể được đăng ký trên ứng dụng với phương thức
:meth:`~flask.Flask.add_url_rule` của nó. Đối số đầu tiên cho
``as_view`` là tên để sử dụng để tham chiếu đến view với
:func:`~flask.url_for`.

.. note::

    Bạn không thể decorate lớp với ``@app.route()`` theo cách bạn sẽ
    làm với một hàm view cơ bản.

Tiếp theo, chúng ta cần có thể đăng ký cùng một lớp view cho các model
và template khác nhau, để làm cho nó hữu ích hơn hàm ban đầu.
Lớp sẽ nhận hai đối số, model và template, và lưu trữ
chúng trên ``self``. Sau đó ``dispatch_request`` có thể tham chiếu những cái này thay vì
các giá trị được mã hóa cứng.

.. code-block:: python

    class ListView(View):
        def __init__(self, model, template):
            self.model = model
            self.template = template

        def dispatch_request(self):
            items = self.model.query.all()
            return render_template(self.template, items=items)

Hãy nhớ, chúng ta tạo hàm view với ``View.as_view()`` thay vì
tạo lớp trực tiếp. Bất kỳ đối số bổ sung nào được truyền cho ``as_view``
sau đó được truyền khi tạo lớp. Bây giờ chúng ta có thể đăng ký cùng một
view để xử lý nhiều model.

.. code-block:: python

    app.add_url_rule(
        "/users/",
        view_func=ListView.as_view("user_list", User, "users.html"),
    )
    app.add_url_rule(
        "/stories/",
        view_func=ListView.as_view("story_list", Story, "stories.html"),
    )


Biến URL
--------

Bất kỳ biến nào được bắt bởi URL đều được truyền dưới dạng đối số từ khóa cho
phương thức ``dispatch_request``, giống như chúng sẽ được truyền cho một hàm view
thông thường.

.. code-block:: python

    class DetailView(View):
        def __init__(self, model):
            self.model = model
            self.template = f"{model.__name__.lower()}/detail.html"

        def dispatch_request(self, id)
            item = self.model.query.get_or_404(id)
            return render_template(self.template, item=item)

    app.add_url_rule(
        "/users/<int:id>",
        view_func=DetailView.as_view("user_detail", User)
    )


Vòng đời View và ``self``
-------------------------

Theo mặc định, một thể hiện mới của lớp view được tạo mỗi khi một
request được xử lý. Điều này có nghĩa là an toàn để ghi dữ liệu khác vào
``self`` trong quá trình request, vì request tiếp theo sẽ không nhìn thấy nó,
không giống như các hình thức trạng thái toàn cục khác.

Tuy nhiên, nếu lớp view của bạn cần thực hiện nhiều khởi tạo phức tạp,
làm điều đó cho mỗi request là không cần thiết và có thể không hiệu quả. Để
tránh điều này, hãy đặt :attr:`View.init_every_request` thành ``False``, điều này sẽ
chỉ tạo một thể hiện của lớp và sử dụng nó cho mọi request. Trong
trường hợp này, ghi vào ``self`` là không an toàn. Nếu bạn cần lưu trữ dữ liệu
trong quá trình request, hãy sử dụng :data:`~flask.g` thay thế.

Trong ví dụ ``ListView``, không có gì ghi vào ``self`` trong quá trình
request, vì vậy hiệu quả hơn khi tạo một thể hiện duy nhất.

.. code-block:: python

    class ListView(View):
        init_every_request = False

        def __init__(self, model, template):
            self.model = model
            self.template = template

        def dispatch_request(self):
            items = self.model.query.all()
            return render_template(self.template, items=items)

Các thể hiện khác nhau vẫn sẽ được tạo cho mỗi cuộc gọi ``as_view``,
nhưng không phải cho mỗi request đến các view đó.


View Decorators
---------------

Bản thân lớp view không phải là hàm view. Các view decorator cần
được áp dụng cho hàm view được trả về bởi ``as_view``, không phải bản thân
lớp. Đặt :attr:`View.decorators` thành một danh sách các decorator để áp dụng.

.. code-block:: python

    class UserList(View):
        decorators = [cache(minutes=2), login_required]

    app.add_url_rule('/users/', view_func=UserList.as_view())

Nếu bạn không đặt ``decorators``, bạn có thể áp dụng chúng thủ công thay thế.
Điều này tương đương với:

.. code-block:: python

    view = UserList.as_view("users_list")
    view = cache(minutes=2)(view)
    view = login_required(view)
    app.add_url_rule('/users/', view_func=view)

Hãy nhớ rằng thứ tự rất quan trọng. Nếu bạn quen với kiểu ``@decorator``,
điều này tương đương với:

.. code-block:: python

    @app.route("/users/")
    @login_required
    @cache(minutes=2)
    def user_list():
        ...


Gợi ý Phương thức (Method Hints)
--------------------------------

Một mẫu phổ biến là đăng ký một view với ``methods=["GET", "POST"]``,
sau đó kiểm tra ``request.method == "POST"`` để quyết định làm gì. Đặt
:attr:`View.methods` tương đương với việc truyền danh sách các phương thức cho
``add_url_rule`` hoặc ``route``.

.. code-block:: python

    class MyView(View):
        methods = ["GET", "POST"]

        def dispatch_request(self):
            if request.method == "POST":
                ...
            ...

    app.add_url_rule('/my-view', view_func=MyView.as_view('my-view'))

Điều này tương đương với những điều sau, ngoại trừ các lớp con tiếp theo có thể
kế thừa hoặc thay đổi các phương thức.

.. code-block:: python

    app.add_url_rule(
        "/my-view",
        view_func=MyView.as_view("my-view"),
        methods=["GET", "POST"],
    )


Điều phối Phương thức và API
----------------------------

Đối với các API, có thể hữu ích khi sử dụng một hàm khác nhau cho mỗi phương thức
HTTP. :class:`MethodView` mở rộng :class:`View` cơ bản để điều phối
đến các phương thức khác nhau của lớp dựa trên phương thức request. Mỗi phương thức
HTTP ánh xạ tới một phương thức của lớp có cùng tên (chữ thường).

:class:`MethodView` tự động đặt :attr:`View.methods` dựa trên các
phương thức được định nghĩa bởi lớp. Nó thậm chí còn biết cách xử lý các lớp con
ghi đè hoặc định nghĩa các phương thức khác.

Chúng ta có thể tạo một lớp ``ItemAPI`` chung cung cấp các phương thức get (chi tiết),
patch (chỉnh sửa), và delete cho một model nhất định. Một ``GroupAPI`` có thể
cung cấp các phương thức get (danh sách) và post (tạo).

.. code-block:: python

    from flask.views import MethodView

    class ItemAPI(MethodView):
        init_every_request = False

        def __init__(self, model):
            self.model = model
            self.validator = generate_validator(model)

        def _get_item(self, id):
            return self.model.query.get_or_404(id)

        def get(self, id):
            item = self._get_item(id)
            return jsonify(item.to_json())

        def patch(self, id):
            item = self._get_item(id)
            errors = self.validator.validate(item, request.json)

            if errors:
                return jsonify(errors), 400

            item.update_from_json(request.json)
            db.session.commit()
            return jsonify(item.to_json())

        def delete(self, id):
            item = self._get_item(id)
            db.session.delete(item)
            db.session.commit()
            return "", 204

    class GroupAPI(MethodView):
        init_every_request = False

        def __init__(self, model):
            self.model = model
            self.validator = generate_validator(model, create=True)

        def get(self):
            items = self.model.query.all()
            return jsonify([item.to_json() for item in items])

        def post(self):
            errors = self.validator.validate(request.json)

            if errors:
                return jsonify(errors), 400

            db.session.add(self.model.from_json(request.json))
            db.session.commit()
            return jsonify(item.to_json())

    def register_api(app, model, name):
        item = ItemAPI.as_view(f"{name}-item", model)
        group = GroupAPI.as_view(f"{name}-group", model)
        app.add_url_rule(f"/{name}/<int:id>", view_func=item)
        app.add_url_rule(f"/{name}/", view_func=group)

    register_api(app, User, "users")
    register_api(app, Story, "stories")

Điều này tạo ra các view sau, một REST API tiêu chuẩn!

================ ========== ===================
URL               Method     Description
----------------- ---------- -------------------
``/users/``       ``GET``    Liệt kê tất cả người dùng
``/users/``       ``POST``   Tạo một người dùng mới
``/users/<id>``   ``GET``    Hiển thị một người dùng đơn lẻ
``/users/<id>``   ``PATCH``  Cập nhật một người dùng
``/users/<id>``   ``DELETE`` Xóa một người dùng
``/stories/``     ``GET``    Liệt kê tất cả câu chuyện
``/stories/``     ``POST``   Tạo một câu chuyện mới
``/stories/<id>`` ``GET``    Hiển thị một câu chuyện đơn lẻ
``/stories/<id>`` ``PATCH``  Cập nhật một câu chuyện
``/stories/<id>`` ``DELETE`` Xóa một câu chuyện
================ ========== ===================
