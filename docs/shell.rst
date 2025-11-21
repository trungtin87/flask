Làm việc với Shell
==================

Một trong những lý do mọi người yêu thích Python là shell tương tác. Nó cho phép
bạn chơi đùa với mã trong thời gian thực và nhận kết quả ngay lập tức.
Flask cung cấp lệnh CLI ``flask shell`` để khởi động một Python shell
tương tác với một số thiết lập được thực hiện để làm cho việc làm việc với ứng dụng Flask dễ dàng hơn.

.. code-block:: text

    $ flask shell

Tạo một Request Context
-----------------------

``flask shell`` đẩy một app context tự động, vì vậy :data:`.current_app` và
:data:`.g` đã có sẵn. Tuy nhiên, không có request HTTP nào đang được
xử lý trong shell, vì vậy :data:`.request` và :data:`.session` chưa có sẵn.

Cách dễ nhất để tạo một request context thích hợp từ shell là bằng cách
sử dụng phương thức :attr:`~flask.Flask.test_request_context` tạo ra
cho chúng ta một :class:`~flask.ctx.RequestContext`:

>>> ctx = app.test_request_context()

Thông thường bạn sẽ sử dụng câu lệnh ``with`` để làm cho context này hoạt động, nhưng
trong shell dễ dàng hơn để gọi :meth:`~.RequestContext.push` và
:meth:`~.RequestContext.pop` thủ công:

>>> ctx.push()

Từ thời điểm đó trở đi bạn có thể làm việc với đối tượng request cho đến khi bạn gọi
``pop``:

>>> ctx.pop()

Kích hoạt Trước/Sau Request
---------------------------

Chỉ bằng cách tạo một request context, bạn vẫn chưa chạy mã mà
thường được chạy trước một request. Điều này có thể dẫn đến cơ sở dữ liệu của bạn
không khả dụng nếu bạn đang kết nối với cơ sở dữ liệu trong một
callback trước request hoặc người dùng hiện tại không được lưu trữ trên
đối tượng :data:`~flask.g` v.v.

Tuy nhiên điều này có thể dễ dàng được thực hiện bởi chính bạn. Chỉ cần gọi
:meth:`~flask.Flask.preprocess_request`:

>>> ctx = app.test_request_context()
>>> ctx.push()
>>> app.preprocess_request()

Hãy nhớ rằng hàm :meth:`~flask.Flask.preprocess_request`
có thể trả về một đối tượng response, trong trường hợp đó chỉ cần bỏ qua nó.

Để tắt một request, bạn cần đánh lừa một chút trước khi các hàm sau request
(được kích hoạt bởi :meth:`~flask.Flask.process_response`) hoạt động trên
một đối tượng response:

>>> app.process_response(app.response_class())
<Response 0 bytes [200 OK]>
>>> ctx.pop()

Các hàm được đăng ký như :meth:`~flask.Flask.teardown_request` được
tự động gọi khi context bị pop. Vì vậy đây là nơi hoàn hảo
để tự động hủy các tài nguyên cần thiết bởi request
context (chẳng hạn như kết nối cơ sở dữ liệu).


Cải thiện hơn nữa Trải nghiệm Shell
-----------------------------------

Nếu bạn thích ý tưởng thử nghiệm trong một shell, hãy tạo cho mình một module
với những thứ bạn muốn star import vào session tương tác của mình. Ở đó
bạn cũng có thể định nghĩa thêm một số phương thức trợ giúp cho những việc chung như
khởi tạo cơ sở dữ liệu, xóa bảng v.v.

Chỉ cần đặt chúng vào một module (như `shelltools`) và import từ đó:

>>> from shelltools import *
