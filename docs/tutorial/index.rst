Tutorial
========

.. toctree::
    :caption: Contents:
    :maxdepth: 1

    layout
    factory
    database
    views
    templates
    static
    blog
    install
    tests
    deploy
    next

Tutorial này sẽ hướng dẫn bạn tạo một ứng dụng blog cơ bản
có tên là Flaskr. Người dùng sẽ có thể đăng ký, đăng nhập, tạo bài viết,
và chỉnh sửa hoặc xóa bài viết của riêng họ. Bạn sẽ có thể đóng gói và
cài đặt ứng dụng trên các máy tính khác.

.. image:: flaskr_index.png
    :align: center
    :class: screenshot
    :alt: screenshot of index page

Giả định rằng bạn đã quen thuộc với Python. `Hướng dẫn chính thức`_
trong tài liệu Python là một cách tuyệt vời để học hoặc ôn tập trước.

.. _official tutorial: https://docs.python.org/3/tutorial/

Mặc dù được thiết kế để cung cấp một điểm khởi đầu tốt, tutorial không
bao gồm tất cả các tính năng của Flask. Hãy xem :doc:`/quickstart` để có
cái nhìn tổng quan về những gì Flask có thể làm, sau đó đi sâu vào tài liệu để tìm hiểu thêm.
Tutorial chỉ sử dụng những gì được cung cấp bởi Flask và Python. Trong một
dự án khác, bạn có thể quyết định sử dụng :doc:`/extensions` hoặc các thư viện khác
để làm cho một số tác vụ đơn giản hơn.

.. image:: flaskr_login.png
    :align: center
    :class: screenshot
    :alt: screenshot of login page

Flask rất linh hoạt. Nó không yêu cầu bạn sử dụng bất kỳ dự án cụ thể nào
hoặc bố cục mã. Tuy nhiên, khi mới bắt đầu, sẽ hữu ích khi sử dụng một
cách tiếp cận có cấu trúc hơn. Điều này có nghĩa là tutorial sẽ yêu cầu một chút
boilerplate ngay từ đầu, nhưng nó được thực hiện để tránh nhiều cạm bẫy phổ biến mà
các nhà phát triển mới gặp phải, và nó tạo ra một dự án dễ mở rộng.
Khi bạn trở nên thoải mái hơn với Flask, bạn có thể thoát khỏi
cấu trúc này và tận dụng đầy đủ tính linh hoạt của Flask.

.. image:: flaskr_edit.png
    :align: center
    :class: screenshot
    :alt: screenshot of edit page

:gh:`Dự án tutorial có sẵn dưới dạng ví dụ trong kho lưu trữ Flask
<examples/tutorial>`, nếu bạn muốn so sánh dự án của mình
với sản phẩm cuối cùng khi bạn làm theo tutorial.

Tiếp tục đến :doc:`layout`.
