Bảo mật Web
===================

Các ứng dụng web phải đối mặt với nhiều loại vấn đề bảo mật tiềm ẩn, và việc đảm bảo mọi thứ đều đúng có thể rất khó khăn, hoặc thậm chí không biết "đúng" là gì. Flask cố gắng giải quyết một số vấn đề này theo mặc định, nhưng còn có những phần bạn cần tự xử lý. Nhiều giải pháp này là sự đánh đổi, và sẽ phụ thuộc vào nhu cầu và mô hình đe dọa cụ thể của từng ứng dụng. Nhiều nền tảng lưu trữ có thể giải quyết một số vấn đề mà Flask không cần phải xử lý.

Sử dụng tài nguyên
-------------------

Một loại tấn công phổ biến là "Từ chối dịch vụ" (DoS hoặc DDoS). Đây là một loại rất rộng, và các biến thể khác nhau nhắm vào các lớp khác nhau của một ứng dụng đã triển khai. Nói chung, một thứ gì đó được thực hiện để tăng thời gian xử lý hoặc bộ nhớ sử dụng cho mỗi yêu cầu, đến mức không còn đủ tài nguyên để xử lý các yêu cầu hợp lệ.

Flask cung cấp một vài tùy chọn cấu hình để xử lý việc sử dụng tài nguyên. Chúng có thể được đặt cho toàn bộ ứng dụng hoặc cho từng yêu cầu riêng lẻ. Tài liệu cho mỗi tùy chọn sẽ có chi tiết hơn.

-   :data:`MAX_CONTENT_LENGTH` hoặc :attr:`.Request.max_content_length` kiểm soát lượng dữ liệu sẽ được đọc từ một yêu cầu. Mặc định không được đặt, mặc dù nó vẫn sẽ chặn các luồng không giới hạn trừ khi máy chủ WSGI chỉ ra hỗ trợ.
-   :data:`MAX_FORM_MEMORY_SIZE` hoặc :attr:`.Request.max_form_memory_size` kiểm soát kích thước tối đa của bất kỳ trường ``multipart/form-data`` không phải là tệp. Mặc định là 500kB.
-   :data:`MAX_FORM_PARTS` hoặc :attr:`.Request.max_form_parts` kiểm soát số lượng trường ``multipart/form-data`` có thể được phân tích. Mặc định là 1000. Kết hợp với ``max_form_memory_size`` mặc định, điều này có nghĩa một biểu mẫu sẽ chiếm tối đa 500MB bộ nhớ.

Bất kể các thiết lập này, bạn cũng nên xem xét các thiết lập có sẵn từ hệ điều hành, môi trường container (Docker, v.v.), máy chủ WSGI, máy chủ HTTP và nền tảng lưu trữ. Chúng thường có cách để đặt giới hạn tài nguyên, thời gian chờ và các kiểm tra khác bất kể Flask được cấu hình như thế nào.

.. _security-xss:

Cross-Site Scripting (XSS)
--------------------------

Cross site scripting là khái niệm chèn HTML tùy ý (và JavaScript) vào ngữ cảnh của một trang web. Để khắc phục, các nhà phát triển phải escape (thoát) đúng văn bản để không cho phép chèn HTML tùy ý. Để biết thêm thông tin, xem bài Wikipedia về `Cross-Site Scripting <https://en.wikipedia.org/wiki/Cross-site_scripting>`_.

Flask cấu hình Jinja để tự động escape tất cả các giá trị trừ khi được chỉ định ngược lại. Điều này nên loại bỏ mọi vấn đề XSS gây ra trong mẫu, nhưng vẫn còn những nơi khác mà bạn cần cẩn thận:

-   tạo HTML mà không có sự trợ giúp của Jinja
-   gọi :class:`~markupsafe.Markup` trên dữ liệu do người dùng cung cấp
-   gửi HTML từ các tệp tải lên, không làm như vậy, hãy sử dụng header ``Content-Disposition: attachment`` để ngăn vấn đề này.
-   gửi tệp văn bản từ các tệp tải lên. Một số trình duyệt sẽ đoán loại nội dung dựa trên vài byte đầu tiên, vì vậy người dùng có thể lừa trình duyệt thực thi HTML.

Một điều rất quan trọng khác là các thuộc tính không có dấu ngoặc kép. Mặc dù Jinja có thể bảo vệ bạn khỏi các vấn đề XSS bằng cách escape HTML, có một thứ mà nó không thể bảo vệ: XSS qua việc chèn thuộc tính. Để chống lại vector tấn công này, luôn luôn đặt dấu ngoặc kép hoặc đơn cho các thuộc tính khi sử dụng biểu thức Jinja trong chúng:

.. sourcecode:: html+jinja

    <input value="{{ value }}">

Tại sao cần làm như vậy? Vì nếu không, kẻ tấn công có thể dễ dàng chèn các trình xử lý JavaScript tùy ý. Ví dụ, kẻ tấn công có thể chèn đoạn HTML+JavaScript sau:

