Caching
=======

Khi ứng dụng của bạn chạy chậm, hãy thêm một số cache vào. Chà, ít nhất
đó là cách dễ nhất để tăng tốc mọi thứ. Cache làm gì? Giả sử bạn
có một hàm mất một khoảng thời gian để hoàn thành nhưng kết quả sẽ
vẫn đủ tốt nếu chúng cũ 5 phút. Vì vậy, ý tưởng là
bạn thực sự đặt kết quả của phép tính đó vào một cache trong một khoảng
thời gian.

Bản thân Flask không cung cấp caching cho bạn, nhưng `Flask-Caching`_, một
extension cho Flask thì có. Flask-Caching hỗ trợ nhiều backend khác nhau, và thậm chí
có thể phát triển backend caching của riêng bạn.


.. _Flask-Caching: https://flask-caching.readthedocs.io/en/latest/
