Ví dụ JavaScript Ajax
=======================

Minh họa cách gửi dữ liệu biểu mẫu và xử lý phản hồi JSON bằng
JavaScript. Điều này cho phép thực hiện các yêu cầu mà không cần điều hướng khỏi
trang. Minh họa việc sử dụng |fetch|_, |XMLHttpRequest|_, và
|jQuery.ajax|_. Xem `tài liệu Flask`_ về JavaScript và Ajax.

.. |fetch| replace:: ``fetch``
.. _fetch: https://developer.mozilla.org/en-US/docs/Web/API/WindowOrWorkerGlobalScope/fetch

.. |XMLHttpRequest| replace:: ``XMLHttpRequest``
.. _XMLHttpRequest: https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest

.. |jQuery.ajax| replace:: ``jQuery.ajax``
.. _jQuery.ajax: https://api.jquery.com/jQuery.ajax/

.. _tài liệu Flask: https://flask.palletsprojects.com/patterns/javascript/


Cài đặt
-------

.. code-block:: text

    $ python3 -m venv .venv
    $ . .venv/bin/activate
    $ pip install -e .


Chạy
----

.. code-block:: text

    $ flask --app js_example run

Mở http://127.0.0.1:5000 trong trình duyệt.


Kiểm thử
--------

.. code-block:: text

    $ pip install -e '.[test]'
    $ coverage run -m pytest
    $ coverage report
