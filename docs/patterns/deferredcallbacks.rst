Deferred Request Callbacks
==========================

Một trong những nguyên tắc thiết kế của Flask là các đối tượng phản hồi được tạo ra và
truyền xuống một chuỗi các callback tiềm năng có thể sửa đổi chúng hoặc thay thế
chúng. Khi việc xử lý request bắt đầu, chưa có đối tượng phản hồi nào. Nó được
tạo ra khi cần thiết bởi một view function hoặc bởi một số thành phần khác trong
hệ thống.

Điều gì xảy ra nếu bạn muốn sửa đổi phản hồi tại một điểm mà phản hồi
chưa tồn tại? Một ví dụ phổ biến cho điều đó sẽ là một callback
:meth:`~flask.Flask.before_request` muốn đặt một cookie trên
đối tượng phản hồi.

Một cách là tránh tình huống này. Rất thường xuyên điều đó là có thể. Ví dụ
bạn có thể cố gắng di chuyển logic đó vào một callback :meth:`~flask.Flask.after_request`
thay thế. Tuy nhiên, đôi khi việc di chuyển mã đến đó làm cho nó
phức tạp hơn hoặc khó xử lý hơn.

Như một giải pháp thay thế, bạn có thể sử dụng :func:`~flask.after_this_request` để đăng ký
các callback sẽ thực thi chỉ sau request hiện tại. Bằng cách này bạn có thể
trì hoãn việc thực thi mã từ bất kỳ đâu trong ứng dụng, dựa trên request
hiện tại.

Bất cứ lúc nào trong một request, chúng ta có thể đăng ký một hàm để được gọi vào
cuối request. Ví dụ bạn có thể ghi nhớ ngôn ngữ hiện tại của
người dùng trong một cookie trong một callback :meth:`~flask.Flask.before_request`::

    from flask import request, after_this_request

    @app.before_request
    def detect_user_language():
        language = request.cookies.get('user_lang')

        if language is None:
            language = guess_language_from_request()

            # khi phản hồi tồn tại, đặt một cookie với ngôn ngữ
            @after_this_request
            def remember_language(response):
                response.set_cookie('user_lang', language)
                return response

        g.language = language
