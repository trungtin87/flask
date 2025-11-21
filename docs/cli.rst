Giao diện Dòng Lệnh Flask
==========================

Cài đặt Flask sẽ cài đặt script ``flask`` – một giao diện dòng lệnh dựa trên `Click`_ – trong môi trường ảo của bạn. Khi chạy từ terminal, script này cho phép truy cập các lệnh tích hợp, các lệnh mở rộng và các lệnh do ứng dụng định nghĩa. Tùy chọn ``--help`` sẽ cung cấp thông tin chi tiết về bất kỳ lệnh và tùy chọn nào.

.. _Click: https://click.palletsprojects.com/

Khám phá Ứng dụng
-------------------

Lệnh ``flask`` được cài đặt bởi Flask, không phải bởi ứng dụng của bạn; vì vậy nó cần biết nơi tìm ứng dụng để sử dụng. Tùy chọn ``--app`` được dùng để chỉ định cách tải ứng dụng. 

Mặc dù ``--app`` hỗ trợ nhiều cách chỉ định ứng dụng, hầu hết các trường hợp nên đơn giản. Dưới đây là các giá trị thường dùng:

- (không có gì)
    Tên ``app`` hoặc ``wsgi`` được import (dưới dạng file ``.py`` hoặc package), tự động phát hiện một app (``app`` hoặc ``application``) hoặc một factory (``create_app`` hoặc ``make_app``).
- ``--app hello``
    Tên được import, tự động phát hiện một app (``app`` hoặc ``application``) hoặc một factory (``create_app`` hoặc ``make_app``).

----

``--app`` có ba phần: một đường dẫn tùy chọn để đặt thư mục làm việc hiện tại, một file Python hoặc đường dẫn import dạng dotted, và một tên biến tùy chọn của instance hoặc factory. Nếu tên là một factory, có thể theo sau là các đối số trong dấu ngoặc. Các ví dụ sau minh họa các phần này:

- ``--app src/hello``
    Đặt thư mục làm việc hiện tại thành ``src`` rồi import ``hello``.
- ``--app hello.web``
    Import đường dẫn ``hello.web``.
- ``--app hello:app2``
    Sử dụng instance Flask ``app2`` trong module ``hello``.
- ``--app 'hello:create_app("dev")'``
    Gọi factory ``create_app`` trong ``hello`` với đối số chuỗi ``"dev"``.

Nếu không đặt ``--app``, lệnh sẽ cố gắng import ``app`` hoặc ``wsgi`` (dưới dạng file ``.py`` hoặc package) và tự động phát hiện một instance hoặc factory. Trong import được cung cấp, lệnh sẽ tìm một instance có tên ``app`` hoặc ``application`` trước, sau đó bất kỳ instance nào. Nếu không tìm thấy, lệnh sẽ tìm một factory ``create_app`` hoặc ``make_app`` trả về một instance.

Nếu có dấu ngoặc sau tên factory, nội dung trong ngoặc sẽ được phân tích như các literal Python và truyền vào hàm. Điều này có nghĩa các chuỗi vẫn phải được đặt trong dấu ngoặc.

Chạy Máy Chủ Phát Triển
--------------------------

Lệnh :func:`run <cli.run_command>` sẽ khởi động máy chủ phát triển. Nó thay thế phương thức :meth:`Flask.run` trong hầu hết các trường hợp.

::

    $ flask --app hello run
     * Serving Flask app "hello"
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

.. warning:: Không sử dụng lệnh này để chạy ứng dụng trong môi trường production. Chỉ dùng máy chủ phát triển trong quá trình phát triển. Máy chủ phát triển chỉ mang lại tiện lợi, nhưng không được thiết kế để an toàn, ổn định hoặc hiệu quả. Xem :doc:`/deploying/index` để biết cách chạy trong production.

Nếu một chương trình khác đã sử dụng cổng 5000, bạn sẽ thấy ``OSError: [Errno 98]`` hoặc ``OSError: [WinError 10013]`` khi máy chủ cố gắng khởi động. Xem :ref:`address-already-in-use` để xử lý.

Chế Độ Gỡ Lỗi
----------------

Trong chế độ gỡ lỗi, lệnh ``flask run`` sẽ bật debugger tương tác và reloader mặc định, và làm cho lỗi dễ thấy và gỡ lỗi hơn. Để bật chế độ gỡ lỗi, dùng tùy chọn ``--debug``.

.. code-block:: console

    $ flask --app hello run --debug
     * Serving Flask app "hello"
     * Debug mode: on
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
     * Restarting with inotify reloader
     * Debugger is active!
     * Debugger PIN: 223-456-919

Tùy chọn ``--debug`` cũng có thể được truyền vào lệnh ``flask`` cấp cao để bật chế độ gỡ lỗi cho bất kỳ lệnh nào. Hai lệnh ``run`` sau đây là tương đương:

.. code-block:: console

    $ flask --app hello --debug run
    $ flask --app hello run --debug

Theo Dõi và Bỏ Qua Các Tệp Khi Reload
--------------------------------------

