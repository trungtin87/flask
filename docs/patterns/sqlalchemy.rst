SQLAlchemy trong Flask
======================

Nhiều người thích `SQLAlchemy`_ để truy cập cơ sở dữ liệu. Trong trường hợp này, nên
sử dụng một package thay vì một module cho ứng dụng flask của bạn
và đặt các model vào một module riêng biệt (:doc:`packages`). Mặc dù điều đó
không cần thiết, nhưng nó rất có ý nghĩa.

Có bốn cách rất phổ biến để sử dụng SQLAlchemy. Tôi sẽ phác thảo từng
cái ở đây:

Flask-SQLAlchemy Extension
---------------------------

Bởi vì SQLAlchemy là một lớp trừu tượng cơ sở dữ liệu phổ biến và object
relational mapper yêu cầu một chút nỗ lực cấu hình,
có một extension Flask xử lý điều đó cho bạn. Điều này được khuyến nghị
nếu bạn muốn bắt đầu nhanh chóng.

Bạn có thể tải xuống `Flask-SQLAlchemy`_ từ `PyPI
<https://pypi.org/project/Flask-SQLAlchemy/>`_.

.. _Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/


Declarative
-----------

Extension declarative trong SQLAlchemy là phương pháp gần đây nhất để sử dụng
SQLAlchemy. Nó cho phép bạn định nghĩa các bảng và model trong một lần, tương tự
như cách Django hoạt động. Ngoài văn bản sau, tôi khuyên bạn nên đọc
tài liệu chính thức về extension `declarative`_.

Đây là module :file:`database.py` ví dụ cho ứng dụng của bạn::

    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

    engine = create_engine('sqlite:////tmp/test.db')
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    Base = declarative_base()
    Base.query = db_session.query_property()

    def init_db():
        # import tất cả các module ở đây có thể định nghĩa model để
        # chúng sẽ được đăng ký đúng cách trên metadata. Nếu không
        # bạn sẽ phải import chúng trước khi gọi init_db()
        import yourapplication.models
        Base.metadata.create_all(bind=engine)

Để định nghĩa các model của bạn, chỉ cần phân lớp class `Base` được tạo bởi
mã ở trên. Nếu bạn đang tự hỏi tại sao chúng ta không phải quan tâm đến
các thread ở đây (như chúng ta đã làm trong ví dụ SQLite3 ở trên với
đối tượng :data:`~flask.g`): đó là vì SQLAlchemy đã làm điều đó cho chúng ta
với :class:`~sqlalchemy.orm.scoped_session`.

Để sử dụng SQLAlchemy theo cách declarative với ứng dụng của bạn, bạn chỉ
cần đặt mã sau vào module ứng dụng của bạn. Flask sẽ
tự động xóa các phiên cơ sở dữ liệu ở cuối request hoặc
khi ứng dụng tắt::

    from yourapplication.database import db_session

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

Đây là một model ví dụ (đặt cái này vào :file:`models.py`, ví dụ)::

    from sqlalchemy import Column, Integer, String
    from yourapplication.database import Base

    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String(50), unique=True)
        email = Column(String(120), unique=True)

        def __init__(self, name=None, email=None):
            self.name = name
            self.email = email

        def __repr__(self):
            return f'<User {self.name!r}>'

Để tạo cơ sở dữ liệu bạn có thể sử dụng hàm `init_db`:

>>> from yourapplication.database import init_db
>>> init_db()

Bạn có thể chèn các mục vào cơ sở dữ liệu như thế này:

>>> from yourapplication.database import db_session
>>> from yourapplication.models import User
>>> u = User('admin', 'admin@localhost')
>>> db_session.add(u)
>>> db_session.commit()

Truy vấn cũng đơn giản:

>>> User.query.all()
[<User 'admin'>]
>>> User.query.filter(User.name == 'admin').first()
<User 'admin'>

.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _declarative: https://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/

Manual Object Relational Mapping
---------------------------------

Manual object relational mapping có một vài ưu điểm và một vài nhược điểm
so với cách tiếp cận declarative ở trên. Sự khác biệt chính là
bạn định nghĩa các bảng và class riêng biệt và ánh xạ chúng lại với nhau. Nó linh hoạt hơn
nhưng phải gõ nhiều hơn một chút. Nói chung nó hoạt động giống như
cách tiếp cận declarative, vì vậy hãy chắc chắn cũng chia ứng dụng của bạn thành
nhiều module trong một package.

Đây là một module :file:`database.py` ví dụ cho ứng dụng của bạn::

    from sqlalchemy import create_engine, MetaData
    from sqlalchemy.orm import scoped_session, sessionmaker

    engine = create_engine('sqlite:////tmp/test.db')
    metadata = MetaData()
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    def init_db():
        metadata.create_all(bind=engine)

Như trong cách tiếp cận declarative, bạn cần đóng phiên sau mỗi app
context. Đặt cái này vào module ứng dụng của bạn::

    from yourapplication.database import db_session

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

Đây là một bảng và model ví dụ (đặt cái này vào :file:`models.py`)::

    from sqlalchemy import Table, Column, Integer, String
    from sqlalchemy.orm import mapper
    from yourapplication.database import metadata, db_session

    class User(object):
        query = db_session.query_property()

        def __init__(self, name=None, email=None):
            self.name = name
            self.email = email

        def __repr__(self):
            return f'<User {self.name!r}>'

    users = Table('users', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(50), unique=True),
        Column('email', String(120), unique=True)
    )
    mapper(User, users)

Truy vấn và chèn hoạt động chính xác giống như trong ví dụ trên.


SQL Abstraction Layer
---------------------

Nếu bạn chỉ muốn sử dụng lớp trừu tượng hệ thống cơ sở dữ liệu (và SQL)
bạn về cơ bản chỉ cần engine::

    from sqlalchemy import create_engine, MetaData, Table

    engine = create_engine('sqlite:////tmp/test.db')
    metadata = MetaData(bind=engine)

Sau đó bạn có thể khai báo các bảng trong mã của bạn như trong các ví dụ
ở trên, hoặc tự động tải chúng::

    from sqlalchemy import Table

    users = Table('users', metadata, autoload=True)

Để chèn dữ liệu bạn có thể sử dụng phương thức `insert`. Chúng ta phải lấy một
kết nối trước để chúng ta có thể sử dụng một giao dịch:

>>> con = engine.connect()
>>> con.execute(users.insert(), name='admin', email='admin@localhost')

SQLAlchemy sẽ tự động commit cho chúng ta.

Để truy vấn cơ sở dữ liệu của bạn, bạn sử dụng engine trực tiếp hoặc sử dụng một kết nối:

>>> users.select(users.c.id == 1).execute().first()
(1, 'admin', 'admin@localhost')

Các kết quả này cũng là các tuple giống dict:

>>> r = users.select(users.c.id == 1).execute().first()
>>> r['name']
'admin'

Bạn cũng có thể truyền các chuỗi câu lệnh SQL cho phương thức
:meth:`~sqlalchemy.engine.base.Connection.execute`:

>>> engine.execute('select * from users where id = :1', [1]).first()
(1, 'admin', 'admin@localhost')

Để biết thêm thông tin về SQLAlchemy, hãy truy cập
`website <https://www.sqlalchemy.org/>`_.
