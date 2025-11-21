Phân lớp Flask (Subclassing Flask)
==================================

Class :class:`~flask.Flask` được thiết kế để phân lớp.

Ví dụ, bạn có thể muốn ghi đè cách các tham số request được xử lý để bảo toàn thứ tự của chúng::

    from flask import Flask, Request
    from werkzeug.datastructures import ImmutableOrderedMultiDict
    class MyRequest(Request):
        """Request subclass để ghi đè lưu trữ tham số request"""
        parameter_storage_class = ImmutableOrderedMultiDict
    class MyFlask(Flask):
        """Flask subclass sử dụng custom request class"""
        request_class = MyRequest

Đây là cách tiếp cận được khuyến nghị để ghi đè hoặc tăng cường chức năng nội bộ của Flask.
