Lazy Loading Views
==================

Flask thường được sử dụng với các decorator. Decorator rất đơn giản và bạn
có URL ngay bên cạnh hàm được gọi cho URL cụ thể đó. Tuy nhiên có một
nhược điểm đối với cách tiếp cận này: nó có nghĩa là tất cả mã của bạn
sử dụng decorator phải được import trước hoặc Flask sẽ không bao giờ
thực sự tìm thấy hàm của bạn.

Điều này có thể là một vấn đề nếu ứng dụng của bạn phải import nhanh. Nó có thể
phải làm điều đó trên các hệ thống như Google App Engine hoặc các hệ thống khác. Vì vậy
nếu bạn đột nhiên nhận thấy rằng ứng dụng của bạn vượt quá cách tiếp cận này, bạn
có thể quay lại với một URL mapping tập trung.

Hệ thống cho phép có một URL map trung tâm là hàm
:meth:`~flask.Flask.add_url_rule`. Thay vì sử dụng decorator,
bạn có một file thiết lập ứng dụng với tất cả các URL.

Chuyển đổi sang URL Map Tập trung
---------------------------------

Hãy tưởng tượng ứng dụng hiện tại trông giống như thế này::

    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def index():
        pass

    @app.route('/user/<username>')
    def user(username):
        pass

Sau đó, với cách tiếp cận tập trung, bạn sẽ có một file với các view
(:file:`views.py`) nhưng không có bất kỳ decorator nào::

    def index():
        pass

    def user(username):
        pass

Và sau đó một file thiết lập một ứng dụng ánh xạ các hàm đến
URL::

    from flask import Flask
    from yourapplication import views
    app = Flask(__name__)
    app.add_url_rule('/', view_func=views.index)
    app.add_url_rule('/user/<username>', view_func=views.user)

Loading Muộn
------------

Cho đến nay chúng ta chỉ tách các view và routing, nhưng module vẫn
được load trước. Mẹo là thực sự load view function khi cần thiết.
Điều này có thể được thực hiện với một helper class hoạt động giống như một
hàm nhưng bên trong import hàm thực sự khi sử dụng lần đầu tiên::

    from werkzeug.utils import import_string, cached_property

    class LazyView(object):

        def __init__(self, import_name):
            self.__module__, self.__name__ = import_name.rsplit('.', 1)
            self.import_name = import_name

        @cached_property
        def view(self):
            return import_string(self.import_name)

        def __call__(self, *args, **kwargs):
            return self.view(*args, **kwargs)

Điều quan trọng ở đây là `__module__` và `__name__` được đặt đúng cách.
Điều này được Flask sử dụng nội bộ để tìm ra cách đặt tên cho
các URL rule trong trường hợp bạn không cung cấp tên cho rule.

Sau đó bạn có thể định nghĩa nơi trung tâm của mình để kết hợp các view như thế này::

    from flask import Flask
    from yourapplication.helpers import LazyView
    app = Flask(__name__)
    app.add_url_rule('/',
                     view_func=LazyView('yourapplication.views.index'))
    app.add_url_rule('/user/<username>',
                     view_func=LazyView('yourapplication.views.user'))

Bạn có thể tối ưu hóa thêm điều này về số lượng phím cần
viết bằng cách có một hàm gọi vào
:meth:`~flask.Flask.add_url_rule` bằng cách thêm tiền tố một chuỗi với tên dự án
và một dấu chấm, và bằng cách bao bọc `view_func` trong một `LazyView` khi cần thiết. ::

    def url(import_name, url_rules=[], **options):
        view = LazyView(f"yourapplication.{import_name}")
        for url_rule in url_rules:
            app.add_url_rule(url_rule, view_func=view, **options)

    # thêm một route duy nhất vào index view
    url('views.index', ['/'])

    # thêm hai route vào một function endpoint duy nhất
    url_rules = ['/user/','/user/<username>']
    url('views.user', url_rules)

Một điều cần lưu ý là các trình xử lý before và after request phải
ở trong một file được import trước để hoạt động đúng trên request
đầu tiên. Điều tương tự cũng áp dụng cho bất kỳ loại decorator còn lại nào.
