Request Content Checksums
=========================

Nhiều đoạn mã có thể tiêu thụ dữ liệu request và xử lý trước nó.
Ví dụ dữ liệu JSON kết thúc trên đối tượng request đã được đọc và
xử lý, dữ liệu form cũng kết thúc ở đó nhưng đi qua một đường dẫn mã
khác. Điều này có vẻ bất tiện khi bạn muốn tính toán
checksum của dữ liệu request đến. Điều này đôi khi cần thiết cho
một số API.

May mắn thay điều này rất đơn giản để thay đổi bằng cách bao bọc input
stream.

Ví dụ sau tính toán checksum SHA1 của dữ liệu đến khi
nó được đọc và lưu trữ nó trong môi trường WSGI::

    import hashlib

    class ChecksumCalcStream(object):

        def __init__(self, stream):
            self._stream = stream
            self._hash = hashlib.sha1()

        def read(self, bytes):
            rv = self._stream.read(bytes)
            self._hash.update(rv)
            return rv

        def readline(self, size_hint):
            rv = self._stream.readline(size_hint)
            self._hash.update(rv)
            return rv

    def generate_checksum(request):
        env = request.environ
        stream = ChecksumCalcStream(env['wsgi.input'])
        env['wsgi.input'] = stream
        return stream._hash

Để sử dụng điều này, tất cả những gì bạn cần làm là hook calculating stream vào
trước khi request bắt đầu tiêu thụ dữ liệu. (Ví dụ: hãy cẩn thận khi truy cập
``request.form`` hoặc bất cứ thứ gì thuộc loại đó. ``before_request_handlers``
chẳng hạn nên cẩn thận không truy cập nó).

Ví dụ sử dụng::

    @app.route('/special-api', methods=['POST'])
    def special_api():
        hash = generate_checksum(request)
        # Truy cập này phân tích cú pháp input stream
        files = request.files
        # Tại thời điểm này hash được xây dựng đầy đủ.
        checksum = hash.hexdigest()
        return f"Hash was: {checksum}"
