Quyết định Thiết kế trong Flask
================================

Nếu bạn tò mò tại sao Flask làm một số điều theo cách nó làm và không
khác đi, phần này dành cho bạn. Điều này sẽ cung cấp cho bạn một ý tưởng về
một số quyết định thiết kế có thể xuất hiện tùy tiện và đáng ngạc nhiên lúc
đầu, đặc biệt là khi so sánh trực tiếp với các framework khác.


Đối tượng Ứng dụng Rõ ràng
---------------------------

Một ứng dụng web Python dựa trên WSGI phải có một callable
trung tâm triển khai ứng dụng thực tế. Trong Flask đây là một
instance của class :class:`~flask.Flask`. Mỗi ứng dụng Flask phải
tạo một instance của class này và truyền cho nó tên của
module, nhưng tại sao Flask không thể tự làm điều đó?

Không có một đối tượng ứng dụng rõ ràng như vậy, mã sau::

    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def index():
        return 'Hello World!'

Sẽ trông như thế này thay thế::

    from hypothetical_flask import route

    @route('/')
    def index():
        return 'Hello World!'

Có ba lý do chính cho điều này. Quan trọng nhất là
các đối tượng ứng dụng ngầm định yêu cầu rằng chỉ có thể có một instance tại
một thời điểm. Có những cách để giả mạo nhiều ứng dụng với một
đối tượng ứng dụng duy nhất, như duy trì một stack các ứng dụng, nhưng điều này
gây ra một số vấn đề mà tôi sẽ không nêu chi tiết ở đây. Bây giờ câu hỏi là:
khi nào một microframework cần nhiều hơn một ứng dụng cùng một
lúc? Một ví dụ tốt cho điều này là unit testing. Khi bạn muốn kiểm tra
một cái gì đó, có thể rất hữu ích khi tạo một ứng dụng tối thiểu để kiểm tra
hành vi cụ thể. Khi đối tượng ứng dụng bị xóa, mọi thứ nó
đã cấp phát sẽ được giải phóng lại.

Một điều khác trở nên khả thi khi bạn có một đối tượng rõ ràng nằm
xung quanh trong mã của bạn là bạn có thể subclass base class
(:class:`~flask.Flask`) để thay đổi hành vi cụ thể. Điều này sẽ không
khả thi nếu không có hack nếu đối tượng được tạo trước cho bạn
dựa trên một class không được expose cho bạn.

Nhưng có một lý do rất quan trọng khác tại sao Flask phụ thuộc vào
việc khởi tạo rõ ràng class đó: tên package. Bất cứ khi nào bạn
tạo một instance Flask, bạn thường truyền cho nó `__name__` làm tên package.
Flask phụ thuộc vào thông tin đó để tải tài nguyên đúng cách tương đối
với module của bạn. Với sự hỗ trợ xuất sắc của Python cho reflection, nó có thể
sau đó truy cập package để tìm ra nơi các template và file tĩnh
được lưu trữ (xem :meth:`~flask.Flask.open_resource`). Bây giờ rõ ràng có
các framework xung quanh không cần bất kỳ cấu hình nào và vẫn có thể
tải các template tương đối với module ứng dụng của bạn. Nhưng chúng phải
sử dụng thư mục làm việc hiện tại cho điều đó, đó là một cách rất không đáng tin cậy
để xác định nơi ứng dụng đang ở. Thư mục làm việc hiện tại
là process-wide và nếu bạn đang chạy nhiều ứng dụng trong một
process (có thể xảy ra trong một webserver mà bạn không biết) các đường dẫn
sẽ bị lệch. Tệ hơn: nhiều webserver không đặt thư mục làm việc thành
thư mục của ứng dụng của bạn mà là document root không
phải là cùng một thư mục.

Lý do thứ ba là "rõ ràng tốt hơn ngầm định". Đối tượng đó là
ứng dụng WSGI của bạn, bạn không phải nhớ bất cứ điều gì khác. Nếu bạn
muốn áp dụng một WSGI middleware, chỉ cần wrap nó và bạn đã xong (mặc dù
có những cách tốt hơn để làm điều đó để bạn không mất tham chiếu
đến đối tượng ứng dụng :meth:`~flask.Flask.wsgi_app`).

Hơn nữa, thiết kế này làm cho việc sử dụng một factory function để
tạo ứng dụng trở nên khả thi, điều này rất hữu ích cho unit testing và các
điều tương tự (:doc:`/patterns/appfactories`).

Hệ thống Routing
----------------

