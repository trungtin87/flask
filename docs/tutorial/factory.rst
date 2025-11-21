.. currentmodule:: flask

Thiết lập Ứng dụng
==================

Một ứng dụng Flask là một instance của class :class:`Flask`.
Mọi thứ về ứng dụng, chẳng hạn như cấu hình và URL, sẽ
được đăng ký với class này.

Cách đơn giản nhất để tạo một ứng dụng Flask là tạo
một instance :class:`Flask` toàn cục trực tiếp ở đầu mã của bạn, giống như
cách ví dụ "Hello, World!" đã làm ở trang trước. Mặc dù điều này
đơn giản và hữu ích trong một số trường hợp, nó có thể gây ra một số vấn đề khó khăn khi
dự án phát triển.

Thay vì tạo một instance :class:`Flask` toàn cục, bạn sẽ tạo
nó bên trong một hàm. Hàm này được gọi là *application
factory*. Bất kỳ cấu hình, đăng ký và thiết lập nào khác mà
ứng dụng cần sẽ xảy ra bên trong hàm, sau đó ứng dụng
sẽ được trả về.


Application Factory
-------------------

Đã đến lúc bắt đầu viết mã! Tạo thư mục ``flaskr`` và thêm
file ``__init__.py``. ``__init__.py`` phục vụ hai mục đích: nó sẽ
chứa application factory, và nó cho Python biết rằng thư mục ``flaskr``
nên được coi là một package.

.. code-block:: none

    $ mkdir flaskr

.. code-block:: python
    :caption: ``flaskr/__init__.py``

    import os

    from flask import Flask


    def create_app(test_config=None):
        # tạo và cấu hình app
        app = Flask(__name__, instance_relative_config=True)
        app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        )

        if test_config is None:
            # load instance config, nếu nó tồn tại, khi không kiểm thử
            app.config.from_pyfile('config.py', silent=True)
        else:
            # load test config nếu được truyền vào
            app.config.from_mapping(test_config)

        # đảm bảo instance folder tồn tại
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass

        # một trang đơn giản nói hello
        @app.route('/hello')
        def hello():
            return 'Hello, World!'

        return app

``create_app`` là hàm application factory. Bạn sẽ thêm vào nó
sau trong tutorial, nhưng nó đã làm rất nhiều việc rồi.

#.  ``app = Flask(__name__, instance_relative_config=True)`` tạo
    instance :class:`Flask`.

    *   ``__name__`` là tên của module Python hiện tại. Ứng dụng
        cần biết nó nằm ở đâu để thiết lập một số đường dẫn, và
        ``__name__`` là một cách thuận tiện để cho nó biết điều đó.

    *   ``instance_relative_config=True`` cho ứng dụng biết rằng
        các file cấu hình là tương đối với
        :ref:`instance folder <instance-folders>`. Instance folder
        nằm bên ngoài package ``flaskr`` và có thể chứa dữ liệu cục bộ
        không nên được commit vào version control, chẳng hạn như
        các secret cấu hình và file cơ sở dữ liệu.

#.  :meth:`app.config.from_mapping() <Config.from_mapping>` đặt
    một số cấu hình mặc định mà ứng dụng sẽ sử dụng:

    *   :data:`SECRET_KEY` được Flask và các extension sử dụng để giữ dữ liệu
        an toàn. Nó được đặt thành ``'dev'`` để cung cấp một giá trị thuận tiện
        trong quá trình phát triển, nhưng nó nên được ghi đè bằng một giá trị
        ngẫu nhiên khi triển khai.

    *   ``DATABASE`` là đường dẫn nơi file cơ sở dữ liệu SQLite sẽ được
        lưu. Nó nằm dưới
        :attr:`app.instance_path <Flask.instance_path>`, là
        đường dẫn mà Flask đã chọn cho instance folder. Bạn sẽ tìm hiểu
        thêm về cơ sở dữ liệu trong phần tiếp theo.

#.  :meth:`app.config.from_pyfile() <Config.from_pyfile>` ghi đè
    cấu hình mặc định với các giá trị được lấy từ file ``config.py``
    trong instance folder nếu nó tồn tại. Ví dụ, khi
    triển khai, điều này có thể được sử dụng để đặt một ``SECRET_KEY`` thực.

    *   ``test_config`` cũng có thể được truyền cho factory, và sẽ được
        sử dụng thay vì cấu hình instance. Điều này là để các bài kiểm tra
        bạn sẽ viết sau trong tutorial có thể được cấu hình
        độc lập với bất kỳ giá trị phát triển nào bạn đã cấu hình.

#.  :func:`os.makedirs` đảm bảo rằng
    :attr:`app.instance_path <Flask.instance_path>` tồn tại. Flask
    không tự động tạo instance folder, nhưng nó cần được
    tạo vì dự án của bạn sẽ tạo file cơ sở dữ liệu SQLite
    ở đó.

#.  :meth:`@app.route() <Flask.route>` tạo một route đơn giản để bạn có thể
    thấy ứng dụng hoạt động trước khi đi vào phần còn lại của
    tutorial. Nó tạo một kết nối giữa URL ``/hello`` và một
    hàm trả về một phản hồi, chuỗi ``'Hello, World!'`` trong
    trường hợp này.


Chạy Ứng dụng
-------------

Bây giờ bạn có thể chạy ứng dụng của mình bằng lệnh ``flask``. Từ
terminal, cho Flask biết nơi tìm ứng dụng của bạn, sau đó chạy nó trong
chế độ debug. Hãy nhớ rằng, bạn vẫn nên ở trong thư mục
``flask-tutorial`` cấp cao nhất, không phải package ``flaskr``.

Chế độ debug hiển thị một debugger tương tác bất cứ khi nào một trang đưa ra một
exception, và khởi động lại máy chủ bất cứ khi nào bạn thực hiện thay đổi đối với
mã. Bạn có thể để nó chạy và chỉ cần tải lại trang trình duyệt khi bạn
làm theo tutorial.

.. code-block:: text

    $ flask --app flaskr run --debug

Bạn sẽ thấy đầu ra tương tự như thế này:

.. code-block:: text

     * Serving Flask app "flaskr"
     * Debug mode: on
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
     * Restarting with stat
     * Debugger is active!
     * Debugger PIN: nnn-nnn-nnn

Truy cập http://127.0.0.1:5000/hello trong trình duyệt và bạn sẽ thấy
thông báo "Hello, World!". Chúc mừng, bạn hiện đang chạy ứng dụng
web Flask của mình!

Nếu một chương trình khác đã sử dụng cổng 5000, bạn sẽ thấy
``OSError: [Errno 98]`` hoặc ``OSError: [WinError 10013]`` khi
máy chủ cố gắng khởi động. Xem :ref:`address-already-in-use` để biết cách
xử lý điều đó.

Tiếp tục đến :doc:`database`.
