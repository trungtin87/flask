Cài đặt
=======


Phiên bản Python
----------------

Chúng tôi khuyên bạn nên sử dụng phiên bản Python mới nhất. Flask hỗ trợ Python 3.10 trở lên.


Các phụ thuộc
-------------

Các bản phân phối này sẽ được cài đặt tự động khi cài đặt Flask.

* `Werkzeug`_ triển khai WSGI, giao diện Python tiêu chuẩn giữa
  các ứng dụng và máy chủ.
* `Jinja`_ là một ngôn ngữ template dùng để render các trang mà ứng dụng của bạn
  phục vụ.
* `MarkupSafe`_ đi kèm với Jinja. Nó escape đầu vào không tin cậy khi render
  template để tránh các cuộc tấn công injection.
* `ItsDangerous`_ ký dữ liệu một cách an toàn để đảm bảo tính toàn vẹn của nó. Điều này được sử dụng
  để bảo vệ cookie phiên của Flask.
* `Click`_ là một framework để viết các ứng dụng dòng lệnh. Nó cung cấp
  lệnh ``flask`` và cho phép thêm các lệnh quản lý tùy chỉnh.
* `Blinker`_ cung cấp hỗ trợ cho :doc:`signals`.

.. _Werkzeug: https://palletsprojects.com/p/werkzeug/
.. _Jinja: https://palletsprojects.com/p/jinja/
.. _MarkupSafe: https://palletsprojects.com/p/markupsafe/
.. _ItsDangerous: https://palletsprojects.com/p/itsdangerous/
.. _Click: https://palletsprojects.com/p/click/
.. _Blinker: https://blinker.readthedocs.io/


Các phụ thuộc tùy chọn
~~~~~~~~~~~~~~~~~~~~~~

Các bản phân phối này sẽ không được cài đặt tự động. Flask sẽ phát hiện và
sử dụng chúng nếu bạn cài đặt chúng.

* `python-dotenv`_ kích hoạt hỗ trợ cho :ref:`dotenv` khi chạy các lệnh
  ``flask``.
* `Watchdog`_ cung cấp trình tải lại nhanh hơn, hiệu quả hơn cho máy chủ
  phát triển.

.. _python-dotenv: https://github.com/theskumar/python-dotenv#readme
.. _watchdog: https://pythonhosted.org/watchdog/


greenlet
~~~~~~~~

Bạn có thể chọn sử dụng gevent hoặc eventlet với ứng dụng của mình. Trong trường hợp
này, greenlet>=1.0 là bắt buộc. Khi sử dụng PyPy, PyPy>=7.3.7 là
bắt buộc.

Đây không phải là các phiên bản được hỗ trợ tối thiểu, chúng chỉ chỉ ra các phiên bản
đầu tiên đã thêm các tính năng cần thiết. Bạn nên sử dụng các phiên bản
mới nhất của mỗi loại.


Môi trường ảo
-------------

Sử dụng môi trường ảo để quản lý các phụ thuộc cho dự án của bạn, cả trong
phát triển và trong sản xuất.

Môi trường ảo giải quyết vấn đề gì? Càng có nhiều dự án Python,
bạn càng có nhiều khả năng cần làm việc với các phiên bản khác nhau của
các thư viện Python, hoặc thậm chí chính Python. Các phiên bản mới hơn của thư viện cho một
dự án có thể phá vỡ khả năng tương thích trong một dự án khác.

Môi trường ảo là các nhóm thư viện Python độc lập, một cho mỗi
dự án. Các gói được cài đặt cho một dự án sẽ không ảnh hưởng đến các dự án khác hoặc
các gói của hệ điều hành.

Python đi kèm với module :mod:`venv` để tạo các môi trường
ảo.


.. _install-create-env:

Tạo một môi trường
~~~~~~~~~~~~~~~~~~

Tạo một thư mục dự án và một thư mục :file:`.venv` bên trong:

.. tabs::

   .. group-tab:: macOS/Linux

      .. code-block:: text

         $ mkdir myproject
         $ cd myproject
         $ python3 -m venv .venv

   .. group-tab:: Windows

      .. code-block:: text

         > mkdir myproject
         > cd myproject
         > py -3 -m venv .venv


.. _install-activate-env:

Kích hoạt môi trường
~~~~~~~~~~~~~~~~~~~~

Trước khi bạn làm việc trên dự án của mình, hãy kích hoạt môi trường tương ứng:

.. tabs::

   .. group-tab:: macOS/Linux

      .. code-block:: text

         $ . .venv/bin/activate

   .. group-tab:: Windows

      .. code-block:: text

         > .venv\Scripts\activate

Dấu nhắc shell của bạn sẽ thay đổi để hiển thị tên của môi trường
đã kích hoạt.


Cài đặt Flask
-------------

Trong môi trường đã kích hoạt, sử dụng lệnh sau để cài đặt
Flask:

.. code-block:: sh

    $ pip install Flask

Flask hiện đã được cài đặt. Xem :doc:`/quickstart` hoặc đi đến
:doc:`Tổng quan Tài liệu </index>`.
