File Tĩnh (Static Files)
========================

Các view và template xác thực hoạt động, nhưng chúng trông rất đơn giản
hiện tại. Một số `CSS`_ có thể được thêm vào để thêm kiểu cho bố cục HTML bạn
đã xây dựng. Kiểu sẽ không thay đổi, vì vậy nó là một file *tĩnh* thay vì
một template.

Flask tự động thêm một view ``static`` nhận một đường dẫn tương đối
đến thư mục ``flaskr/static`` và phục vụ nó. Template ``base.html``
đã có một liên kết đến file ``style.css``:

.. code-block:: html+jinja

    {{ url_for('static', filename='style.css') }}

Bên cạnh CSS, các loại file tĩnh khác có thể là các file với các hàm JavaScript
, hoặc một hình ảnh logo. Tất cả chúng đều được đặt dưới thư mục
``flaskr/static`` và được tham chiếu với
``url_for('static', filename='...')``.

Tutorial này không tập trung vào cách viết CSS, vì vậy bạn chỉ cần sao chép
nội dung sau vào file ``flaskr/static/style.css``:

.. code-block:: css
    :caption: ``flaskr/static/style.css``

    html { font-family: sans-serif; background: #eee; padding: 1rem; }
    body { max-width: 960px; margin: 0 auto; background: white; }
    h1 { font-family: serif; color: #377ba8; margin: 1rem 0; }
    a { color: #377ba8; }
    hr { border: none; border-top: 1px solid lightgray; }
    nav { background: lightgray; display: flex; align-items: center; padding: 0 0.5rem; }
    nav h1 { flex: auto; margin: 0; }
    nav h1 a { text-decoration: none; padding: 0.25rem 0.5rem; }
    nav ul  { display: flex; list-style: none; margin: 0; padding: 0; }
    nav ul li a, nav ul li span, header .action { display: block; padding: 0.5rem; }
    .content { padding: 0 1rem 1rem; }
    .content > header { border-bottom: 1px solid lightgray; display: flex; align-items: flex-end; }
    .content > header h1 { flex: auto; margin: 1rem 0 0.25rem 0; }
    .flash { margin: 1em 0; padding: 1em; background: #cae6f6; border: 1px solid #377ba8; }
    .post > header { display: flex; align-items: flex-end; font-size: 0.85em; }
    .post > header > div:first-of-type { flex: auto; }
    .post > header h1 { font-size: 1.5em; margin-bottom: 0; }
    .post .about { color: slategray; font-style: italic; }
    .post .body { white-space: pre-line; }
    .content:last-child { margin-bottom: 0; }
    .content form { margin: 1em 0; display: flex; flex-direction: column; }
    .content label { font-weight: bold; margin-bottom: 0.5em; }
    .content input, .content textarea { margin-bottom: 1em; }
    .content textarea { min-height: 12em; resize: vertical; }
    input.danger { color: #cc2f2e; }
    input[type=submit] { align-self: start; min-width: 10em; }

Bạn có thể tìm thấy một phiên bản ít compact hơn của ``style.css`` trong
:gh:`mã ví dụ <examples/tutorial/flaskr/static/style.css>`.

Truy cập http://127.0.0.1:5000/auth/login và trang sẽ trông giống như
ảnh chụp màn hình bên dưới.

.. image:: flaskr_login.png
    :align: center
    :class: screenshot
    :alt: screenshot of login page

Bạn có thể đọc thêm về CSS từ `tài liệu của Mozilla <CSS_>`_. Nếu
bạn thay đổi một file tĩnh, hãy làm mới trang trình duyệt. Nếu thay đổi
không hiển thị, hãy thử xóa cache của trình duyệt.

.. _CSS: https://developer.mozilla.org/docs/Web/CSS

Tiếp tục đến :doc:`blog`.
