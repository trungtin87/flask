JavaScript, ``fetch``, và JSON
==============================

Bạn có thể muốn làm cho trang HTML của mình trở nên động, bằng cách thay đổi dữ liệu mà không cần
tải lại toàn bộ trang. Thay vì gửi một ``<form>`` HTML và
thực hiện chuyển hướng để render lại template, bạn có thể thêm
`JavaScript`_ gọi |fetch|_ và thay thế nội dung trên trang.

|fetch|_ là giải pháp JavaScript hiện đại, tích hợp sẵn để thực hiện
các request từ một trang. Bạn có thể đã nghe nói về các phương pháp và thư viện "AJAX"
khác, chẳng hạn như |XHR|_ hoặc `jQuery`_. Những thứ này không còn cần thiết trong
các trình duyệt hiện đại, mặc dù bạn có thể chọn sử dụng chúng hoặc một thư viện khác
tùy thuộc vào yêu cầu của ứng dụng của bạn. Các tài liệu này sẽ chỉ tập trung
vào các tính năng JavaScript tích hợp sẵn.

.. _JavaScript: https://developer.mozilla.org/Web/JavaScript
.. |fetch| replace:: ``fetch()``
.. _fetch: https://developer.mozilla.org/Web/API/Fetch_API
.. |XHR| replace:: ``XMLHttpRequest()``
.. _XHR: https://developer.mozilla.org/Web/API/XMLHttpRequest
.. _jQuery: https://jquery.com/


Render Template
---------------

Điều quan trọng là phải hiểu sự khác biệt giữa template và
JavaScript. Template được render trên máy chủ, trước khi phản hồi được
gửi đến trình duyệt của người dùng. JavaScript chạy trong trình duyệt của người dùng, sau khi
template được render và gửi đi. Do đó, không thể sử dụng
JavaScript để ảnh hưởng đến cách template Jinja được render, nhưng có thể
render dữ liệu vào JavaScript sẽ chạy.

Để cung cấp dữ liệu cho JavaScript khi render template, hãy sử dụng
bộ lọc :func:`~jinja-filters.tojson` trong một khối ``<script>``. Điều này sẽ
chuyển đổi dữ liệu thành một đối tượng JavaScript hợp lệ, và đảm bảo rằng bất kỳ
ký tự HTML không an toàn nào được render an toàn. Nếu bạn không sử dụng
bộ lọc ``tojson``, bạn sẽ nhận được một ``SyntaxError`` trong console của
trình duyệt.

.. code-block:: python

    data = generate_report()
    return render_template("report.html", chart_data=data)

.. code-block:: jinja

    <script>
        const chart_data = {{ chart_data|tojson }}
        chartLib.makeChart(chart_data)
    </script>

Một mẫu ít phổ biến hơn là thêm dữ liệu vào thuộc tính ``data-`` trên một
thẻ HTML. Trong trường hợp này, bạn phải sử dụng dấu nháy đơn xung quanh giá trị, không phải
dấu nháy kép, nếu không bạn sẽ tạo ra HTML không hợp lệ hoặc không an toàn.

.. code-block:: jinja

    <div data-chart='{{ chart_data|tojson }}'></div>


Tạo URL
-------

Cách khác để lấy dữ liệu từ máy chủ đến JavaScript là thực hiện một
request cho nó. Đầu tiên, bạn cần biết URL để request.

Cách đơn giản nhất để tạo URL là tiếp tục sử dụng
:func:`~flask.url_for` khi render template. Ví dụ:

.. code-block:: javascript

    const user_url = {{ url_for("user", id=current_user.id)|tojson }}
    fetch(user_url).then(...)

Tuy nhiên, bạn có thể cần tạo một URL dựa trên thông tin bạn chỉ
biết trong JavaScript. Như đã thảo luận ở trên, JavaScript chạy trong trình duyệt
của người dùng, không phải là một phần của quá trình render template, vì vậy bạn không thể sử dụng
``url_for`` tại thời điểm đó.

Trong trường hợp này, bạn cần biết "root URL" mà ứng dụng của bạn
được phục vụ. Trong các thiết lập đơn giản, đây là ``/``, nhưng nó cũng có thể
là một cái gì đó khác, như ``https://example.com/myapp/``.

Một cách đơn giản để cho mã JavaScript của bạn biết về root này là đặt nó
làm biến toàn cục khi render template. Sau đó bạn có thể sử dụng nó
khi tạo URL từ JavaScript.

.. code-block:: javascript

    const SCRIPT_ROOT = {{ request.script_root|tojson }}
    let user_id = ...  // làm gì đó để lấy user id từ trang
    let user_url = `${SCRIPT_ROOT}/user/${user_id}`
    fetch(user_url).then(...)


Thực hiện Request với ``fetch``
-------------------------------

|fetch|_ nhận hai đối số, một URL và một đối tượng với các tùy chọn khác,
và trả về một |Promise|_. Chúng tôi sẽ không đề cập đến tất cả các tùy chọn có sẵn, và
sẽ chỉ sử dụng ``then()`` trên promise, không phải các callback khác hoặc
cú pháp ``await``. Đọc tài liệu MDN được liên kết để biết thêm thông tin về
các tính năng đó.

Theo mặc định, phương thức GET được sử dụng. Nếu phản hồi chứa JSON, nó
có thể được sử dụng với một chuỗi callback ``then()``.