Flask sử dụng hệ thống routing Werkzeug được thiết kế để
tự động sắp xếp các route theo độ phức tạp. Điều này có nghĩa là bạn có thể khai báo
các route theo thứ tự tùy ý và chúng vẫn sẽ hoạt động như mong đợi. Đây là một
yêu cầu nếu bạn muốn triển khai đúng cách routing dựa trên decorator
vì các decorator có thể được kích hoạt theo thứ tự không xác định khi ứng dụng được
chia thành nhiều module.

Một quyết định thiết kế khác với hệ thống routing Werkzeug là các route
trong Werkzeug cố gắng đảm bảo rằng các URL là duy nhất. Werkzeug sẽ đi khá xa
với điều đó ở chỗ nó sẽ tự động chuyển hướng đến một URL canonical nếu một route
là mơ hồ.


Một Template Engine
-------------------

Flask quyết định một template engine: Jinja. Tại sao Flask không có một
giao diện template engine pluggable? Bạn rõ ràng có thể sử dụng một
template engine khác, nhưng Flask vẫn sẽ cấu hình Jinja cho bạn. Trong khi
giới hạn đó rằng Jinja *luôn* được cấu hình có thể sẽ biến mất,
quyết định gộp một template engine và sử dụng nó sẽ không.

Các template engine giống như ngôn ngữ lập trình và mỗi engine đó
có một sự hiểu biết nhất định về cách mọi thứ hoạt động. Trên bề mặt chúng
đều hoạt động giống nhau: bạn cho engine biết đánh giá một template với một tập hợp
các biến và lấy giá trị trả về dưới dạng chuỗi.

Nhưng đó là nơi sự giống nhau kết thúc. Ví dụ Jinja có một
hệ thống filter mở rộng, một cách nhất định để thực hiện kế thừa template,
hỗ trợ cho các khối có thể tái sử dụng (macro) có thể được sử dụng từ bên trong
các template và cũng từ mã Python, hỗ trợ rendering template lặp,
cú pháp có thể cấu hình và hơn thế nữa. Mặt khác một engine
như Genshi dựa trên đánh giá XML stream, kế thừa template bằng cách
tính đến tính khả dụng của XPath và hơn thế nữa. Mako mặt khác
xử lý các template tương tự như các module Python.

Khi nói đến việc kết nối một template engine với một ứng dụng hoặc
framework, có nhiều hơn là chỉ rendering template. Ví dụ,
Flask sử dụng hỗ trợ autoescaping mở rộng của Jinja. Nó cũng cung cấp
các cách để truy cập macro từ các template Jinja.

Một lớp trừu tượng template không lấy đi các tính năng độc đáo của
các template engine là một khoa học riêng và một
công việc quá lớn cho một microframework như Flask.

Hơn nữa, các extension sau đó có thể dễ dàng phụ thuộc vào một ngôn ngữ template
đang có mặt. Bạn có thể dễ dàng sử dụng ngôn ngữ templating của riêng mình, nhưng một
extension vẫn có thể phụ thuộc vào chính Jinja.


"Micro" có nghĩa là gì?
-----------------------

"Micro" không có nghĩa là toàn bộ ứng dụng web của bạn phải vừa với một file
Python duy nhất (mặc dù nó chắc chắn có thể), cũng không có nghĩa là Flask thiếu
chức năng. "Micro" trong microframework có nghĩa là Flask nhằm mục đích giữ
core đơn giản nhưng có thể mở rộng. Flask sẽ không đưa ra nhiều quyết định cho bạn, chẳng hạn như
cơ sở dữ liệu nào để sử dụng. Những quyết định mà nó đưa ra, chẳng hạn như
templating engine nào để sử dụng, rất dễ thay đổi. Mọi thứ khác tùy thuộc vào bạn, để
Flask có thể là mọi thứ bạn cần và không có gì bạn không cần.

Theo mặc định, Flask không bao gồm một lớp trừu tượng cơ sở dữ liệu, xác thực form
hoặc bất cứ thứ gì khác nơi các thư viện khác nhau đã tồn tại có thể
xử lý điều đó. Thay vào đó, Flask hỗ trợ các extension để thêm chức năng như vậy vào
ứng dụng của bạn như thể nó được triển khai trong chính Flask. Nhiều extension
cung cấp tích hợp cơ sở dữ liệu, xác thực form, xử lý upload, các
công nghệ xác thực mở khác nhau, và hơn thế nữa. Flask có thể là "micro", nhưng nó sẵn sàng cho
sử dụng production trên nhiều nhu cầu khác nhau.

