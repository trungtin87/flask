Tải lên Tệp (Uploading Files)
=============================

À vâng, vấn đề cũ kỹ tốt đẹp của việc tải lên tệp. Ý tưởng cơ bản của việc tải lên
tệp thực sự khá đơn giản. Về cơ bản nó hoạt động như thế này:

1. Một thẻ ``<form>`` được đánh dấu với ``enctype=multipart/form-data``
   và một ``<input type=file>`` được đặt trong form đó.
2. Ứng dụng truy cập tệp từ từ điển :attr:`~flask.request.files`
   trên đối tượng request.
3. sử dụng phương thức :meth:`~werkzeug.datastructures.FileStorage.save` của tệp để lưu
   tệp vĩnh viễn ở đâu đó trên hệ thống tệp.

Giới thiệu Nhẹ nhàng
--------------------

Hãy bắt đầu với một ứng dụng rất cơ bản tải lên một tệp vào một
thư mục tải lên cụ thể và hiển thị một tệp cho người dùng. Hãy xem
mã khởi động cho ứng dụng của chúng ta::

    import os
    from flask import Flask, flash, request, redirect, url_for
    from werkzeug.utils import secure_filename

    UPLOAD_FOLDER = '/path/to/the/uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Vì vậy, đầu tiên chúng ta cần một vài import. Hầu hết nên đơn giản,
:func:`werkzeug.secure_filename` được giải thích một chút sau đó.
``UPLOAD_FOLDER`` là nơi chúng ta sẽ lưu trữ các tệp đã tải lên và
``ALLOWED_EXTENSIONS`` là tập hợp các phần mở rộng tệp được phép.

Tại sao chúng ta giới hạn các phần mở rộng được phép? Bạn có thể không muốn
người dùng của mình có thể tải lên mọi thứ ở đó nếu máy chủ đang trực tiếp
gửi dữ liệu ra cho client. Bằng cách đó bạn có thể đảm bảo rằng người dùng
không thể tải lên các tệp HTML có thể gây ra các vấn đề XSS (xem
:ref:`security-xss`). Cũng hãy chắc chắn không cho phép các tệp ``.php`` nếu máy chủ
thực thi chúng, nhưng ai cài đặt PHP trên máy chủ của họ, phải không?  :)

