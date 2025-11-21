import os

from flask import Flask


def create_app(test_config=None):
    """Tạo và cấu hình một thể hiện của ứng dụng Flask."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # một bí mật mặc định nên được ghi đè bởi cấu hình thể hiện
        SECRET_KEY="dev",
        # lưu trữ cơ sở dữ liệu trong thư mục thể hiện
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # tải cấu hình thể hiện, nếu nó tồn tại, khi không kiểm thử
        app.config.from_pyfile("config.py", silent=True)
    else:
        # tải cấu hình kiểm thử nếu được truyền vào
        app.config.update(test_config)

    # đảm bảo thư mục thể hiện tồn tại
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/hello")
    def hello():
        return "Xin chào, Thế giới!"

    # register the database commands
    from . import db

    db.init_app(app)

    # apply the blueprints to the app
    from . import auth
    from . import blog

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule("/", endpoint="index")

    return app
