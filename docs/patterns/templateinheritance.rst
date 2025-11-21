Kế thừa Template (Template Inheritance)
========================================

Phần mạnh mẽ nhất của Jinja là kế thừa template. Kế thừa template
cho phép bạn xây dựng một template "bộ xương" cơ sở chứa tất cả các phần tử
chung của trang web của bạn và định nghĩa các **block** mà các template con có thể ghi đè.

Nghe có vẻ phức tạp nhưng rất cơ bản. Dễ hiểu nhất là bắt đầu
với một ví dụ.


Template Cơ sở
--------------

Template này, mà chúng ta sẽ gọi là :file:`layout.html`, định nghĩa một bộ xương HTML đơn giản
document mà bạn có thể sử dụng cho một trang hai cột đơn giản. Nhiệm vụ của
các template "con" là điền nội dung vào các block trống:

.. sourcecode:: html+jinja

    <!doctype html>
    <html>
      <head>
        {% block head %}
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        <title>{% block title %}{% endblock %} - My Webpage</title>
        {% endblock %}
      </head>
      <body>
        <div id="content">{% block content %}{% endblock %}</div>
        <div id="footer">
          {% block footer %}
          &copy; Copyright 2010 by <a href="http://domain.invalid/">you</a>.
          {% endblock %}
        </div>
      </body>
    </html>

Trong ví dụ này, các thẻ ``{% block %}`` định nghĩa bốn block mà các template con
có thể điền vào. Tất cả những gì thẻ `block` làm là cho engine template biết rằng một
template con có thể ghi đè những phần đó của template.

Template Con
------------

Một template con có thể trông như thế này:

.. sourcecode:: html+jinja

    {% extends "layout.html" %}
    {% block title %}Index{% endblock %}
    {% block head %}
      {{ super() }}
      <style type="text/css">
        .important { color: #336699; }
      </style>
    {% endblock %}
    {% block content %}
      <h1>Index</h1>
      <p class="important">
        Welcome on my awesome homepage.
    {% endblock %}

Thẻ ``{% extends %}`` là chìa khóa ở đây. Nó cho engine template biết rằng
template này "mở rộng" một template khác. Khi hệ thống template đánh giá
template này, đầu tiên nó xác định vị trí cha. Thẻ extends phải là
thẻ đầu tiên trong template. Để render nội dung của một block được định nghĩa trong
template cha, sử dụng ``{{ super() }}``.
