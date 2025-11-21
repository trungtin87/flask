Sử dụng SQLite 3 với Flask
==========================

Bạn có thể triển khai một vài hàm để làm việc với một kết nối SQLite trong một
ngữ cảnh request. Kết nối được tạo lần đầu tiên khi nó được truy cập,
được sử dụng lại khi truy cập tiếp theo, cho đến khi nó được đóng khi ngữ cảnh request kết thúc.

Đây là một ví dụ đơn giản về cách bạn có thể sử dụng SQLite 3 với Flask::

    import sqlite3
    from flask import g

    DATABASE = '/path/to/database.db'

    def get_db():
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(DATABASE)
        return db

    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

Bây giờ, để sử dụng cơ sở dữ liệu, ứng dụng phải có một ngữ cảnh
ứng dụng đang hoạt động (điều này luôn đúng nếu có một request đang diễn ra)
hoặc tự tạo một ngữ cảnh ứng dụng. Tại thời điểm đó hàm ``get_db``
có thể được sử dụng để lấy kết nối cơ sở dữ liệu hiện tại. Bất cứ khi nào
ngữ cảnh bị hủy, kết nối cơ sở dữ liệu sẽ bị chấm dứt.

Ví dụ::

    @app.route('/')
    def index():
        cur = get_db().cursor()
        ...


.. note::

    Hãy nhớ rằng các hàm teardown request và appcontext
    luôn được thực thi, ngay cả khi một trình xử lý before-request thất bại hoặc
    không bao giờ được thực thi. Vì điều này chúng ta phải chắc chắn ở đây rằng
    cơ sở dữ liệu ở đó trước khi chúng ta đóng nó.

Kết nối theo Yêu cầu
--------------------

Ưu điểm của cách tiếp cận này (kết nối khi sử dụng lần đầu) là điều này sẽ
chỉ mở kết nối nếu thực sự cần thiết. Nếu bạn muốn sử dụng
mã này bên ngoài ngữ cảnh request, bạn có thể sử dụng nó trong một Python shell bằng cách mở
ngữ cảnh ứng dụng bằng tay::

    with app.app_context():
        # bây giờ bạn có thể sử dụng get_db()


Truy vấn Dễ dàng
----------------

Bây giờ trong mỗi hàm xử lý request bạn có thể truy cập `get_db()` để lấy
kết nối cơ sở dữ liệu mở hiện tại. Để đơn giản hóa việc làm việc với SQLite, một
hàm row factory rất hữu ích. Nó được thực thi cho mỗi kết quả được trả về
từ cơ sở dữ liệu để chuyển đổi kết quả. Ví dụ, để lấy
các dict thay vì tuple, điều này có thể được chèn vào hàm ``get_db``
chúng ta đã tạo ở trên::

    def make_dicts(cursor, row):
        return dict((cursor.description[idx][0], value)
                    for idx, value in enumerate(row))

    db.row_factory = make_dicts

Điều này sẽ làm cho module sqlite3 trả về các dict cho kết nối cơ sở dữ liệu này, dễ xử lý hơn nhiều. Thậm chí đơn giản hơn, chúng ta có thể đặt cái này trong ``get_db`` thay thế::

    db.row_factory = sqlite3.Row

Điều này sẽ sử dụng các đối tượng Row thay vì dict để trả về kết quả của các truy vấn. Đây là các ``namedtuple``, vì vậy chúng ta có thể truy cập chúng bằng index hoặc bằng key. Ví dụ, giả sử chúng ta có một ``sqlite3.Row`` được gọi là ``r`` cho các hàng ``id``, ``FirstName``, ``LastName``, và ``MiddleInitial``::

    >>> # Bạn có thể lấy giá trị dựa trên tên của hàng
    >>> r['FirstName']
    John
    >>> # Hoặc, bạn có thể lấy chúng dựa trên index
    >>> r[1]
    John
    # Các đối tượng Row cũng có thể lặp lại:
    >>> for value in r:
    ...     print(value)
    1
    John
    Doe
    M

Ngoài ra, nên cung cấp một hàm truy vấn kết hợp
lấy con trỏ, thực thi và lấy kết quả::

    def query_db(query, args=(), one=False):
        cur = get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv

Hàm nhỏ tiện lợi này, kết hợp với một row factory, làm cho
việc làm việc với cơ sở dữ liệu dễ chịu hơn nhiều so với chỉ sử dụng
các đối tượng cursor và connection thô.

Đây là cách bạn có thể sử dụng nó::

    for user in query_db('select * from users'):
        print(user['username'], 'has the id', user['user_id'])

Hoặc nếu bạn chỉ muốn một kết quả duy nhất::

    user = query_db('select * from users where username = ?',
                    [the_username], one=True)
    if user is None:
        print('No such user')
    else:
        print(the_username, 'has the id', user['user_id'])

Để truyền các phần biến đổi cho câu lệnh SQL, sử dụng dấu chấm hỏi trong
câu lệnh và truyền vào các đối số dưới dạng danh sách. Không bao giờ thêm chúng trực tiếp vào
câu lệnh SQL với định dạng chuỗi vì điều này làm cho nó có thể
tấn công ứng dụng bằng cách sử dụng `SQL Injections
<https://en.wikipedia.org/wiki/SQL_injection>`_.

Schema Ban đầu
--------------

Các cơ sở dữ liệu quan hệ cần schema, vì vậy các ứng dụng thường đi kèm với một
file `schema.sql` tạo cơ sở dữ liệu. Nên cung cấp
một hàm tạo cơ sở dữ liệu dựa trên schema đó. Hàm này
có thể làm điều đó cho bạn::

    def init_db():
        with app.app_context():
            db = get_db()
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()

Sau đó bạn có thể tạo một cơ sở dữ liệu như vậy từ Python shell:

>>> from yourapplication import init_db
>>> init_db()