.. code-block:: javascript

    const room_url = {{ url_for("room_detail", id=room.id)|tojson }}
    fetch(room_url)
        .then(response => response.json())
        .then(data => {
            // data là một đối tượng JSON đã được phân tích cú pháp
        })

Để gửi dữ liệu, sử dụng một phương thức dữ liệu như POST, và truyền tùy chọn ``body``.
Các loại dữ liệu phổ biến nhất là form data hoặc JSON data.

Để gửi form data, truyền một đối tượng |FormData|_ đã được điền. Điều này sử dụng
cùng định dạng như một form HTML, và sẽ được truy cập với ``request.form``
trong một view Flask.

.. code-block:: javascript

    let data = new FormData()
    data.append("name", "Flask Room")
    data.append("description", "Talk about Flask here.")
    fetch(room_url, {
        "method": "POST",
        "body": data,
    }).then(...)

Nói chung, ưu tiên gửi dữ liệu request dưới dạng form data, như sẽ được sử dụng
khi gửi một form HTML. JSON có thể đại diện cho dữ liệu phức tạp hơn, nhưng
trừ khi bạn cần điều đó, tốt hơn là nên gắn bó với định dạng đơn giản hơn. Khi
gửi dữ liệu JSON, header ``Content-Type: application/json`` cũng phải được
gửi, nếu không Flask sẽ trả về lỗi 400.

.. code-block:: javascript

    let data = {
        "name": "Flask Room",
        "description": "Talk about Flask here.",
    }
    fetch(room_url, {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": JSON.stringify(data),
    }).then(...)

.. |Promise| replace:: ``Promise``
.. _Promise: https://developer.mozilla.org/Web/JavaScript/Reference/Global_Objects/Promise
.. |FormData| replace:: ``FormData``
.. _FormData: https://developer.mozilla.org/en-US/docs/Web/API/FormData


Theo dõi Chuyển hướng (Redirects)
---------------------------------

Một phản hồi có thể là một chuyển hướng, ví dụ nếu bạn đã đăng nhập bằng
JavaScript thay vì form HTML truyền thống, và view của bạn trả về
một chuyển hướng thay vì JSON. Các request JavaScript có theo dõi chuyển hướng, nhưng
chúng không thay đổi trang. Nếu bạn muốn làm cho trang thay đổi bạn có thể
kiểm tra phản hồi và áp dụng chuyển hướng thủ công.

.. code-block:: javascript

    fetch("/login", {"body": ...}).then(
        response => {
            if (response.redirected) {
                window.location = response.url
            } else {
                showLoginError()
            }
        }
    )


Thay thế Nội dung
-----------------

Một phản hồi có thể là HTML mới, hoặc là một phần mới của trang để thêm hoặc
thay thế, hoặc một trang hoàn toàn mới. Nói chung, nếu bạn đang trả về
toàn bộ trang, sẽ tốt hơn nếu xử lý điều đó bằng một chuyển hướng như được hiển thị
trong phần trước. Ví dụ sau đây chỉ ra cách thay thế một
``<div>`` bằng HTML được trả về bởi một request.

.. code-block:: html

    <div id="geology-fact">
        {{ include "geology_fact.html" }}
    </div>
    <script>
        const geology_url = {{ url_for("geology_fact")|tojson }}
        const geology_div = getElementById("geology-fact")
        fetch(geology_url)
            .then(response => response.text)
            .then(text => geology_div.innerHTML = text)
    </script>


Trả về JSON từ Views
--------------------

Để trả về một đối tượng JSON từ API view của bạn, bạn có thể trực tiếp trả về một
dict từ view. Nó sẽ được tuần tự hóa thành JSON một cách tự động.

.. code-block:: python

    @app.route("/user/<int:id>")
    def user_detail(id):
        user = User.query.get_or_404(id)
        return {
            "username": User.username,
            "email": User.email,
            "picture": url_for("static", filename=f"users/{id}/profile.png"),
        }

Nếu bạn muốn trả về một loại JSON khác, hãy sử dụng hàm
:func:`~flask.json.jsonify`, hàm này tạo ra một đối tượng phản hồi
với dữ liệu đã cho được tuần tự hóa thành JSON.

.. code-block:: python

    from flask import jsonify

    @app.route("/users")
    def user_list():
        users = User.query.order_by(User.name).all()
        return jsonify([u.to_json() for u in users])

Thường không phải là ý tưởng hay khi trả về dữ liệu tệp trong một phản hồi JSON.
JSON không thể đại diện cho dữ liệu nhị phân trực tiếp, vì vậy nó phải được mã hóa
base64, điều này có thể chậm, tốn nhiều băng thông hơn để gửi, và không
dễ cache. Thay vào đó, hãy phục vụ các tệp bằng cách sử dụng một view, và tạo một URL
đến tệp mong muốn để bao gồm trong JSON. Sau đó client có thể thực hiện một
request riêng biệt để lấy tài nguyên được liên kết sau khi nhận được JSON.


Nhận JSON trong Views
---------------------

Sử dụng thuộc tính :attr:`~flask.Request.json` của đối tượng
:data:`~flask.request` để giải mã body của request dưới dạng JSON. Nếu
body không phải là JSON hợp lệ, hoặc header ``Content-Type`` không được đặt thành
``application/json``, một lỗi 400 Bad Request sẽ được đưa ra.

.. code-block:: python

    from flask import request

    @app.post("/user/<int:id>")
    def user_update(id):
        user = User.query.get_or_404(id)
        user.update_from_json(request.json)
        db.session.commit()
        return user.to_json()
