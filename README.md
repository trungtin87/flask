<div align="center"><img src="https://raw.githubusercontent.com/pallets/flask/refs/heads/stable/docs/_static/flask-name.svg" alt="" height="150"></div>

# Flask

Flask là một framework ứng dụng web [WSGI] nhẹ. Nó được thiết kế
để giúp bắt đầu nhanh chóng và dễ dàng, với khả năng mở rộng lên
các ứng dụng phức tạp. Nó bắt đầu như một wrapper đơn giản xung quanh [Werkzeug]
và [Jinja], và đã trở thành một trong những framework ứng dụng web Python phổ biến nhất.

Flask đưa ra các gợi ý, nhưng không bắt buộc bất kỳ phụ thuộc hoặc
bố cục dự án nào. Việc lựa chọn các công cụ và thư viện muốn sử dụng
là tùy thuộc vào nhà phát triển. Có rất nhiều tiện ích mở rộng được cung cấp bởi
cộng đồng giúp việc thêm chức năng mới trở nên dễ dàng.

[WSGI]: https://wsgi.readthedocs.io/
[Werkzeug]: https://werkzeug.palletsprojects.com/
[Jinja]: https://jinja.palletsprojects.com/

## Một Ví dụ Đơn giản

```python
# lưu tệp này dưới tên app.py
from flask import Flask

app = Flask(__name__)

@app.route("/")
def xichao():
    return "Xin chào, thế giới!"
```

```
$ flask run
  * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

## Quyên góp

Tổ chức Pallets phát triển và hỗ trợ Flask cùng các thư viện
mà nó sử dụng. Để phát triển cộng đồng những người đóng góp và người dùng, và
cho phép các nhà bảo trì dành nhiều thời gian hơn cho các dự án, [vui lòng
quyên góp ngay hôm nay].

[vui lòng quyên góp ngay hôm nay]: https://palletsprojects.com/donate

## Đóng góp

Xem [tài liệu đóng góp chi tiết][contrib] của chúng tôi để biết nhiều cách
đóng góp, bao gồm báo cáo lỗi, yêu cầu tính năng, đặt câu hỏi hoặc trả lời
câu hỏi, và tạo PR.

[contrib]: https://palletsprojects.com/contributing/