Tiếp theo các hàm kiểm tra xem một phần mở rộng có hợp lệ không và tải lên
tệp và chuyển hướng người dùng đến URL cho tệp đã tải lên::

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            # kiểm tra xem post request có phần file không
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # Nếu người dùng không chọn tệp, trình duyệt gửi một
            # tệp trống không có tên tệp.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('download_file', name=filename))
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        '''

Vậy hàm :func:`~werkzeug.utils.secure_filename` thực sự làm gì?
Bây giờ vấn đề là có nguyên tắc gọi là "không bao giờ tin tưởng đầu vào của
người dùng". Điều này cũng đúng cho tên tệp của một tệp đã tải lên. Tất cả
dữ liệu form đã gửi có thể bị giả mạo, và tên tệp có thể nguy hiểm. Hiện tại
chỉ cần nhớ: luôn sử dụng hàm đó để bảo mật tên tệp
trước khi lưu trữ nó trực tiếp trên hệ thống tệp.

.. admonition:: Thông tin cho Chuyên gia

   Vậy bạn quan tâm đến việc hàm :func:`~werkzeug.utils.secure_filename` đó
   làm gì và vấn đề là gì nếu bạn không sử dụng nó? Vì vậy chỉ cần
   tưởng tượng ai đó sẽ gửi thông tin sau dưới dạng `filename` đến
   ứng dụng của bạn::

      filename = "../../../../home/username/.bashrc"

   Giả sử số lượng ``../`` là chính xác và bạn sẽ nối cái này với
   ``UPLOAD_FOLDER`` người dùng có thể có khả năng sửa đổi một tệp trên
   hệ thống tệp của máy chủ mà anh ấy hoặc cô ấy không nên sửa đổi. Điều này đòi hỏi một số
   kiến thức về ứng dụng trông như thế nào, nhưng hãy tin tôi, các hacker
   rất kiên nhẫn :)

   Bây giờ hãy xem hàm đó hoạt động như thế nào:

   >>> secure_filename('../../../../home/username/.bashrc')
   'home_username_.bashrc'

Chúng ta muốn có thể phục vụ các tệp đã tải lên để chúng có thể được tải xuống
bởi người dùng. Chúng ta sẽ định nghĩa một view ``download_file`` để phục vụ các tệp trong
thư mục tải lên theo tên. ``url_for("download_file", name=name)`` tạo ra
các URL tải xuống.

.. code-block:: python

    from flask import send_from_directory

    @app.route('/uploads/<name>')
    def download_file(name):
        return send_from_directory(app.config["UPLOAD_FOLDER"], name)

Nếu bạn đang sử dụng middleware hoặc máy chủ HTTP để phục vụ các tệp, bạn có thể
đăng ký endpoint ``download_file`` là ``build_only`` để ``url_for``
sẽ hoạt động mà không cần một view function.

.. code-block:: python

    app.add_url_rule(
        "/uploads/<name>", endpoint="download_file", build_only=True
    )


Cải thiện Tải lên
-----------------

.. versionadded:: 0.6

Vậy chính xác Flask xử lý việc tải lên như thế nào? Chà, nó sẽ lưu trữ chúng trong
bộ nhớ của máy chủ web nếu các tệp nhỏ hợp lý, nếu không thì ở một
vị trí tạm thời (như được trả về bởi :func:`tempfile.gettempdir`). Nhưng làm thế nào
bạn chỉ định kích thước tệp tối đa sau đó việc tải lên bị hủy bỏ? Theo
mặc định Flask sẽ vui vẻ chấp nhận tải lên tệp với lượng bộ nhớ
không giới hạn, nhưng bạn có thể giới hạn điều đó bằng cách đặt khóa cấu hình
``MAX_CONTENT_LENGTH``::

    from flask import Flask, Request

    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

Mã ở trên sẽ giới hạn payload tối đa được phép là 16 megabyte.
Nếu một tệp lớn hơn được truyền, Flask sẽ đưa ra một ngoại lệ
:exc:`~werkzeug.exceptions.RequestEntityTooLarge`.

.. admonition:: Vấn đề Reset Kết nối

    Khi sử dụng máy chủ phát triển cục bộ, bạn có thể nhận được lỗi reset
    kết nối thay vì phản hồi 413. Bạn sẽ nhận được phản hồi trạng thái
    chính xác khi chạy ứng dụng với một máy chủ WSGI sản xuất.

Tính năng này đã được thêm vào trong Flask 0.6 nhưng cũng có thể đạt được trong các phiên bản cũ hơn
bằng cách phân lớp đối tượng request. Để biết thêm thông tin về điều đó
tham khảo tài liệu Werkzeug về xử lý tệp.


Thanh Tiến trình Tải lên
------------------------

Một thời gian trước, nhiều nhà phát triển đã có ý tưởng đọc tệp đến trong
các đoạn nhỏ và lưu trữ tiến trình tải lên trong cơ sở dữ liệu để có thể
thăm dò tiến trình với JavaScript từ client. Client hỏi
máy chủ mỗi 5 giây xem nó đã truyền được bao nhiêu, nhưng đây là
điều mà nó đã nên biết.

Một Giải pháp Dễ dàng hơn
-------------------------

Bây giờ có những giải pháp tốt hơn hoạt động nhanh hơn và đáng tin cậy hơn. Có
các thư viện JavaScript như jQuery_ có các plugin form để dễ dàng
xây dựng thanh tiến trình.

Bởi vì mẫu chung cho việc tải lên tệp tồn tại gần như không thay đổi trong tất cả
các ứng dụng xử lý việc tải lên, cũng có một số extension Flask
triển khai một cơ chế tải lên đầy đủ cho phép kiểm soát những
phần mở rộng tệp nào được phép tải lên.

.. _jQuery: https://jquery.com/