Khi dùng chế độ gỡ lỗi, reloader sẽ kích hoạt mỗi khi mã Python hoặc các module được import thay đổi. Reloader có thể theo dõi các tệp bổ sung bằng tùy chọn ``--extra-files``. Các đường dẫn được phân tách bằng ``:`` (hoặc ``;`` trên Windows).

.. code-block:: text

    $ flask run --extra-files file1:dirA/file2:dirB/
     * Running on http://127.0.0.1:8000/
     * Detected change in '/path/to/file1', reloading

Reloader cũng có thể bỏ qua các tệp bằng các mẫu ``fnmatch`` qua tùy chọn ``--exclude-patterns``. Các mẫu được phân tách bằng ``:`` (hoặc ``;`` trên Windows).

Mở Shell
----------

Để khám phá dữ liệu trong ứng dụng, bạn có thể khởi động một Python shell tương tác bằng lệnh :func:`shell <cli.shell_command>`. Một context ứng dụng sẽ được kích hoạt, và instance app sẽ được import.

::

    $ flask shell
    Python 3.10.0 (default, Oct 27 2021, 06:59:51) [GCC 11.1.0] on linux
    App: example [production]
    Instance: /home/david/Projects/pallets/flask/instance
    >>>

Sử dụng :meth:`~Flask.shell_context_processor` để tự động import các đối tượng khác.

Biến Môi Trường Từ dotenv
--------------------------

Lệnh ``flask`` hỗ trợ thiết lập bất kỳ tùy chọn nào cho bất kỳ lệnh nào bằng biến môi trường. Các biến được đặt dạng ``FLASK_OPTION`` hoặc ``FLASK_COMMAND_OPTION``; ví dụ ``FLASK_APP`` hoặc ``FLASK_RUN_PORT``.

Thay vì truyền tùy chọn mỗi lần chạy lệnh, hoặc thiết lập biến môi trường mỗi lần mở terminal, bạn có thể sử dụng hỗ trợ dotenv của Flask để tự động thiết lập biến môi trường từ các file ``.env`` và ``.flaskenv``.

Nếu cài đặt ``python-dotenv`` thì lệnh ``flask`` sẽ đọc các biến từ các file này. Bạn cũng có thể chỉ định một file bổ sung để tải bằng tùy chọn ``--env-file``.

Các biến trong ``.env`` không nên được commit vào repository vì chúng có thể chứa thông tin nhạy cảm; ``.flaskenv`` nên chứa các biến công khai như ``FLASK_APP``.

Các thư mục được quét lên trên từ thư mục bạn gọi ``flask`` để tìm các file này.

Các file chỉ được tải bởi lệnh ``flask`` hoặc khi gọi :meth:`~Flask.run`. Nếu muốn tải chúng trong production, hãy gọi :func:`~cli.load_dotenv` thủ công.

Cài Đặt Các Lệnh
-----------------

Click được cấu hình để tải giá trị mặc định cho các tùy chọn lệnh từ biến môi trường. Các biến sử dụng mẫu ``FLASK_COMMAND_OPTION``. Ví dụ, để đặt cổng cho lệnh run, thay vì ``flask run --port 8000``:

.. tabs::

    .. group-tab:: Bash

        .. code-block:: text

            $ export FLASK_RUN_PORT=8000
            $ flask run
            * Running on http://127.0.0.1:8000/

    .. group-tab:: Fish

        .. code-block:: text

            $ set -x FLASK_RUN_PORT 8000
            $ flask run
            * Running on http://127.0.0.1:8000/

    .. group-tab:: CMD

        .. code-block:: text

            > set FLASK_RUN_PORT=8000
            > flask run
            * Running on http://127.0.0.1:8000/

    .. group-tab:: Powershell

        .. code-block:: text

            > $env:FLASK_RUN_PORT = 8000
            > flask run
            * Running on http://127.0.0.1:8000/

Các tùy chọn này có thể được thêm vào file ``.flaskenv`` giống như ``FLASK_APP`` để làm mặc định.

Tắt dotenv
----------

Lệnh ``flask`` sẽ hiển thị thông báo nếu phát hiện file ``.env`` nhưng không cài đặt ``python-dotenv``. Để tắt việc tải file ``.env`` ngay cả khi ``python-dotenv`` đã cài, đặt biến môi trường ``FLASK_SKIP_DOTENV``.

.. code-block:: bash

    $ flask run
     * Tip: There are .env files present. Do "pip install python-dotenv" to use them.

Cài đặt ``FLASK_SKIP_DOTENV=1`` sẽ ngăn Flask tải file ``.env``.

.. tabs::

    .. group-tab:: Bash

        .. code-block:: text

            $ export FLASK_SKIP_DOTENV=1
            $ flask run

    .. group-tab:: Fish

        .. code-block:: text

            $ set -x FLASK_SKIP_DOTENV 1
            $ flask run

    .. group-tab:: CMD

        .. code-block:: text

            > set FLASK_SKIP_DOTENV=1
            > flask run

    .. group-tab:: Powershell

        .. code-block:: text

            > $env:FLASK_SKIP_DOTENV = 1
            > flask run