Tại sao Flask tự gọi mình là một microframework nhưng nó phụ thuộc vào hai
thư viện (cụ thể là Werkzeug và Jinja). Tại sao không nên? Nếu chúng ta nhìn
sang phía Ruby của phát triển web, chúng ta có một giao thức rất
tương tự như WSGI. Chỉ là nó được gọi là Rack ở đó, nhưng ngoài điều đó nó
trông rất giống một rendition WSGI cho Ruby. Nhưng gần như tất cả
các ứng dụng trong Ruby land không hoạt động với Rack trực tiếp, mà trên một
thư viện có cùng tên. Thư viện Rack này có hai tương đương trong
Python: WebOb (trước đây là Paste) và Werkzeug. Paste vẫn còn nhưng
theo hiểu biết của tôi, nó đã bị deprecated một phần ủng hộ WebOb. Sự
phát triển của WebOb và Werkzeug bắt đầu song song với các ý tưởng tương tự
trong tâm trí: là một triển khai tốt của WSGI cho các ứng dụng khác tận dụng
.

Flask là một framework tận dụng công việc đã được thực hiện bởi
Werkzeug để giao tiếp WSGI đúng cách (có thể là một nhiệm vụ phức tạp vào
những lúc). Nhờ vào sự phát triển gần đây trong cơ sở hạ tầng
package Python, các package với dependency không còn là vấn đề nữa và
có rất ít lý do chống lại việc có các thư viện phụ thuộc vào các thư viện khác.


Context Local
-------------

Flask sử dụng các context local và proxy đặc biệt để cung cấp quyền truy cập vào
ứng dụng hiện tại và dữ liệu request cho bất kỳ mã nào đang chạy trong một request, lệnh CLI,
v.v. Context local là cụ thể cho worker xử lý hoạt động, chẳng hạn như một
thread, process, coroutine, hoặc greenlet.

Context và proxy giúp giải quyết hai vấn đề phát triển: circular import, và
truyền xung quanh dữ liệu toàn cục. :data:`.current_app` có thể được sử dụng để truy cập
đối tượng ứng dụng mà không cần import đối tượng app trực tiếp, tránh
các vấn đề circular import. :data:`.request`, :data:`.session`, và :data:`.g` có thể
được import để truy cập dữ liệu hiện tại cho request, thay vì cần
truyền chúng làm đối số qua mọi hàm duy nhất trong dự án của bạn.


Hỗ trợ Async/await và ASGI
---------------------------

Flask hỗ trợ các coroutine ``async`` cho các view function bằng cách thực thi
coroutine trên một thread riêng biệt thay vì sử dụng một event loop trên
main thread như một framework async-first (ASGI) sẽ làm. Điều này là cần thiết
để Flask duy trì khả năng tương thích ngược với các extension và mã được xây dựng
trước khi ``async`` được giới thiệu vào Python. Sự타협 này giới thiệu
một chi phí hiệu suất so với các framework ASGI, do
overhead của các thread.

Do cách mã của Flask gắn chặt với WSGI, không rõ liệu có thể
làm cho class ``Flask`` hỗ trợ cả ASGI và WSGI cùng một lúc. Công việc
hiện đang được thực hiện trong Werkzeug để làm việc với ASGI, có thể
cuối cùng cho phép hỗ trợ trong Flask.

Xem :doc:`/async-await` để thảo luận thêm.


Flask là gì, Flask không phải là gì
------------------------------------

Flask sẽ không bao giờ có một lớp cơ sở dữ liệu. Nó sẽ không có một thư viện form
hoặc bất cứ thứ gì khác theo hướng đó. Chính Flask chỉ cầu nối đến Werkzeug
để triển khai một ứng dụng WSGI đúng cách và đến Jinja để xử lý templating.
Nó cũng bind vào một vài package thư viện tiêu chuẩn phổ biến như logging.
Mọi thứ khác là cho các extension.

Tại sao lại như vậy? Bởi vì mọi người có sở thích và
yêu cầu khác nhau và Flask không thể đáp ứng những điều đó nếu nó buộc bất kỳ điều này
vào core. Phần lớn các ứng dụng web sẽ cần một template
engine ở một dạng nào đó. Tuy nhiên không phải mọi ứng dụng đều cần một cơ sở dữ liệu SQL.

Khi codebase của bạn phát triển, bạn tự do đưa ra các quyết định thiết kế phù hợp
cho dự án của mình. Flask sẽ tiếp tục cung cấp một lớp glue rất đơn giản cho
những gì tốt nhất mà Python cung cấp. Bạn có thể triển khai các mẫu nâng cao trong
SQLAlchemy hoặc công cụ cơ sở dữ liệu khác, giới thiệu persistence dữ liệu phi quan hệ
khi thích hợp, và tận dụng các công cụ framework-agnostic được xây dựng cho WSGI,
giao diện web Python.

Ý tưởng của Flask là xây dựng một nền tảng tốt cho tất cả các ứng dụng.
Mọi thứ khác tùy thuộc vào bạn hoặc các extension.