.. sourcecode:: html

    onmouseover=alert(document.cookie)

Khi người dùng di chuột qua ô nhập, cookie sẽ được hiện ra trong một cửa sổ cảnh báo. Thay vì chỉ hiển thị cookie, kẻ tấn công có thể thực thi bất kỳ mã JavaScript nào khác. Kết hợp với việc tiêm CSS, kẻ tấn công thậm chí có thể làm cho phần tử chiếm toàn bộ trang, khiến người dùng chỉ cần di chuột bất kỳ nơi nào trên trang để kích hoạt tấn công.

Có một loại vấn đề XSS mà việc escape của Jinja không bảo vệ: thuộc tính ``href`` của thẻ ``a`` có thể chứa URI ``javascript:``, trình duyệt sẽ thực thi khi người dùng nhấp vào nếu không được bảo vệ đúng cách.

.. sourcecode:: html

    <a href="{{ value }}">click here</a>
    <a href="javascript:alert('unsafe');">click here</a>

Để ngăn điều này, bạn cần đặt header phản hồi :ref:`security-csp`.

Cross-Site Request Forgery (CSRF)
---------------------------------

Một vấn đề lớn khác là CSRF. Đây là một chủ đề rất phức tạp và tôi sẽ không đi sâu vào chi tiết ở đây, chỉ đề cập tới nó là gì và cách ngăn ngừa một cách lý thuyết.

Nếu thông tin xác thực của bạn được lưu trong cookie, bạn có trạng thái ngầm định "đã đăng nhập". Cookie này được gửi cùng mỗi yêu cầu tới một trang. Thật không may, điều này bao gồm các yêu cầu được kích hoạt bởi các trang bên thứ ba. Nếu bạn không lưu ý, một số người có thể lừa người dùng của bạn thực hiện các hành động ngu ngốc mà họ không biết.

