MongoDB với MongoEngine
=======================

Sử dụng một cơ sở dữ liệu document như MongoDB là một giải pháp thay thế phổ biến cho
các cơ sở dữ liệu SQL quan hệ. Mẫu này chỉ ra cách sử dụng
`MongoEngine`_, một thư viện ánh xạ document, để tích hợp với MongoDB.

Một máy chủ MongoDB đang chạy và `Flask-MongoEngine`_ là bắt buộc. ::

    pip install flask-mongoengine

.. _MongoEngine: http://mongoengine.org
.. _Flask-MongoEngine: https://flask-mongoengine.readthedocs.io


Cấu hình
--------

Thiết lập cơ bản có thể được thực hiện bằng cách định nghĩa ``MONGODB_SETTINGS`` trên
``app.config`` và tạo một instance ``MongoEngine``. ::

    from flask import Flask
    from flask_mongoengine import MongoEngine

    app = Flask(__name__)
    app.config['MONGODB_SETTINGS'] = {
        "db": "myapp",
    }
    db = MongoEngine(app)


Ánh xạ Document
---------------

Để khai báo một model đại diện cho một Mongo document, hãy tạo một class
kế thừa từ ``Document`` và khai báo từng field. ::

    import mongoengine as me

    class Movie(me.Document):
        title = me.StringField(required=True)
        year = me.IntField()
        rated = me.StringField()
        director = me.StringField()
        actors = me.ListField()

Nếu document có các field lồng nhau, sử dụng ``EmbeddedDocument`` để
định nghĩa các field của embedded document và
``EmbeddedDocumentField`` để khai báo nó trên document cha. ::

    class Imdb(me.EmbeddedDocument):
        imdb_id = me.StringField()
        rating = me.DecimalField()
        votes = me.IntField()

    class Movie(me.Document):
        ...
        imdb = me.EmbeddedDocumentField(Imdb)


Tạo Dữ liệu
-----------

Khởi tạo class document của bạn với các đối số từ khóa cho các field.
Bạn cũng có thể gán giá trị cho các thuộc tính field sau khi khởi tạo.
Sau đó gọi ``doc.save()``. ::

    bttf = Movie(title="Back To The Future", year=1985)
    bttf.actors = [
        "Michael J. Fox",
        "Christopher Lloyd"
    ]
    bttf.imdb = Imdb(imdb_id="tt0088763", rating=8.5)
    bttf.save()


Truy vấn (Queries)
------------------

Sử dụng thuộc tính ``objects`` của class để thực hiện truy vấn. Một đối số từ khóa
tìm kiếm một giá trị bằng nhau trên field. ::

    bttf = Movie.objects(title="Back To The Future").get_or_404()

Các toán tử truy vấn có thể được sử dụng bằng cách nối chúng với tên field
sử dụng dấu gạch dưới kép. ``objects``, và các truy vấn được trả về bởi
việc gọi nó, có thể lặp lại. ::

    some_theron_movie = Movie.objects(actors__in=["Charlize Theron"]).first()

    for recents in Movie.objects(year__gte=2017):
        print(recents.title)


Tài liệu
--------

Có nhiều cách khác để định nghĩa và truy vấn document với MongoEngine.
Để biết thêm thông tin, hãy xem `tài liệu chính thức
<MongoEngine_>`_.

Flask-MongoEngine thêm các tiện ích hữu ích trên MongoEngine. Hãy xem
`tài liệu <Flask-MongoEngine_>`_ của họ nữa.
