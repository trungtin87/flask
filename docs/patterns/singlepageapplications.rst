Ứng dụng Một Trang (Single-Page Applications)
==============================================

Flask có thể được sử dụng để phục vụ các Ứng dụng Một Trang (SPA) bằng cách đặt các file tĩnh
được tạo ra bởi framework frontend của bạn trong một thư mục con bên trong
dự án của bạn. Bạn cũng sẽ cần tạo một endpoint bắt tất cả định tuyến tất cả
các request đến SPA của bạn.

Ví dụ sau đây minh họa cách phục vụ một SPA cùng với một API::

    from flask import Flask, jsonify

    app = Flask(__name__, static_folder='app', static_url_path="/app")


    @app.route("/heartbeat")
    def heartbeat():
        return jsonify({"status": "healthy"})


    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return app.send_static_file("index.html")