Giả sử bạn có một URL cụ thể, khi bạn gửi yêu cầu ``POST`` tới sẽ xóa hồ sơ người dùng (ví dụ ``http://example.com/user/delete``). Nếu kẻ tấn công tạo một trang mà gửi yêu cầu POST tới URL đó với một chút JavaScript, họ chỉ cần lừa một số người dùng tải trang đó và hồ sơ của họ sẽ bị xóa.

Hãy tưởng tượng bạn chạy Facebook với hàng triệu người dùng đồng thời và ai đó gửi liên kết tới hình ảnh mèo con. Khi người dùng truy cập trang đó, hồ sơ của họ sẽ bị xóa trong khi họ đang xem hình ảnh mèo bông.

Làm sao để ngăn? Cơ bản là với mỗi yêu cầu thay đổi nội dung trên máy chủ, bạn cần một token một lần dùng duy nhất, lưu trong cookie **và** truyền cùng dữ liệu biểu mẫu. Khi nhận dữ liệu trên máy chủ, bạn so sánh hai token và đảm bảo chúng bằng nhau.

Tại sao Flask không làm điều này cho bạn? Vị trí lý tưởng để thực hiện việc này là trong khung xác thực biểu mẫu, mà Flask không có.

.. _security-json:

JSON Security
-------------

Trong Flask 0.10 và thấp hơn, :func:`~flask.jsonify` không tuần tự hoá các mảng cấp cao. Điều này là do một lỗ hổng bảo mật trong ECMAScript 4. ECMAScript 5 đã khắc phục lỗ hổng này, vì vậy chỉ các trình duyệt rất cũ mới còn bị ảnh hưởng. Tất cả các trình duyệt này đều có các lỗ hổng nghiêm trọng khác, vì vậy hành vi này đã được thay đổi và :func:`~flask.jsonify` hiện hỗ trợ tuần tự hoá các mảng.

Tiêu đề bảo mật
----------------

Các trình duyệt nhận ra các tiêu đề phản hồi để kiểm soát bảo mật. Chúng tôi khuyến nghị xem xét từng tiêu đề dưới đây để sử dụng trong ứng dụng của bạn. Tiện ích mở rộng `Flask-Talisman`_ có thể được dùng để quản lý HTTPS và các tiêu đề bảo mật cho bạn.

.. _Flask-Talisman: https://github.com/wntrblm/flask-talisman

HTTP Strict Transport Security (HSTS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Buộc trình duyệt chuyển tất cả các yêu cầu HTTP sang HTTPS, ngăn chặn các cuộc tấn công man-in-the-middle (MITM). ::

    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security

Content Security Policy (CSP)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cho trình duyệt biết nơi nó có thể tải các loại tài nguyên. Tiêu đề này nên được sử dụng khi có thể, nhưng cần định nghĩa chính sách phù hợp cho trang của bạn. Một chính sách rất nghiêm ngặt sẽ là::

    response.headers['Content-Security-Policy'] = "default-src 'self'"

- https://csp.withgoogle.com/docs/index.html
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy

X-Content-Type-Options
~~~~~~~~~~~~~~~~~~~~~~

Buộc trình duyệt tuân thủ loại nội dung phản hồi thay vì cố gắng đoán, có thể bị lợi dụng để tạo tấn công XSS. ::

    response.headers['X-Content-Type-Options'] = 'nosniff'

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options

X-Frame-Options
~~~~~~~~~~~~~~~~

Ngăn các trang bên ngoài nhúng trang của bạn trong một ``iframe``. Điều này ngăn các cuộc tấn công "clickjacking". ::

    response.headers['X-Frame-Options'] = 'SAMEORIGIN'

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options

Set-Cookie options
~~~~~~~~~~~~~~~~~~

Các tùy chọn này có thể được thêm vào tiêu đề ``Set-Cookie`` để cải thiện bảo mật. Flask có các tùy chọn cấu hình để đặt chúng trên cookie phiên. Chúng cũng có thể được đặt trên các cookie khác.

- ``Secure`` giới hạn cookie chỉ truyền qua lưu lượng HTTPS.
- ``HttpOnly`` bảo vệ nội dung cookie khỏi việc đọc bằng JavaScript.
- ``SameSite`` hạn chế cách cookie được gửi với các yêu cầu từ các trang bên ngoài. Có thể đặt là ``'Lax'`` (được khuyến nghị) hoặc ``'Strict'``.

```python
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

response.set_cookie('username', 'flask', secure=True, httponly=True, samesite='Lax')
```

Xác định ``Expires`` hoặc ``Max-Age`` sẽ làm cookie hết hạn sau thời gian cho trước, hoặc sau thời gian hiện tại cộng với tuổi thọ. Nếu không đặt, cookie sẽ bị xóa khi trình duyệt đóng.

```python
# cookie hết hạn sau 10 phút
response.set_cookie('snakes', '3', max_age=600)
```

Đối với cookie phiên, nếu :attr:`session.permanent <flask.session.permanent>` được đặt, thì :data:`PERMANENT_SESSION_LIFETIME` được dùng để đặt thời gian hết hạn. Flask mặc định kiểm tra chữ ký mật mã không cũ hơn giá trị này. Giảm giá trị này có thể giúp giảm thiểu các cuộc tấn công replay, nơi cookie bị chặn và gửi lại sau.

```python
app.config.update(
    PERMANENT_SESSION_LIFETIME=600
)

@app.route('/login', methods=['POST'])
def login():
    ...
    session.clear()
    session['user_id'] = user.id
    session.permanent = True
    ...
```

Sử dụng :class:`itsdangerous.TimedSerializer` để ký và xác thực các giá trị cookie khác (hoặc bất kỳ giá trị nào cần chữ ký bảo mật).

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie

.. _samesite_support: https://caniuse.com/#feat=same-site-cookie-attribute

Header xác thực Host
--------------------

Header ``Host`` được client sử dụng để chỉ định tên máy chủ mà yêu cầu được thực hiện. Điều này được dùng, ví dụ, bởi ``url_for(..., _external=True)`` để tạo URL đầy đủ, dùng trong email hoặc các tin nhắn ngoài trình duyệt.

Mặc định ứng dụng không biết host nào được phép truy cập và cho phép bất kỳ host nào. Mặc dù trình duyệt không cho phép đặt header ``Host``, các yêu cầu do kẻ tấn công trong các kịch bản khác có thể đặt header ``Host`` theo ý muốn.

Khi triển khai ứng dụng, đặt :data:`TRUSTED_HOSTS` để giới hạn các giá trị header ``Host`` có thể nhận.

Header ``Host`` có thể được proxy thay đổi bởi các proxy giữa client và ứng dụng. Xem :doc:`deploying/proxy_fix` để chỉ cho ứng dụng biết các giá trị proxy nào đáng tin cậy.

Sao chép/Dán vào Terminal
--------------------------

Các ký tự ẩn như ký tự backspace (``\b``, ``^H``) có thể khiến văn bản hiển thị khác trong HTML so với khi nó được giải thích nếu ``dán vào terminal https://security.stackexchange.com/q/39118``__.

Ví dụ, ``import y\bose\bm\bi\bt\be`` hiển thị là ``import yosemite`` trong HTML, nhưng các backspace được áp dụng khi dán vào terminal, và nó trở thành ``import os``.

Nếu bạn mong đợi người dùng sao chép và dán mã không tin cậy từ trang của bạn, ví dụ từ các bình luận trên blog kỹ thuật, hãy cân nhắc lọc thêm, như thay thế tất cả ký tự ``\b``.

.. code-block:: python

    body = body.replace("\b", "")

Hầu hết các terminal hiện đại sẽ cảnh báo và loại bỏ các ký tự ẩn khi dán, vì vậy không cần thiết phải làm như vậy. Tuy nhiên, vẫn có cách tạo lệnh nguy hiểm mà không thể lọc được. Tùy thuộc vào trường hợp sử dụng của trang, có thể hiển thị cảnh báo về việc sao chép mã nói chung.
