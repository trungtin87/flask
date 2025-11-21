Signals
=======

Signals là một cách nhẹ nhàng để thông báo cho các subscriber về các sự kiện nhất định trong
vòng đời của ứng dụng và mỗi request. Khi một sự kiện xảy ra, nó phát ra
signal, signal này gọi mỗi subscriber.

Signals được triển khai bởi thư viện `Blinker`_. Xem tài liệu của nó để biết thông tin
chi tiết. Flask cung cấp một số signals tích hợp. Các tiện ích mở rộng có thể cung cấp signals của riêng chúng.

Nhiều signals phản ánh các callback dựa trên decorator của Flask với tên tương tự. Ví dụ,
signal :data:`.request_started` tương tự như decorator :meth:`~.Flask.before_request`.
Ưu điểm của signals so với các trình xử lý là chúng có thể được đăng ký
tạm thời, và không thể ảnh hưởng trực tiếp đến ứng dụng. Điều này hữu ích cho việc kiểm thử,
số liệu (metrics), kiểm toán, và hơn thế nữa. Ví dụ, nếu bạn muốn biết những template nào đã được
render ở những phần nào của những request nào, có một signal sẽ thông báo cho bạn về
thông tin đó.


Signals Cốt lõi
---------------

Xem :ref:`core-signals-list` để biết danh sách tất cả các signals tích hợp. Trang :doc:`lifecycle`
cũng mô tả thứ tự mà signals và decorators thực thi.


Đăng ký Signals
---------------

Để đăng ký một signal, bạn có thể sử dụng phương thức
:meth:`~blinker.base.Signal.connect` của một signal. Đối số đầu tiên
là hàm sẽ được gọi khi signal được phát ra,
đối số thứ hai tùy chọn chỉ định một người gửi (sender). Để hủy đăng ký khỏi một
signal, bạn có thể sử dụng phương thức :meth:`~blinker.base.Signal.disconnect`.

Đối với tất cả các signals cốt lõi của Flask, người gửi là ứng dụng đã phát hành
signal. Khi bạn đăng ký một signal, hãy chắc chắn cũng cung cấp một người gửi
trừ khi bạn thực sự muốn lắng nghe signals từ tất cả các ứng dụng. Điều này
đặc biệt đúng nếu bạn đang phát triển một tiện ích mở rộng.

Ví dụ, đây là một trình quản lý ngữ cảnh (context manager) trợ giúp có thể được sử dụng trong một bài kiểm thử đơn vị
để xác định template nào đã được render và biến nào đã được truyền
cho template::

    from flask import template_rendered
    from contextlib import contextmanager

    @contextmanager
    def captured_templates(app):
        recorded = []
        def record(sender, template, context, **extra):
            recorded.append((template, context))
        template_rendered.connect(record, app)
        try:
            yield recorded
        finally:
            template_rendered.disconnect(record, app)

Bây giờ cái này có thể dễ dàng được ghép nối với một test client::

    with captured_templates(app) as templates:
        rv = app.test_client().get('/')
        assert rv.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'index.html'
        assert len(context['items']) == 10

Hãy chắc chắn đăng ký với một đối số ``**extra`` bổ sung để
các cuộc gọi của bạn không thất bại nếu Flask giới thiệu các đối số mới cho các signals.

Tất cả việc render template trong mã được phát hành bởi ứng dụng `app`
trong thân của khối ``with`` bây giờ sẽ được ghi lại trong biến `templates`.
Bất cứ khi nào một template được render, đối tượng template cũng như
context được thêm vào nó.

Ngoài ra còn có một phương thức trợ giúp thuận tiện
(:meth:`~blinker.base.Signal.connected_to`) cho phép bạn
tạm thời đăng ký một hàm vào một signal với một trình quản lý ngữ cảnh của
riêng nó. Bởi vì giá trị trả về của trình quản lý ngữ cảnh không thể được
chỉ định theo cách đó, bạn phải truyền danh sách vào như một đối số::

    from flask import template_rendered

    def captured_templates(app, recorded, **extra):
        def record(sender, template, context):
            recorded.append((template, context))
        return template_rendered.connected_to(record, app)

Ví dụ trên sau đó sẽ trông như thế này::

    templates = []
    with captured_templates(app, templates, **extra):
        ...
        template, context = templates[0]

Tạo Signals
-----------

Nếu bạn muốn sử dụng signals trong ứng dụng của riêng bạn, bạn có thể sử dụng
thư viện blinker trực tiếp. Trường hợp sử dụng phổ biến nhất là các signals được đặt tên trong một
:class:`~blinker.base.Namespace` tùy chỉnh. Đây là những gì được khuyến nghị
hầu hết thời gian::

    from blinker import Namespace
    my_signals = Namespace()

Bây giờ bạn có thể tạo các signals mới như thế này::

    model_saved = my_signals.signal('model-saved')

Tên cho signal ở đây làm cho nó duy nhất và cũng đơn giản hóa
việc gỡ lỗi. Bạn có thể truy cập tên của signal với thuộc tính
:attr:`~blinker.base.NamedSignal.name`.

.. _signals-sending:

Gửi Signals
-----------

Nếu bạn muốn phát ra một signal, bạn có thể làm như vậy bằng cách gọi phương thức
:meth:`~blinker.base.Signal.send`. Nó chấp nhận một người gửi làm đối số đầu tiên
và tùy chọn một số đối số từ khóa được chuyển tiếp đến các
subscriber của signal::

    class Model(object):
        ...

        def save(self):
            model_saved.send(self)

Cố gắng luôn chọn một người gửi tốt. Nếu bạn có một lớp đang phát ra một
signal, hãy truyền ``self`` làm người gửi. Nếu bạn đang phát ra một signal từ một hàm
ngẫu nhiên, bạn có thể truyền ``current_app._get_current_object()`` làm người gửi.

.. admonition:: Truyền Proxy làm Người gửi

   Đừng bao giờ truyền :data:`~flask.current_app` làm người gửi cho một signal. Sử dụng
   ``current_app._get_current_object()`` thay thế. Lý do cho điều này là
   :data:`~flask.current_app` là một proxy và không phải là đối tượng ứng dụng
   thực sự.


Signals và Request Context của Flask
------------------------------------

Các proxy context-local có sẵn giữa :data:`~flask.request_started` và
:data:`~flask.request_finished`, vì vậy bạn có thể dựa vào :class:`flask.g` và các cái khác
khi cần thiết. Lưu ý các hạn chế được mô tả trong :ref:`signals-sending` và
signal :data:`~flask.request_tearing_down`.


Đăng ký Signal Dựa trên Decorator
---------------------------------

Bạn cũng có thể dễ dàng đăng ký vào các signals bằng cách sử dụng decorator
:meth:`~blinker.base.NamedSignal.connect_via`::

    from flask import template_rendered

    @template_rendered.connect_via(app)
    def when_template_rendered(sender, template, context, **extra):
        print(f'Template {template.name} is rendered with {context}')


.. _blinker: https://pypi.org/project/blinker/
