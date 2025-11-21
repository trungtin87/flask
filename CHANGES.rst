Version 3.2.0
-------------

Unreleased

-   Ngừng hỗ trợ cho Python 3.9. :pr:`5730`
-   Xóa mã đã bị phản đối trước đó: ``__version__``. :pr:`5648`
-   ``RequestContext`` đã được hợp nhất với ``AppContext``. ``RequestContext`` hiện là
    một bí danh bị phản đối. Nếu một ngữ cảnh ứng dụng (app context) đã được đẩy (pushed), nó sẽ không được sử dụng lại
    khi điều phối một yêu cầu. Điều này đơn giản hóa đáng kể mã nội bộ để theo dõi
    ngữ cảnh hoạt động. :issue:`5639`
-   Các decorator ``template_filter``, ``template_test``, và ``template_global``
    có thể được sử dụng mà không cần dấu ngoặc đơn. :issue:`5729`


Version 3.1.2
-------------

Đã phát hành 2025-08-19

-   ``stream_with_context`` không bị lỗi bên trong các view bất đồng bộ (async views). :issue:`5774`
-   Khi sử dụng ``follow_redirects`` trong test client, trạng thái cuối cùng
    của ``session`` là chính xác. :issue:`5786`
-   Nới lỏng gợi ý kiểu (type hint) cho việc truyền bytes IO vào ``send_file``. :issue:`5776`


Version 3.1.1
-------------

Đã phát hành 2025-05-13

-   Sửa thứ tự chọn khóa ký (signing key) khi xoay vòng khóa được bật thông qua
    ``SECRET_KEY_FALLBACKS``. :ghsa:`4grg-w6v8-c28g`
-   Sửa gợi ý kiểu cho ``cli_runner.invoke``. :issue:`5645`
-   ``flask --help`` tải ứng dụng và các plugin trước để đảm bảo tất cả các lệnh
    đều được hiển thị. :issue:`5673`
-   Đánh dấu lớp cơ sở sans-io là có khả năng xử lý các view trả về
    ``AsyncIterable``. Điều này không chính xác đối với Flask, nhưng giúp việc gõ kiểu dễ dàng hơn
    cho Quart. :pr:`5659`


Version 3.1.0
-------------

Đã phát hành 2024-11-13

-   Ngừng hỗ trợ cho Python 3.8. :pr:`5623`
-   Cập nhật phiên bản phụ thuộc tối thiểu lên các bản phát hành tính năng mới nhất.
    Werkzeug >= 3.1, ItsDangerous >= 2.2, Blinker >= 1.9. :pr:`5624,5633`
-   Cung cấp một tùy chọn cấu hình để kiểm soát các phản hồi
    tự động cho phương thức OPTIONS. :pr:`5496`
-   ``Flask.open_resource``/``open_instance_resource`` và
    ``Blueprint.open_resource`` nhận tham số ``encoding`` để sử dụng khi
    mở ở chế độ văn bản. Mặc định là ``utf-8``. :issue:`5504`
-   ``Request.max_content_length`` có thể được tùy chỉnh theo từng yêu cầu thay vì chỉ
    thông qua cấu hình ``MAX_CONTENT_LENGTH``. Đã thêm cấu hình
    ``MAX_FORM_MEMORY_SIZE`` và ``MAX_FORM_PARTS``. Đã thêm tài liệu
    về giới hạn tài nguyên vào trang bảo mật. :issue:`5625`
-   Thêm hỗ trợ cho thuộc tính cookie ``Partitioned`` (CHIPS), với cấu hình
    ``SESSION_COOKIE_PARTITIONED``. :issue:`5472`
-   ``-e path`` được ưu tiên hơn các tệp mặc định ``.env`` và ``.flaskenv``.
    ``load_dotenv`` tải các tệp mặc định cùng với đường dẫn trừ khi
    ``load_defaults=False`` được truyền vào. :issue:`5628`
-   Hỗ trợ xoay vòng khóa với cấu hình ``SECRET_KEY_FALLBACKS``, một danh sách các
    khóa bí mật cũ vẫn có thể được sử dụng để hủy ký (unsigning). Các tiện ích mở rộng sẽ cần
    thêm hỗ trợ. :issue:`5621`
-   Sửa cách thiết lập ``host_matching=True`` hoặc ``subdomain_matching=False``
    tương tác với ``SERVER_NAME``. Thiết lập ``SERVER_NAME`` không còn hạn chế
    các yêu cầu chỉ đến miền đó. :issue:`5553`
-   ``Request.trusted_hosts`` được kiểm tra trong quá trình định tuyến, và có thể được thiết lập thông qua
    cấu hình ``TRUSTED_HOSTS``. :issue:`5636`


Version 3.0.3
-------------

Đã phát hành 2024-04-07

-   Mặc định ``hashlib.sha1`` có thể không khả dụng trong các bản build FIPS. Không
    truy cập nó tại thời điểm import để nhà phát triển có thời gian thay đổi mặc định.
    :issue:`5448`
-   Không khởi tạo thuộc tính ``cli`` trong khung sansio, mà thay vào đó là trong
    lớp cụ thể ``Flask``. :pr:`5270`


Version 3.0.2
-------------

Đã phát hành 2024-02-03

-   Sửa kiểu cho thuộc tính ``jinja_loader``. :issue:`5388`
-   Sửa lỗi với các tùy chọn CLI ``--extra-files`` và ``--exclude-patterns``.
    :issue:`5391`


Version 3.0.1
-------------

Đã phát hành 2024-01-18

-   Sửa kiểu cho tham số ``path`` của ``send_file``. :issue:`5336`
-   Sửa lỗi chính tả trong thông báo lỗi cho tùy chọn ``flask run --key``. :pr:`5344`
-   Dữ liệu phiên (session) được bỏ gắn thẻ (untagged) mà không dựa vào ``object_hook`` của
    ``json.loads`` tích hợp sẵn. Điều này cho phép các nhà cung cấp JSON khác không triển khai điều đó.
    :issue:`5381`
-   Giải quyết nhiều phát hiện về kiểu hơn khi sử dụng chế độ nghiêm ngặt của mypy. :pr:`5383`


Version 3.0.0
-------------

Đã phát hành 2023-09-30

-   Xóa mã đã bị phản đối trước đó. :pr:`5223`
-   Phản đối thuộc tính ``__version__``. Sử dụng phát hiện tính năng, hoặc
    ``importlib.metadata.version("flask")`` thay thế. :issue:`5230`
-   Cấu trúc lại mã sao cho các lớp Flask (app) và Blueprint
    có các cơ sở Sans-IO. :pr:`5127`
-   Cho phép self là một tham số cho url_for. :pr:`5264`
-   Yêu cầu Werkzeug >= 3.0.0.


Version 2.3.3
-------------

Đã phát hành 2023-08-21

-   Tương thích với Python 3.12.
-   Yêu cầu Werkzeug >= 2.3.7.
-   Sử dụng ``flit_core`` thay vì ``setuptools`` làm backend xây dựng.
-   Tái cấu trúc cách xác định đường dẫn gốc và đường dẫn instance của ứng dụng. :issue:`5160`


Version 2.3.2
-------------

Đã phát hành 2023-05-01

-   Thiết lập header ``Vary: Cookie`` khi session được truy cập, sửa đổi, hoặc làm mới.
-   Cập nhật yêu cầu Werkzeug lên >=2.3.3 để áp dụng các bản sửa lỗi gần đây.
    :ghsa:`m2qf-hxjv-5gpq`


Version 2.3.1
-------------

Đã phát hành 2023-04-25

-   Khôi phục ``from flask import Markup`` đã bị phản đối. :issue:`5084`


Version 2.3.0
-------------

Đã phát hành 2023-04-25

-   Ngừng hỗ trợ cho Python 3.7. :pr:`5072`
-   Cập nhật các yêu cầu tối thiểu lên các phiên bản mới nhất: Werkzeug>=2.3.0, Jinja2>3.1.2,
    itsdangerous>=2.1.2, click>=8.1.3.
-   Xóa mã đã bị phản đối trước đó. :pr:`4995`

    -   Các phương thức ``push`` và ``pop`` của các đối tượng ``_app_ctx_stack`` và
        ``_request_ctx_stack`` bị phản đối đã bị xóa. ``top`` vẫn tồn tại để cung cấp
        cho các tiện ích mở rộng thêm thời gian để cập nhật, nhưng nó sẽ bị xóa.
    -   Biến môi trường ``FLASK_ENV``, khóa cấu hình ``ENV``, và thuộc tính ``app.env``
        đã bị xóa.
    -   Các thuộc tính ``session_cookie_name``, ``send_file_max_age_default``, ``use_x_sendfile``,
        ``propagate_exceptions``, và ``templates_auto_reload`` trên ``app``
        đã bị xóa.
    -   Các khóa cấu hình ``JSON_AS_ASCII``, ``JSON_SORT_KEYS``, ``JSONIFY_MIMETYPE``, và
        ``JSONIFY_PRETTYPRINT_REGULAR`` đã bị xóa.
    -   Các decorator ``app.before_first_request`` và ``bp.before_app_first_request``
        đã bị xóa.
    -   Các thuộc tính ``json_encoder`` và ``json_decoder`` trên app và blueprint, và
        các lớp ``json.JSONEncoder`` và ``JSONDecoder`` tương ứng, đã bị xóa.
    -   Các hàm ``json.htmlsafe_dumps`` và ``htmlsafe_dump`` đã bị xóa.
    -   Gọi các phương thức thiết lập trên blueprint sau khi đăng ký là một lỗi thay vì
        cảnh báo. :pr:`4997`

-   Việc import ``escape`` và ``Markup`` từ ``flask`` bị phản đối. Hãy import chúng
    trực tiếp từ ``markupsafe``. :pr:`4996`
-   Thuộc tính ``app.got_first_request`` bị phản đối. :pr:`4997`
-   Decorator ``locked_cached_property`` bị phản đối. Sử dụng một khóa bên trong
    hàm được decorate nếu cần khóa. :issue:`4993`
-   Signals luôn có sẵn. ``blinker>=1.6.2`` là một phụ thuộc bắt buộc. Thuộc tính
    ``signals_available`` bị phản đối. :issue:`5056`
-   Signals hỗ trợ các hàm subscriber ``async``. :pr:`5049`
-   Xóa việc sử dụng các khóa có thể khiến các yêu cầu chặn nhau trong thời gian rất ngắn.
    :issue:`4993`
-   Sử dụng metadata đóng gói hiện đại với ``pyproject.toml`` thay vì ``setup.cfg``.
    :pr:`4947`
-   Đảm bảo các tên miền phụ được áp dụng với các blueprint lồng nhau. :issue:`4834`
-   ``config.from_file`` có thể sử dụng ``text=False`` để chỉ ra rằng bộ phân tích cú pháp muốn một
    tệp nhị phân. :issue:`4989`
-   Nếu một blueprint được tạo với tên trống, nó sẽ ném ra ``ValueError``.
    :issue:`5010`
-   ``SESSION_COOKIE_DOMAIN`` không quay trở lại ``SERVER_NAME``. Mặc định là không
    thiết lập miền, điều mà các trình duyệt hiện đại hiểu là khớp chính xác thay vì
    khớp tên miền phụ. Các cảnh báo về ``localhost`` và địa chỉ IP cũng bị xóa.
    :issue:`5051`
-   Lệnh ``routes`` hiển thị ``subdomain`` hoặc ``host`` của mỗi quy tắc khi
    khớp miền được sử dụng. :issue:`5004`
-   Sử dụng đánh giá hoãn lại (postponed evaluation) của các chú thích (annotations). :pr:`5071`


Version 2.2.5
-------------

Đã phát hành 2023-05-02

-   Cập nhật để tương thích với Werkzeug 2.3.3.
-   Thiết lập header ``Vary: Cookie`` khi session được truy cập, sửa đổi, hoặc làm mới.


Version 2.2.4
-------------

Đã phát hành 2023-04-25

-   Cập nhật để tương thích với Werkzeug 2.3.


Version 2.2.3
-------------

Đã phát hành 2023-02-15

-   Autoescape được bật theo mặc định cho các tệp mẫu ``.svg``. :issue:`4831`
-   Sửa kiểu của ``template_folder`` để chấp nhận ``pathlib.Path``. :issue:`4892`
-   Thêm tùy chọn ``--debug`` vào lệnh ``flask run``. :issue:`4777`


Version 2.2.2
-------------

Đã phát hành 2022-08-08

-   Cập nhật phụ thuộc Werkzeug lên >= 2.2.2. Điều này bao gồm các bản sửa lỗi liên quan
    đến bộ định tuyến mới nhanh hơn, phân tích cú pháp header, và máy chủ phát triển.
    :pr:`4754`
-   Sửa giá trị mặc định cho ``app.env`` thành ``"production"``. Thuộc tính này
    vẫn bị phản đối. :issue:`4740`


Version 2.2.1
-------------

Đã phát hành 2022-08-03

-   Thiết lập hoặc truy cập ``json_encoder`` hoặc ``json_decoder`` sẽ ném ra
    cảnh báo phản đối. :issue:`4732`


Version 2.2.0
-------------

Đã phát hành 2022-08-01

-   Xóa mã đã bị phản đối trước đó. :pr:`4667`

    -   Các tên cũ cho một số tham số ``send_file`` đã bị xóa.
        ``download_name`` thay thế ``attachment_filename``, ``max_age``
        thay thế ``cache_timeout``, và ``etag`` thay thế ``add_etags``.
        Ngoài ra, ``path`` thay thế ``filename`` trong
        ``send_from_directory``.
    -   Thuộc tính ``RequestContext.g`` trả về ``AppContext.g`` đã bị
        xóa.

-   Cập nhật phụ thuộc Werkzeug lên >= 2.2.
-   Các ngữ cảnh ứng dụng và yêu cầu được quản lý bằng cách sử dụng các biến ngữ cảnh Python
    trực tiếp thay vì ``LocalStack`` của Werkzeug. Điều này sẽ dẫn đến
    hiệu suất và sử dụng bộ nhớ tốt hơn. :pr:`4682`

    -   Các nhà bảo trì tiện ích mở rộng, hãy lưu ý rằng ``_app_ctx_stack.top``
        và ``_request_ctx_stack.top`` đã bị phản đối. Lưu trữ dữ liệu trên
        ``g`` thay vào đó bằng cách sử dụng một tiền tố duy nhất, như
        ``g._extension_name_attr``.

-   Biến môi trường ``FLASK_ENV`` và thuộc tính ``app.env`` bị
    phản đối, loại bỏ sự phân biệt giữa chế độ phát triển và gỡ lỗi.
    Chế độ gỡ lỗi nên được kiểm soát trực tiếp bằng cách sử dụng tùy chọn ``--debug``
    hoặc ``app.run(debug=True)``. :issue:`4714`
-   Một số thuộc tính ủy quyền các khóa cấu hình trên ``app`` bị phản đối:
    ``session_cookie_name``, ``send_file_max_age_default``,
    ``use_x_sendfile``, ``propagate_exceptions``, và
    ``templates_auto_reload``. Sử dụng các khóa cấu hình liên quan thay thế.
    :issue:`4716`
-   Thêm các điểm tùy chỉnh mới vào đối tượng ứng dụng ``Flask`` cho nhiều
    hành vi toàn cục trước đây.

    -   ``flask.url_for`` sẽ gọi ``app.url_for``. :issue:`4568`
    -   ``flask.abort`` sẽ gọi ``app.aborter``.
        ``Flask.aborter_class`` và ``Flask.make_aborter`` có thể được sử dụng
        để tùy chỉnh aborter này. :issue:`4567`
    -   ``flask.redirect`` sẽ gọi ``app.redirect``. :issue:`4569`
    -   ``flask.json`` là một thể hiện của ``JSONProvider``. Một nhà cung cấp
        khác có thể được thiết lập để sử dụng thư viện JSON khác.
        ``flask.jsonify`` sẽ gọi ``app.json.response``, các hàm khác
        trong ``flask.json`` sẽ gọi các hàm tương ứng trong
        ``app.json``. :pr:`4692`

-   Cấu hình JSON được chuyển sang các thuộc tính trên nhà cung cấp mặc định
    ``app.json``. ``JSON_AS_ASCII``, ``JSON_SORT_KEYS``,
    ``JSONIFY_MIMETYPE``, và ``JSONIFY_PRETTYPRINT_REGULAR`` bị
    phản đối. :pr:`4692`
-   Thiết lập các lớp ``json_encoder`` và ``json_decoder`` tùy chỉnh trên
    ứng dụng hoặc một blueprint, và các lớp ``json.JSONEncoder`` và
    ``JSONDecoder`` tương ứng, bị phản đối. Hành vi JSON hiện có thể được
    ghi đè bằng cách sử dụng giao diện nhà cung cấp ``app.json``. :pr:`4692`
-   ``json.htmlsafe_dumps`` và ``json.htmlsafe_dump`` bị phản đối,
    hàm này hiện đã được tích hợp vào Jinja. :pr:`4692`
-   Tái cấu trúc ``register_error_handler`` để hợp nhất việc kiểm tra lỗi.
    Viết lại một số thông báo lỗi để nhất quán hơn. :issue:`4559`
-   Sử dụng các decorator và hàm Blueprint dành cho việc thiết lập sau khi
    đăng ký blueprint sẽ hiển thị cảnh báo. Trong phiên bản tiếp theo,
    điều này sẽ trở thành lỗi giống như các phương thức thiết lập ứng dụng.
    :issue:`4571`
-   ``before_first_request`` bị phản đối. Chạy mã thiết lập khi tạo
    ứng dụng thay thế. :issue:`4605`
-   Đã thêm thuộc tính lớp ``View.init_every_request``. Nếu một lớp con view
    đặt thuộc tính này thành ``False``, view sẽ không tạo một thể hiện mới
    trên mỗi yêu cầu. :issue:`2520`.
-   Một nhóm Click ``flask.cli.FlaskGroup`` có thể được lồng như một
    lệnh con trong một CLI tùy chỉnh. :issue:`3263`
-   Thêm các tùy chọn ``--app`` và ``--debug`` vào CLI ``flask``, thay vì
    yêu cầu chúng được thiết lập thông qua các biến môi trường.
    :issue:`2836`
-   Thêm tùy chọn ``--env-file`` vào CLI ``flask``. Điều này cho phép
    chỉ định một tệp dotenv để tải thêm vào ``.env`` và
    ``.flaskenv``. :issue:`3108`
-   Không còn bắt buộc phải decorate các lệnh CLI tùy chỉnh trên
    ``app.cli`` hoặc ``blueprint.cli`` với ``@with_appcontext``, một ngữ cảnh ứng dụng
    sẽ đã hoạt động tại thời điểm đó. :issue:`2410`
-   ``SessionInterface.get_expiration_time`` sử dụng một giá trị
    nhận biết múi giờ (timezone-aware). :pr:`4645`
-   Các hàm view có thể trả về các generator trực tiếp thay vì bọc
    chúng trong một ``Response``. :pr:`4629`
-   Thêm các hàm ``stream_template`` và ``stream_template_string`` để
    render một template dưới dạng một luồng các mảnh. :pr:`4629`
-   Một triển khai mới về bảo tồn ngữ cảnh trong quá trình gỡ lỗi và
    kiểm thử. :pr:`4666`

    -   ``request``, ``g``, và các biến cục bộ ngữ cảnh khác trỏ đến
        dữ liệu chính xác khi chạy mã trong bảng điều khiển gỡ lỗi tương tác.
        :issue:`2836`
    -   Các hàm teardown luôn được chạy vào cuối yêu cầu,
        ngay cả khi ngữ cảnh được bảo tồn. Chúng cũng được chạy sau khi
        ngữ cảnh được bảo tồn bị pop.
    -   ``stream_with_context`` bảo tồn ngữ cảnh riêng biệt khỏi một
        khối ``with client``. Nó sẽ được dọn dẹp khi
        ``response.get_data()`` hoặc ``response.close()`` được gọi.

-   Cho phép trả về một danh sách từ một hàm view, để chuyển đổi nó thành một
    phản hồi JSON giống như một dict. :issue:`4672`
-   Khi kiểm tra kiểu, cho phép ``TypedDict`` được trả về từ các hàm view.
    :pr:`4695`
-   Xóa các tùy chọn ``--eager-loading/--lazy-loading`` khỏi
    lệnh ``flask run``. Ứng dụng luôn được tải eager lần đầu tiên,
    sau đó tải lazy trong trình tải lại. Trình tải lại luôn in
    lỗi ngay lập tức nhưng vẫn tiếp tục phục vụ. Xóa middleware nội bộ
    ``DispatchingApp`` được sử dụng bởi triển khai trước đó.
    :issue:`4715`


Version 2.1.3
-------------

Đã phát hành 2022-07-13

-   Inline một số import tùy chọn chỉ được sử dụng cho một số lệnh CLI
    nhất định. :pr:`4606`
-   Nới lỏng chú thích kiểu cho các hàm ``after_request``. :issue:`4600`
-   ``instance_path`` cho các gói namespace sử dụng đường dẫn gần nhất với
    mô-đun con được import. :issue:`4610`
-   Thông báo lỗi rõ ràng hơn khi ``render_template`` và
    ``render_template_string`` được sử dụng bên ngoài một ngữ cảnh ứng dụng.
    :pr:`4693`


Version 2.1.2
-------------

Đã phát hành 2022-04-28

-   Sửa chú thích kiểu cho ``json.loads``, nó chấp nhận str hoặc bytes.
    :issue:`4519`
-   Các tùy chọn ``--cert`` và ``--key`` trên ``flask run`` có thể được đưa ra
    theo bất kỳ thứ tự nào. :issue:`4459`


Version 2.1.1
-------------

Đã phát hành vào 2022-03-30

-   Đặt phiên bản yêu cầu tối thiểu của importlib_metadata thành 3.6.0,
    điều này là bắt buộc trên Python < 3.10. :issue:`4502`


Version 2.1.0
-------------

Đã phát hành 2022-03-28

-   Ngừng hỗ trợ cho Python 3.6. :pr:`4335`
-   Cập nhật phụ thuộc Click lên >= 8.0. :pr:`4008`
-   Xóa mã đã bị phản đối trước đó. :pr:`4337`

    -   CLI không truyền ``script_info`` đến các hàm factory ứng dụng.
    -   ``config.from_json`` được thay thế bởi
        ``config.from_file(name, load=json.load)``.
    -   Các hàm ``json`` không còn nhận tham số ``encoding``.
    -   ``safe_join`` bị xóa, sử dụng ``werkzeug.utils.safe_join``
        thay thế.
    -   ``total_seconds`` bị xóa, sử dụng ``timedelta.total_seconds``
        thay thế.
    -   Cùng một blueprint không thể được đăng ký với cùng một tên. Sử dụng
        ``name=`` khi đăng ký để chỉ định một tên duy nhất.
    -   Tham số ``as_tuple`` của test client bị xóa. Sử dụng
        ``response.request.environ`` thay thế. :pr:`4417`

-   Một số tham số trong ``send_file`` và ``send_from_directory`` đã được
    đổi tên trong 2.0. Thời gian phản đối cho các tên cũ được kéo dài
    đến 2.2. Hãy chắc chắn kiểm tra với các cảnh báo phản đối hiển thị.

    -   ``attachment_filename`` được đổi tên thành ``download_name``.
    -   ``cache_timeout`` được đổi tên thành ``max_age``.
    -   ``add_etags`` được đổi tên thành ``etag``.
    -   ``filename`` được đổi tên thành ``path``.

-   Thuộc tính ``RequestContext.g`` bị phản đối. Sử dụng ``g`` trực tiếp
    hoặc ``AppContext.g`` thay thế. :issue:`3898`
-   ``copy_current_request_context`` có thể decorate các hàm async.
    :pr:`4303`
-   CLI sử dụng ``importlib.metadata`` thay vì ``pkg_resources`` để
    tải các điểm nhập lệnh. :issue:`4419`
-   Ghi đè ``FlaskClient.open`` sẽ không gây ra lỗi khi chuyển hướng.
    :issue:`3396`
-   Thêm tùy chọn ``--exclude-patterns`` vào lệnh CLI ``flask run``
    để chỉ định các mẫu sẽ bị bỏ qua bởi trình tải lại.
    :issue:`4188`
-   Khi sử dụng tải lazy (mặc định với trình gỡ lỗi), ngữ cảnh Click
    từ lệnh ``flask run`` vẫn có sẵn trong
    luồng tải. :issue:`4460`
-   Xóa cookie session sử dụng cờ ``httponly``.
    :issue:`4485`
-   Nới lỏng việc gõ kiểu cho ``errorhandler`` để cho phép người dùng sử dụng các kiểu
    chính xác hơn và decorate cùng một hàm nhiều lần.
    :issue:`4095, 4295, 4297`
-   Sửa việc gõ kiểu cho các phương thức ``__exit__`` để tương thích tốt hơn với
    ``ExitStack``. :issue:`4474`
-   Từ Werkzeug, đối với các phản hồi chuyển hướng, URL header ``Location``
    sẽ vẫn tương đối, và loại trừ scheme và domain, theo mặc định.
    :pr:`4496`
-   Thêm ``Config.from_prefixed_env()`` để tải các giá trị cấu hình từ
    các biến môi trường bắt đầu bằng ``FLASK_`` hoặc một tiền tố khác.
    Nó phân tích các giá trị dưới dạng JSON theo mặc định, và cho phép thiết lập các khóa trong
    các dict lồng nhau. :pr:`4479`


Version 2.0.3
-------------

Đã phát hành 2022-02-14

-   Tham số ``as_tuple`` của test client bị phản đối và sẽ bị
    xóa trong Werkzeug 2.1. Nó hiện cũng bị phản đối trong Flask, để bị
    xóa trong Flask 2.1, trong khi vẫn tương thích với cả hai trong
    2.0.x. Sử dụng ``response.request.environ`` thay thế. :pr:`4341`
-   Sửa chú thích kiểu cho decorator ``errorhandler``. :issue:`4295`
-   Hoàn tác một thay đổi đối với CLI khiến nó ẩn các traceback ``ImportError``
    khi import ứng dụng. :issue:`4307`
-   ``app.json_encoder`` và ``json_decoder`` chỉ được truyền đến
    ``dumps`` và ``loads`` nếu chúng có hành vi tùy chỉnh. Điều này cải thiện
    hiệu suất, chủ yếu trên PyPy. :issue:`4349`
-   Thông báo lỗi rõ ràng hơn khi ``after_this_request`` được sử dụng bên ngoài một
    ngữ cảnh yêu cầu. :issue:`4333`


Version 2.0.2
-------------

Đã phát hành 2021-10-04

-   Sửa chú thích kiểu cho các phương thức ``teardown_*``. :issue:`4093`
-   Sửa chú thích kiểu cho các decorator ``before_request`` và ``before_app_request``.
    :issue:`4104`
-   Đã sửa vấn đề mà việc gõ kiểu yêu cầu các decorator template global
    phải chấp nhận các hàm không có đối số. :issue:`4098`
-   Hỗ trợ các thể hiện View và MethodView với các trình xử lý async. :issue:`4112`
-   Cải thiện việc gõ kiểu của decorator ``app.errorhandler``. :issue:`4095`
-   Sửa việc đăng ký một blueprint hai lần với các tên khác nhau. :issue:`4124`
-   Sửa kiểu của ``static_folder`` để chấp nhận ``pathlib.Path``.
    :issue:`4150`
-   ``jsonify`` xử lý ``decimal.Decimal`` bằng cách mã hóa thành ``str``.
    :issue:`4157`
-   Xử lý chính xác việc ném ra các lỗi bị hoãn trong tải lazy CLI.
    :issue:`4096`
-   Trình tải CLI xử lý ``**kwargs`` trong một hàm ``create_app``.
    :issue:`4170`
-   Sửa thứ tự của ``before_request`` và các callback khác kích hoạt
    trước khi view trả về. Chúng được gọi từ app xuống đến
    blueprint lồng nhau gần nhất. :issue:`4229`


Version 2.0.1
-------------

Đã phát hành 2021-05-21

-   Thêm lại tham số ``filename`` trong ``send_from_directory``. Tham số
    ``filename`` đã được đổi tên thành ``path``, tên cũ
    bị phản đối. :pr:`4019`
-   Đánh dấu các tên cấp cao nhất là đã xuất (exported) để kiểm tra kiểu hiểu
    các import trong các dự án người dùng. :issue:`4024`
-   Sửa chú thích kiểu cho ``g`` và thông báo cho mypy rằng nó là một đối tượng
    namespace có các thuộc tính tùy ý. :issue:`4020`
-   Sửa một số kiểu không có sẵn trong Python 3.6.0. :issue:`4040`
-   Cải thiện việc gõ kiểu cho ``send_file``, ``send_from_directory``, và
    ``get_send_file_max_age``. :issue:`4044`, :pr:`4026`
-   Hiển thị lỗi khi tên blueprint chứa dấu chấm. Dấu ``.`` có
    ý nghĩa đặc biệt, nó được sử dụng để phân tách tên blueprint (lồng nhau) và
    tên endpoint. :issue:`4041`
-   Kết hợp các tiền tố URL khi lồng các blueprint được tạo với
    một giá trị ``url_prefix``. :issue:`4037`
-   Hoàn tác một thay đổi đối với thứ tự khớp URL đã được thực hiện.
    URL lại được khớp sau khi session được tải, vì vậy session có
    sẵn trong các bộ chuyển đổi URL tùy chỉnh. :issue:`4053`
-   Thêm lại ``Config.from_json`` đã bị phản đối, cái mà đã vô tình
    bị xóa sớm. :issue:`4078`
-   Cải thiện việc gõ kiểu cho một số hàm sử dụng ``Callable`` trong chữ ký
    kiểu của chúng, tập trung vào các factory decorator. :issue:`4060`
-   Các blueprint lồng nhau được đăng ký với tên có dấu chấm của chúng. Điều này cho phép
    các blueprint khác nhau có cùng tên được lồng tại các vị trí
    khác nhau. :issue:`4069`
-   ``register_blueprint`` nhận một tùy chọn ``name`` để thay đổi
    tên (trước khi có dấu chấm) mà blueprint được đăng ký. Điều này cho phép
    cùng một blueprint được đăng ký nhiều lần với các tên duy nhất cho
    ``url_for``. Đăng ký cùng một blueprint với cùng một tên
    nhiều lần bị phản đối. :issue:`1091`
-   Cải thiện việc gõ kiểu cho ``stream_with_context``. :issue:`4052`


Version 2.0.0
-------------

Đã phát hành 2021-05-11

-   Ngừng hỗ trợ cho Python 2 và 3.5.
-   Tăng phiên bản tối thiểu của các dự án Pallets khác: Werkzeug >= 2,
    Jinja2 >= 3, MarkupSafe >= 2, ItsDangerous >= 2, Click >= 8. Hãy chắc chắn
    kiểm tra nhật ký thay đổi cho từng dự án. Để tương thích tốt hơn
    với các ứng dụng khác (ví dụ: Celery) vẫn yêu cầu Click 7,
    chưa có phụ thuộc cứng vào Click 8, nhưng sử dụng Click 7 sẽ
    kích hoạt DeprecationWarning và Flask 2.1 sẽ phụ thuộc vào Click 8.
-   Hỗ trợ JSON không còn sử dụng simplejson. Để sử dụng mô-đun JSON khác,
    ghi đè ``app.json_encoder`` và ``json_decoder``. :issue:`3555`
-   Tùy chọn ``encoding`` cho các hàm JSON bị phản đối. :pr:`3562`
-   Truyền ``script_info`` đến các hàm factory ứng dụng bị phản đối. Điều này
    không di động bên ngoài lệnh ``flask``. Sử dụng
    ``click.get_current_context().obj`` nếu cần. :issue:`3552`
-   CLI hiển thị thông báo lỗi tốt hơn khi ứng dụng không tải được
    khi tra cứu các lệnh. :issue:`2741`
-   Thêm ``SessionInterface.get_cookie_name`` để cho phép thiết lập
    tên cookie session động. :pr:`3369`
-   Thêm ``Config.from_file`` để tải cấu hình bằng cách sử dụng các trình tải tệp
    tùy ý, chẳng hạn như ``toml.load`` hoặc ``json.load``.
    ``Config.from_json`` bị phản đối để ủng hộ điều này. :pr:`3398`
-   Lệnh ``flask run`` sẽ chỉ hoãn các lỗi khi tải lại. Các lỗi
    hiện diện trong lần gọi ban đầu sẽ khiến máy chủ thoát với
    traceback ngay lập tức. :issue:`3431`
-   ``send_file`` ném ra ``ValueError`` khi được truyền một đối tượng ``io``
    ở chế độ văn bản. Trước đây, nó sẽ phản hồi với 200 OK và một tệp
    trống. :issue:`3358`
-   Khi sử dụng các chứng chỉ ad-hoc, kiểm tra thư viện cryptography
    thay vì PyOpenSSL. :pr:`3492`
-   Khi chỉ định một hàm factory với ``FLASK_APP``, đối số từ khóa
    có thể được truyền vào. :issue:`3553`
-   Khi tải một tệp ``.env`` hoặc ``.flaskenv``, thư mục làm việc
    hiện tại không còn bị thay đổi thành vị trí của tệp.
    :pr:`3560`
-   Khi trả về một tuple ``(response, headers)`` từ một view, các
    header thay thế thay vì mở rộng các header hiện có trên phản hồi.
    Ví dụ, điều này cho phép thiết lập ``Content-Type`` cho
    ``jsonify()``. Sử dụng ``response.headers.extend()`` nếu muốn mở rộng.
    :issue:`3628`
-   Lớp ``Scaffold`` cung cấp một API chung cho các lớp ``Flask`` và
    ``Blueprint``. Thông tin ``Blueprint`` được lưu trữ trong
    các thuộc tính giống như ``Flask``, thay vì các hàm lambda mờ đục.
    Điều này nhằm mục đích cải thiện tính nhất quán và khả năng bảo trì.
    :issue:`3215`
-   Bao gồm các tùy chọn ``samesite`` và ``secure`` khi xóa
    cookie session. :pr:`3726`
-   Hỗ trợ truyền một ``pathlib.Path`` đến ``static_folder``. :pr:`3579`
-   ``send_file`` và ``send_from_directory`` là các wrapper xung quanh
    các triển khai trong ``werkzeug.utils``. :pr:`3828`
-   Một số tham số ``send_file`` đã được đổi tên, các tên cũ
    bị phản đối. ``attachment_filename`` được đổi tên thành ``download_name``.
    ``cache_timeout`` được đổi tên thành ``max_age``. ``add_etags`` được
    đổi tên thành ``etag``. :pr:`3828, 3883`
-   ``send_file`` truyền ``download_name`` ngay cả khi
    ``as_attachment=False`` bằng cách sử dụng ``Content-Disposition: inline``.
    :pr:`3828`
-   ``send_file`` thiết lập ``conditional=True`` và ``max_age=None`` theo
    mặc định. ``Cache-Control`` được thiết lập thành ``no-cache`` nếu ``max_age``
    không được thiết lập, nếu không thì là ``public``. Điều này bảo các trình duyệt xác thực
    các yêu cầu có điều kiện thay vì sử dụng bộ nhớ cache theo thời gian. :pr:`3828`
-   ``helpers.safe_join`` bị phản đối. Sử dụng
    ``werkzeug.utils.safe_join`` thay thế. :pr:`3828`
-   Ngữ cảnh yêu cầu thực hiện khớp định tuyến trước khi mở session.
    Điều này có thể cho phép một giao diện session thay đổi hành vi dựa trên
    ``request.endpoint``. :issue:`3776`
-   Sử dụng triển khai của Jinja cho bộ lọc ``|tojson``. :issue:`3881`
-   Thêm các decorator định tuyến cho các phương thức HTTP phổ biến. Ví dụ,
    ``@app.post("/login")`` là một lối tắt cho
    ``@app.route("/login", methods=["POST"])``. :pr:`3907`
-   Hỗ trợ các view async, trình xử lý lỗi, trước và sau yêu cầu, và
    các hàm teardown. :pr:`3412`
-   Hỗ trợ lồng các blueprint. :issue:`593, 1548`, :pr:`3923`
-   Thiết lập mã hóa mặc định là "UTF-8" khi tải các tệp ``.env`` và
    ``.flaskenv`` để cho phép sử dụng các ký tự không phải ASCII. :issue:`3931`
-   ``flask shell`` thiết lập hoàn thành tab và lịch sử giống như shell
    ``python`` mặc định nếu ``readline`` được cài đặt. :issue:`3941`
-   ``helpers.total_seconds()`` bị phản đối. Sử dụng
    ``timedelta.total_seconds()`` thay thế. :pr:`3962`
-   Thêm gợi ý kiểu. :pr:`3973`.


Version 1.1.4
-------------

Đã phát hành 2021-05-13

-   Cập nhật ``static_folder`` để sử dụng ``_compat.fspath`` thay vì
    ``os.fspath`` để tiếp tục hỗ trợ Python < 3.6 :issue:`4050`


Version 1.1.3
-------------

Đã phát hành 2021-05-13

-   Thiết lập các phiên bản tối đa của Werkzeug, Jinja, Click, và ItsDangerous.
    :issue:`4043`
-   Thêm lại hỗ trợ cho việc truyền một ``pathlib.Path`` cho ``static_folder``.
    :pr:`3579`


Version 1.1.2
-------------

Đã phát hành 2020-04-03

-   Khắc phục một vấn đề khi chạy lệnh ``flask`` với một
    trình gỡ lỗi bên ngoài trên Windows. :issue:`3297`
-   Tuyến tĩnh sẽ không bắt tất cả các URL nếu đối số ``static_folder``
    của ``Flask`` kết thúc bằng dấu gạch chéo. :issue:`3452`


Version 1.1.1
-------------

Đã phát hành 2019-07-08

-   Cờ ``flask.json_available`` đã được thêm lại để tương thích
    với một số tiện ích mở rộng. Nó sẽ ném ra cảnh báo phản đối khi được sử dụng,
    và sẽ bị xóa trong phiên bản 2.0.0. :issue:`3288`


Version 1.1.0
-------------

Đã phát hành 2019-07-04

-   Tăng phiên bản Werkzeug tối thiểu lên >= 0.15.
-   Ngừng hỗ trợ cho Python 3.4.
-   Các trình xử lý lỗi cho ``InternalServerError`` hoặc ``500`` sẽ luôn được
    truyền một thể hiện của ``InternalServerError``. Nếu chúng được gọi
    do một ngoại lệ không được xử lý, ngoại lệ gốc đó hiện có
    sẵn dưới dạng ``e.original_exception`` thay vì được truyền
    trực tiếp đến trình xử lý. Điều tương tự cũng đúng nếu trình xử lý dành cho
    cơ sở ``HTTPException``. Điều này làm cho hành vi của trình xử lý lỗi
    nhất quán hơn. :pr:`3266`

    -   ``Flask.finalize_request`` được gọi cho tất cả các ngoại lệ
        không được xử lý ngay cả khi không có trình xử lý lỗi ``500``.

-   ``Flask.logger`` lấy cùng tên với ``Flask.name`` (giá trị
    được truyền dưới dạng ``Flask(import_name)``. Điều này hoàn tác hành vi của 1.0 là
    luôn ghi nhật ký vào ``"flask.app"``, để hỗ trợ nhiều ứng dụng
    trong cùng một quy trình. Một cảnh báo sẽ được hiển thị nếu cấu hình cũ được
    phát hiện cần phải di chuyển. :issue:`2866`
-   ``RequestContext.copy`` bao gồm đối tượng session hiện tại trong
    bản sao ngữ cảnh yêu cầu. Điều này ngăn ``session`` trỏ đến một
    đối tượng lỗi thời. :issue:`2935`
-   Sử dụng RequestContext tích hợp sẵn, các ký tự Unicode không in được trong
    Host header sẽ dẫn đến phản hồi HTTP 400 và không phải HTTP 500 như
    trước đây. :pr:`2994`
-   ``send_file`` hỗ trợ các đối tượng ``PathLike`` như được mô tả trong
    :pep:`519`, để hỗ trợ ``pathlib`` trong Python 3. :pr:`3059`
-   ``send_file`` hỗ trợ nội dung một phần ``BytesIO``.
    :issue:`2957`
-   ``open_resource`` chấp nhận chế độ tệp "rt". Điều này vẫn làm
    điều tương tự như "r". :issue:`3163`
-   Thuộc tính ``MethodView.methods`` được thiết lập trong một lớp cơ sở được sử dụng bởi
    các lớp con. :issue:`3138`
-   ``Flask.jinja_options`` là một ``dict`` thay vì một
    ``ImmutableDict`` để cho phép cấu hình dễ dàng hơn. Các thay đổi vẫn phải
    được thực hiện trước khi tạo môi trường. :pr:`3190`
-   ``JSONMixin`` của Flask cho các wrapper yêu cầu và phản hồi đã được
    chuyển vào Werkzeug. Sử dụng phiên bản của Werkzeug với hỗ trợ cụ thể cho
    Flask. Điều này tăng phụ thuộc Werkzeug lên >= 0.15.
    :issue:`3125`
-   Điểm nhập lệnh ``flask`` được đơn giản hóa để tận dụng
    hỗ trợ trình tải lại tốt hơn của Werkzeug 0.15. Điều này tăng phụ thuộc Werkzeug
    lên >= 0.15. :issue:`3022`
-   Hỗ trợ ``static_url_path`` kết thúc bằng dấu gạch chéo.
    :issue:`3134`
-   Hỗ trợ ``static_folder`` trống mà không yêu cầu thiết lập một
    ``static_url_path`` trống cũng như vậy. :pr:`3124`
-   ``jsonify`` hỗ trợ các đối tượng ``dataclass``. :pr:`3195`
-   Cho phép tùy chỉnh ``Flask.url_map_class`` được sử dụng cho định tuyến.
    :pr:`3069`
-   Cổng máy chủ phát triển có thể được đặt thành 0, điều này bảo hệ điều hành
    chọn một cổng khả dụng. :issue:`2926`
-   Giá trị trả về từ ``cli.load_dotenv`` nhất quán hơn với
    tài liệu. Nó sẽ trả về ``False`` nếu python-dotenv không được
    cài đặt, hoặc nếu đường dẫn đã cho không phải là một tệp. :issue:`2937`
-   Hỗ trợ signaling có một stub cho phương thức ``connect_via`` khi
    thư viện Blinker không được cài đặt. :pr:`3208`
-   Thêm một tùy chọn ``--extra-files`` vào lệnh CLI ``flask run`` để
    chỉ định các tệp bổ sung sẽ kích hoạt trình tải lại khi thay đổi.
    :issue:`2897`
-   Cho phép trả về một từ điển từ một hàm view. Tương tự như cách
    trả về một chuỗi sẽ tạo ra một phản hồi ``text/html``, trả về
    một dict sẽ gọi ``jsonify`` để tạo ra một phản hồi ``application/json``.
    :pr:`3111`
-   Các blueprint có một nhóm Click ``cli`` giống như ``app.cli``. Các lệnh CLI
    được đăng ký với một blueprint sẽ có sẵn dưới dạng một nhóm dưới
    lệnh ``flask``. :issue:`1357`.
-   Khi sử dụng test client như một trình quản lý ngữ cảnh (``with client:``),
    tất cả các ngữ cảnh yêu cầu được bảo tồn sẽ bị pop khi khối thoát,
    đảm bảo các ngữ cảnh lồng nhau được dọn dẹp chính xác. :pr:`3157`
-   Hiển thị thông báo lỗi tốt hơn khi kiểu trả về của view không được
    hỗ trợ. :issue:`3214`
-   ``flask.testing.make_test_environ_builder()`` đã bị phản đối để
    ủng hộ một lớp mới ``flask.testing.EnvironBuilder``. :pr:`3232`
-   Lệnh ``flask run`` không còn thất bại nếu Python không được xây dựng
    với hỗ trợ SSL. Sử dụng tùy chọn ``--cert`` sẽ hiển thị một
    thông báo lỗi thích hợp. :issue:`3211`
-   Khớp URL hiện xảy ra sau khi ngữ cảnh yêu cầu được đẩy, thay vì
    khi nó được tạo. Điều này cho phép các bộ chuyển đổi URL tùy chỉnh truy cập
    các ngữ cảnh ứng dụng và yêu cầu, chẳng hạn như để truy vấn cơ sở dữ liệu cho một id.
    :issue:`3088`


Version 1.0.4
-------------

Đã phát hành 2019-07-04

-   Thông tin khóa cho ``BadRequestKeyError`` không còn bị xóa
    bên ngoài chế độ gỡ lỗi, vì vậy các trình xử lý lỗi vẫn có thể truy cập nó. Điều này
    yêu cầu nâng cấp lên Werkzeug 0.15.5. :issue:`3249`
-   ``send_file`` trích dẫn url các ký tự ":" và "/" để hỗ trợ tên tệp UTF-8
    tương thích hơn trong một số trình duyệt. :issue:`3074`
-   Các bản sửa lỗi cho các trình tải import :pep:`451` và pytest 5.x. :issue:`3275`
-   Hiển thị thông báo về dotenv trên stderr thay vì stdout. :issue:`3285`


Version 1.0.3
-------------

Đã phát hành 2019-05-17

-   ``send_file`` mã hóa tên tệp dưới dạng ASCII thay vì Latin-1
    (ISO-8859-1). Điều này sửa lỗi tương thích với Gunicorn, cái mà
    nghiêm ngặt hơn về mã hóa header so với :pep:`3333`. :issue:`2766`
-   Cho phép các CLI tùy chỉnh sử dụng ``FlaskGroup`` để thiết lập cờ gỡ lỗi mà không
    luôn bị ghi đè dựa trên các biến môi trường.
    :pr:`2765`
-   ``flask --version`` xuất ra phiên bản của Werkzeug và đơn giản hóa
    phiên bản Python. :pr:`2825`
-   ``send_file`` xử lý một ``attachment_filename`` là một chuỗi Python 2
    gốc (bytes) với các byte được mã hóa UTF-8. :issue:`2933`
-   Một trình xử lý lỗi catch-all được đăng ký cho ``HTTPException`` sẽ không
    xử lý ``RoutingException``, cái được sử dụng nội bộ trong quá trình
    định tuyến. Điều này sửa lỗi hành vi không mong muốn đã được giới thiệu
    trong 1.0. :pr:`2986`
-   Truyền đối số ``json`` cho ``app.test_client`` không
    đẩy/pop thêm một ngữ cảnh ứng dụng. :issue:`2900`


Version 1.0.2
-------------

Đã phát hành 2018-05-02

-   Sửa nhiều vấn đề tương thích ngược hơn với việc hợp nhất các dấu gạch chéo giữa
    một tiền tố blueprint và route. :pr:`2748`
-   Sửa lỗi với lệnh ``flask routes`` khi không có route nào.
    :issue:`2751`


Version 1.0.1
-------------

Đã phát hành 2018-04-29

-   Sửa việc đăng ký các partial (không có ``__name__``) dưới dạng các hàm view.
    :pr:`2730`
-   Không xử lý các danh sách được trả về từ các hàm view giống như các tuple.
    Chỉ các tuple được hiểu là dữ liệu phản hồi. :issue:`2736`
-   Các dấu gạch chéo thừa giữa ``url_prefix`` của một blueprint và một URL route
    được hợp nhất. Điều này sửa một số vấn đề tương thích ngược với
    thay đổi trong 1.0. :issue:`2731`, :issue:`2742`
-   Chỉ bẫy các lỗi ``BadRequestKeyError`` trong chế độ gỡ lỗi, không phải tất cả
    các lỗi ``BadRequest``. Điều này cho phép ``abort(400)`` tiếp tục
    hoạt động như mong đợi. :issue:`2735`
-   Biến môi trường ``FLASK_SKIP_DOTENV`` có thể được đặt thành ``1``
    để bỏ qua việc tự động tải các tệp dotenv. :issue:`2722`


Version 1.0
-----------

Đã phát hành 2018-04-26

-   Python 2.6 và 3.3 không còn được hỗ trợ.
-   Tăng phiên bản phụ thuộc tối thiểu lên các phiên bản ổn định mới nhất:
    Werkzeug >= 0.14, Jinja >= 2.10, itsdangerous >= 0.24, Click >= 5.1.
    :issue:`2586`
-   Bỏ qua ``app.run`` khi một ứng dụng Flask được chạy từ dòng lệnh.
    Điều này tránh một số hành vi gây nhầm lẫn khi gỡ lỗi.
-   Thay đổi mặc định cho ``JSONIFY_PRETTYPRINT_REGULAR`` thành
    ``False``. ``~json.jsonify`` trả về một định dạng nhỏ gọn theo mặc định,
    và một định dạng thụt lề trong chế độ gỡ lỗi. :pr:`2193`
-   ``Flask.__init__`` chấp nhận đối số ``host_matching`` và thiết lập
    nó trên ``Flask.url_map``. :issue:`1559`
-   ``Flask.__init__`` chấp nhận đối số ``static_host`` và truyền
    nó dưới dạng đối số ``host`` khi định nghĩa tuyến tĩnh.
    :issue:`1559`
-   ``send_file`` hỗ trợ Unicode trong ``attachment_filename``.
    :pr:`2223`
-   Truyền đối số ``_scheme`` từ ``url_for`` đến
    ``Flask.handle_url_build_error``. :pr:`2017`
-   ``Flask.add_url_rule`` chấp nhận đối số ``provide_automatic_options``
    để vô hiệu hóa việc thêm phương thức ``OPTIONS``. :pr:`1489`
-   Các lớp con ``MethodView`` kế thừa các trình xử lý phương thức từ các lớp cơ sở.
    :pr:`1936`
-   Các lỗi gây ra trong khi mở session ở đầu
    yêu cầu được xử lý bởi các trình xử lý lỗi của ứng dụng. :pr:`2254`
-   Các blueprint đã có thêm các thuộc tính ``Blueprint.json_encoder`` và
    ``Blueprint.json_decoder`` để ghi đè encoder và decoder của ứng dụng.
    :pr:`1898`
-   ``Flask.make_response`` ném ra ``TypeError`` thay vì
    ``ValueError`` cho các kiểu phản hồi xấu. Các thông báo lỗi đã được
    cải thiện để mô tả lý do tại sao kiểu không hợp lệ. :pr:`2256`
-   Thêm lệnh CLI ``routes`` để xuất các route đã đăng ký trên
    ứng dụng. :pr:`2259`
-   Hiển thị cảnh báo khi miền cookie session là một tên máy chủ trần (bare hostname) hoặc một địa chỉ IP,
    vì những điều này có thể không hoạt động bình thường trong một số trình duyệt, chẳng hạn như
    Chrome. :pr:`2282`
-   Cho phép địa chỉ IP làm miền cookie session chính xác. :pr:`2282`
-   ``SESSION_COOKIE_DOMAIN`` được thiết lập nếu nó được phát hiện thông qua
    ``SERVER_NAME``. :pr:`2282`
-   Tự động phát hiện factory ứng dụng không đối số được gọi là ``create_app`` hoặc
    ``make_app`` từ ``FLASK_APP``. :pr:`2297`
-   Các hàm factory không bắt buộc phải nhận tham số ``script_info``
    để làm việc với lệnh ``flask``. Nếu chúng nhận một tham số duy nhất
    hoặc một tham số có tên ``script_info``, đối tượng ``ScriptInfo``
    sẽ được truyền vào. :pr:`2319`
-   ``FLASK_APP`` có thể được đặt thành một factory ứng dụng, với các đối số nếu
    cần, ví dụ ``FLASK_APP=myproject.app:create_app('dev')``.
    :pr:`2326`
-   ``FLASK_APP`` có thể trỏ đến các gói cục bộ không được cài đặt trong
    chế độ có thể chỉnh sửa, mặc dù ``pip install -e`` vẫn được ưu tiên.
    :pr:`2414`
-   Thuộc tính lớp ``View``
    ``View.provide_automatic_options`` được thiết lập trong ``View.as_view``, để được
    phát hiện bởi ``Flask.add_url_rule``. :pr:`2316`
-   Xử lý lỗi sẽ thử các trình xử lý được đăng ký cho ``blueprint, code``,
    ``app, code``, ``blueprint, exception``, ``app, exception``.
    :pr:`2314`
-   ``Cookie`` được thêm vào header ``Vary`` của phản hồi nếu session
    được truy cập trong suốt yêu cầu (và không bị xóa). :pr:`2288`
-   ``Flask.test_request_context`` chấp nhận các đối số ``subdomain`` và
    ``url_scheme`` để sử dụng khi xây dựng URL cơ sở.
    :pr:`1621`
-   Thiết lập ``APPLICATION_ROOT`` thành ``'/'`` theo mặc định. Đây đã là
    mặc định ngầm định khi nó được thiết lập thành ``None``.
-   ``TRAP_BAD_REQUEST_ERRORS`` được bật theo mặc định trong chế độ gỡ lỗi.
    ``BadRequestKeyError`` có một thông báo với khóa xấu trong chế độ gỡ lỗi
    thay vì thông báo yêu cầu xấu chung chung. :pr:`2348`
-   Cho phép đăng ký các thẻ mới với ``TaggedJSONSerializer`` để hỗ trợ
    lưu trữ các kiểu khác trong cookie session. :pr:`2352`
-   Chỉ mở session nếu yêu cầu chưa được đẩy lên
    ngăn xếp ngữ cảnh. Điều này cho phép các generator ``stream_with_context``
    truy cập cùng một session mà view chứa nó sử dụng. :pr:`2354`
-   Thêm đối số từ khóa ``json`` cho các phương thức yêu cầu của test client.
    Điều này sẽ dump đối tượng đã cho dưới dạng JSON và thiết lập
    loại nội dung thích hợp. :pr:`2358`
-   Trích xuất xử lý JSON sang một mixin được áp dụng cho cả các lớp ``Request`` và
    ``Response``. Điều này thêm các phương thức ``Response.is_json`` và
    ``Response.get_json`` vào phản hồi để làm cho việc kiểm tra phản hồi JSON
    dễ dàng hơn nhiều. :pr:`2358`
-   Đã xóa bộ nhớ đệm trình xử lý lỗi vì nó gây ra kết quả không mong muốn
    cho một số phân cấp kế thừa ngoại lệ. Đăng ký các trình xử lý
    một cách rõ ràng cho từng ngoại lệ nếu bạn muốn tránh duyệt qua
    MRO. :pr:`2362`
-   Sửa mã hóa JSON không chính xác của các datetime nhận biết (aware), không phải UTC. :pr:`2374`
-   Tự động tải lại template sẽ tôn trọng chế độ gỡ lỗi ngay cả khi
    ``Flask.jinja_env`` đã được truy cập. :pr:`2373`
-   Mã cũ bị phản đối sau đây đã bị xóa. :issue:`2385`

    -   ``flask.ext`` - import các tiện ích mở rộng trực tiếp bằng tên của chúng thay vì
        thông qua namespace ``flask.ext``. Ví dụ,
        ``import flask.ext.sqlalchemy`` trở thành
        ``import flask_sqlalchemy``.
    -   ``Flask.init_jinja_globals`` - mở rộng
        ``Flask.create_jinja_environment`` thay thế.
    -   ``Flask.error_handlers`` - được theo dõi bởi
        ``Flask.error_handler_spec``, sử dụng ``Flask.errorhandler``
        để đăng ký các trình xử lý.
    -   ``Flask.request_globals_class`` - sử dụng
        ``Flask.app_ctx_globals_class`` thay thế.
    -   ``Flask.static_path`` - sử dụng ``Flask.static_url_path`` thay thế.
    -   ``Request.module`` - sử dụng ``Request.blueprint`` thay thế.

-   Thuộc tính ``Request.json`` không còn bị phản đối. :issue:`1421`
-   Hỗ trợ truyền một ``EnvironBuilder`` hoặc ``dict`` đến
    ``test_client.open``. :pr:`2412`
-   Lệnh ``flask`` và ``Flask.run`` sẽ tải các biến môi trường
    từ các tệp ``.env`` và ``.flaskenv`` nếu python-dotenv được
    cài đặt. :pr:`2416`
-   Khi truyền một URL đầy đủ đến test client, scheme trong URL được
    sử dụng thay vì ``PREFERRED_URL_SCHEME``. :pr:`2430`
-   ``Flask.logger`` đã được đơn giản hóa. Cấu hình ``LOGGER_NAME`` và
    ``LOGGER_HANDLER_POLICY`` đã bị xóa. Logger luôn được
    đặt tên là ``flask.app``. Mức độ chỉ được thiết lập trong lần truy cập đầu tiên, nó
    không kiểm tra ``Flask.debug`` mỗi lần. Chỉ một định dạng được sử dụng,
    không phải các định dạng khác nhau tùy thuộc vào ``Flask.debug``. Không có trình xử lý nào bị
    xóa, và một trình xử lý chỉ được thêm vào nếu chưa có trình xử lý nào được
    cấu hình. :pr:`2436`
-   Tên hàm view blueprint không được chứa dấu chấm. :pr:`2450`
-   Sửa một ``ValueError`` gây ra bởi các yêu cầu ``Range`` không hợp lệ trong một số
    trường hợp. :issue:`2526`
-   Máy chủ phát triển sử dụng các luồng theo mặc định. :pr:`2529`
-   Tải các tệp cấu hình với ``silent=True`` sẽ bỏ qua các lỗi ``ENOTDIR``.
    :pr:`2581`
-   Truyền các tùy chọn ``--cert`` và ``--key`` đến ``flask run`` để chạy
    máy chủ phát triển qua HTTPS. :pr:`2606`
-   Đã thêm ``SESSION_COOKIE_SAMESITE`` để kiểm soát thuộc tính ``SameSite``
    trên cookie session. :pr:`2607`
-   Đã thêm ``Flask.test_cli_runner`` để tạo một Click runner có thể
    gọi các lệnh CLI Flask để kiểm thử. :pr:`2636`
-   Khớp tên miền phụ bị vô hiệu hóa theo mặc định và thiết lập
    ``SERVER_NAME`` không ngầm kích hoạt nó. Nó có thể được kích hoạt bằng cách
    truyền ``subdomain_matching=True`` đến hàm tạo ``Flask``.
    :pr:`2635`
-   Một dấu gạch chéo cuối cùng duy nhất bị loại bỏ khỏi ``url_prefix``
    của blueprint khi nó được đăng ký với ứng dụng. :pr:`2629`
-   ``Request.get_json`` không cache kết quả nếu phân tích cú pháp thất bại khi
    ``silent`` là true. :issue:`2651`
-   ``Request.get_json`` không còn chấp nhận các mã hóa tùy ý. JSON đến
    nên được mã hóa bằng UTF-8 theo :rfc:`8259`, nhưng Flask sẽ
    tự động phát hiện UTF-8, -16, hoặc -32. :pr:`2691`
-   Đã thêm ``MAX_COOKIE_SIZE`` và ``Response.max_cookie_size`` để
    kiểm soát khi Werkzeug cảnh báo về các cookie lớn mà các trình duyệt có thể
    bỏ qua. :pr:`2693`
-   Đã cập nhật chủ đề tài liệu để làm cho tài liệu trông đẹp hơn trong các cửa sổ
    nhỏ. :pr:`2709`
-   Viết lại tài liệu hướng dẫn và dự án ví dụ để thực hiện một cách tiếp cận
    có cấu trúc hơn để giúp người dùng mới tránh các cạm bẫy phổ biến.
    :pr:`2676`


Version 0.12.5
--------------

Đã phát hành 2020-02-10

-   Ghim Werkzeug ở mức < 1.0.0. :issue:`3497`


Version 0.12.4
--------------

Đã phát hành 2018-04-29

-   Đóng gói lại 0.12.3 để sửa lỗi bố cục gói. :issue:`2728`


Version 0.12.3
--------------

Đã phát hành 2018-04-26

-   ``Request.get_json`` không còn chấp nhận các mã hóa tùy ý.
    JSON đến nên được mã hóa bằng UTF-8 theo :rfc:`8259`, nhưng
    Flask sẽ tự động phát hiện UTF-8, -16, hoặc -32. :issue:`2692`
-   Sửa một cảnh báo Python về import khi sử dụng ``python -m flask``.
    :issue:`2666`
-   Sửa một ``ValueError`` gây ra bởi các yêu cầu ``Range`` không hợp lệ trong một số
    trường hợp.


Version 0.12.2
--------------

Đã phát hành 2017-05-16

-   Sửa một lỗi trong ``safe_join`` trên Windows.


Version 0.12.1
--------------

Đã phát hành 2017-03-31

-   Ngăn ``flask run`` hiển thị ``NoAppException`` khi một
    ``ImportError`` xảy ra bên trong mô-đun ứng dụng được import.
-   Sửa hành vi mã hóa của ``app.config.from_pyfile`` cho Python 3.
    :issue:`2118`
-   Sử dụng cấu hình ``SERVER_NAME`` nếu nó hiện diện làm giá trị mặc định
    cho ``app.run``. :issue:`2109`, :pr:`2152`
-   Gọi ``ctx.auto_pop`` với đối tượng ngoại lệ thay vì ``None``,
    trong trường hợp một ``BaseException`` như ``KeyboardInterrupt``
    được ném ra trong một trình xử lý yêu cầu.


Version 0.12
------------

Đã phát hành 2016-12-21, tên mã Punsch

-   Lệnh cli hiện phản hồi với ``--version``.
-   Đoán Mimetype và tạo ETag cho các đối tượng giống tệp trong
    ``send_file`` đã bị xóa. :issue:`104`, :pr`1849`
-   Đoán Mimetype trong ``send_file`` hiện thất bại ồn ào và không quay lại
    ``application/octet-stream``. :pr:`1988`
-   Làm cho ``flask.safe_join`` có thể nối nhiều đường dẫn giống như
    ``os.path.join`` :pr:`1730`
-   Hoàn tác một thay đổi hành vi làm cho máy chủ phát triển bị sập thay vì
    trả về Lỗi Máy chủ Nội bộ. :pr:`2006`
-   Gọi chính xác các trình xử lý phản hồi cho cả việc gửi yêu cầu
    thông thường cũng như các trình xử lý lỗi.
-   Vô hiệu hóa lan truyền logger theo mặc định cho logger ứng dụng.
-   Thêm hỗ trợ cho các yêu cầu phạm vi trong ``send_file``.
-   ``app.test_client`` bao gồm môi trường mặc định đặt trước, hiện có thể
    được thiết lập trực tiếp, thay vì mỗi ``client.get``.
-   Sửa lỗi sập khi chạy dưới PyPy3. :pr:`1814`


Version 0.11.1
--------------

Đã phát hành 2016-06-07

-   Đã sửa một lỗi ngăn ``FLASK_APP=foobar/__init__.py`` hoạt động. :pr:`1872`


Version 0.11
------------

Đã phát hành 2016-05-29, tên mã Absinthe

-   Đã thêm hỗ trợ tuần tự hóa các mảng cấp cao nhất vào ``jsonify``. Điều này
    gây ra rủi ro bảo mật trong các trình duyệt cổ đại.
-   Đã thêm tín hiệu before_render_template.
-   Đã thêm ``**kwargs`` vào ``Flask.test_client`` để hỗ trợ truyền
    các đối số từ khóa bổ sung cho hàm tạo của
    ``Flask.test_client_class``.
-   Đã thêm khóa cấu hình ``SESSION_REFRESH_EACH_REQUEST`` kiểm soát
    hành vi set-cookie. Nếu được đặt thành ``True`` một session vĩnh viễn sẽ được
    làm mới mỗi yêu cầu và được gia hạn thời gian tồn tại, nếu được đặt thành
    ``False`` nó sẽ chỉ được sửa đổi nếu session thực sự thay đổi.
    Các session không vĩnh viễn không bị ảnh hưởng bởi điều này và sẽ luôn
    hết hạn nếu cửa sổ trình duyệt đóng.
-   Đã làm cho Flask hỗ trợ các mimetype JSON tùy chỉnh cho dữ liệu đến.
-   Đã thêm hỗ trợ trả về các tuple ở dạng ``(response,
    headers)`` từ một hàm view.
-   Đã thêm ``Config.from_json``.
-   Đã thêm ``Flask.config_class``.
-   Đã thêm ``Config.get_namespace``.
-   Các template không còn được tự động tải lại bên ngoài chế độ gỡ lỗi.
    Điều này có thể được cấu hình với khóa cấu hình mới ``TEMPLATES_AUTO_RELOAD``.
-   Đã thêm một giải pháp thay thế cho một hạn chế trong trình tải namespace
    của Python 3.3.
-   Đã thêm hỗ trợ cho các đường dẫn gốc rõ ràng khi sử dụng các gói namespace
    của Python 3.3.
-   Đã thêm ``flask`` và mô-đun ``flask.cli`` để khởi động
    máy chủ gỡ lỗi cục bộ thông qua hệ thống click CLI. Điều này được khuyến nghị
    hơn phương thức cũ ``flask.run()`` vì nó hoạt động nhanh hơn và đáng tin cậy
    hơn do thiết kế khác và cũng thay thế
    ``Flask-Script``.
-   Các trình xử lý lỗi khớp với các lớp cụ thể hiện được kiểm tra trước,
    do đó cho phép bắt các ngoại lệ là lớp con của các ngoại lệ HTTP
    (trong ``werkzeug.exceptions``). Điều này làm cho tác giả tiện ích mở rộng có thể
    tạo ra các ngoại lệ mà theo mặc định sẽ dẫn đến lỗi HTTP mà họ chọn, nhưng có thể
    bị bắt bằng một trình xử lý lỗi tùy chỉnh nếu muốn.
-   Đã thêm ``Config.from_mapping``.
-   Flask hiện sẽ ghi nhật ký theo mặc định ngay cả khi gỡ lỗi bị tắt. Định dạng nhật ký
    hiện được mã hóa cứng nhưng việc xử lý nhật ký mặc định có thể bị tắt
    thông qua khóa cấu hình ``LOGGER_HANDLER_POLICY``.
-   Đã xóa chức năng mô-đun bị phản đối.
-   Đã thêm cờ cấu hình ``EXPLAIN_TEMPLATE_LOADING`` khi được
    bật sẽ hướng dẫn Flask giải thích cách nó định vị các template.
    Điều này sẽ giúp người dùng gỡ lỗi khi các template sai được tải.
-   Thực thi xử lý blueprint theo thứ tự chúng được đăng ký để
    tải template.
-   Đã chuyển bộ test suite sang py.test.
-   Phản đối ``request.json`` để ủng hộ ``request.get_json()``.
-   Thêm các định nghĩa dấu phân cách "pretty" và "compressed" trong phương thức jsonify().
    Giảm kích thước phản hồi JSON khi
    ``JSONIFY_PRETTYPRINT_REGULAR=False`` bằng cách xóa khoảng trắng không cần thiết
    được bao gồm theo mặc định sau các dấu phân cách.
-   Các phản hồi JSON hiện được kết thúc bằng ký tự dòng mới, vì
    quy ước là các tệp văn bản UNIX kết thúc bằng dòng mới và một số
    máy khách không xử lý tốt khi thiếu dòng mới này. :pr:`1262`
-   Phương thức ``OPTIONS`` được cung cấp tự động hiện đã bị vô hiệu hóa chính xác
    nếu người dùng đã đăng ký quy tắc ghi đè với
    phiên bản chữ thường ``options``. :issue:`1288`
-   ``flask.json.jsonify`` hiện hỗ trợ kiểu ``datetime.date``.
    :pr:`1326`
-   Không rò rỉ thông tin ngoại lệ của các ngoại lệ đã bắt cho các trình xử lý
    teardown ngữ cảnh. :pr:`1393`
-   Cho phép các lớp con môi trường Jinja tùy chỉnh. :pr:`1422`
-   Đã cập nhật hướng dẫn phát triển tiện ích mở rộng.
-   ``flask.g`` hiện có các phương thức ``pop()`` và ``setdefault``.
-   Bật autoescape cho ``flask.templating.render_template_string``
    theo mặc định. :pr:`1515`
-   ``flask.ext`` hiện đã bị phản đối. :pr:`1484`
-   ``send_from_directory`` hiện ném ra BadRequest nếu tên tệp không hợp lệ
    trên hệ điều hành máy chủ. :pr:`1763`
-   Đã thêm biến cấu hình ``JSONIFY_MIMETYPE``. :pr:`1728`
-   Các ngoại lệ trong quá trình xử lý teardown sẽ không còn để lại các ngữ cảnh
    ứng dụng xấu lảng vảng xung quanh.
-   Đã sửa trường hợp kiểm thử ``test_appcontext_signals()`` bị hỏng.
-   Ném ra một ``AttributeError`` trong ``helpers.find_package`` với một
    thông báo hữu ích giải thích lý do tại sao nó được ném ra khi một hook import :pep:`302`
    được sử dụng mà không có phương thức ``is_package()``.
-   Đã sửa một vấn đề khiến các ngoại lệ được ném ra trước khi vào một ngữ cảnh yêu cầu
    hoặc ứng dụng được chuyển đến các trình xử lý teardown.
-   Đã sửa một vấn đề với các tham số truy vấn bị xóa khỏi các yêu cầu
    trong test client khi các URL tuyệt đối được yêu cầu.
-   Đã biến ``@before_first_request`` thành một decorator như dự định.
-   Đã sửa một lỗi etags khi gửi một luồng tệp với một tên.
-   Đã sửa ``send_from_directory`` không mở rộng đến đường dẫn gốc ứng dụng
    một cách chính xác.
-   Đã thay đổi logic của các trình xử lý trước yêu cầu đầu tiên để lật cờ
    sau khi gọi. Điều này sẽ cho phép một số cách sử dụng có khả năng
    nguy hiểm nhưng có lẽ nên được cho phép.
-   Đã sửa lỗi Python 3 khi một trình xử lý từ
    ``app.url_build_error_handlers`` ném lại ``BuildError``.


Version 0.10.1
--------------

Đã phát hành 2013-06-14

-   Đã sửa một vấn đề trong đó ``|tojson`` không trích dẫn các dấu nháy đơn khiến
    bộ lọc không hoạt động bình thường trong các thuộc tính HTML. Bây giờ có thể
    sử dụng bộ lọc đó trong các thuộc tính được trích dẫn đơn. Điều này sẽ
    làm cho việc sử dụng bộ lọc đó với angular.js dễ dàng hơn.
-   Đã thêm hỗ trợ cho chuỗi byte trở lại hệ thống session. Điều này
    đã phá vỡ khả năng tương thích với trường hợp phổ biến của những người đặt dữ liệu
    nhị phân để xác minh mã thông báo vào session.
-   Đã sửa một vấn đề trong đó việc đăng ký cùng một phương thức hai lần cho cùng một
    endpoint sẽ kích hoạt một ngoại lệ không chính xác.


Version 0.10
------------

Đã phát hành 2013-06-13, tên mã Limoncello

-   Đã thay đổi định dạng tuần tự hóa cookie mặc định từ pickle sang JSON để
    hạn chế tác động mà kẻ tấn công có thể thực hiện nếu khóa bí mật bị rò rỉ.
-   Đã thêm các phương thức ``template_test`` ngoài họ phương thức
    ``template_filter`` đã tồn tại.
-   Đã thêm các phương thức ``template_global`` ngoài họ phương thức
    ``template_filter`` đã tồn tại.
-   Thiết lập header content-length cho x-sendfile.
-   Bộ lọc ``tojson`` hiện không thoát các khối script trong trình phân tích cú pháp HTML5.
-   ``tojson`` được sử dụng trong các template hiện an toàn theo mặc định. Điều này được
    cho phép do hành vi thoát khác nhau.
-   Flask hiện sẽ ném ra lỗi nếu bạn cố gắng đăng ký một hàm mới
    trên một endpoint đã được sử dụng.
-   Đã thêm mô-đun wrapper xung quanh simplejson và thêm tuần tự hóa mặc định
    của các đối tượng datetime. Điều này cho phép tùy chỉnh dễ dàng hơn nhiều
    về cách JSON được xử lý bởi Flask hoặc bất kỳ tiện ích mở rộng Flask nào.
-   Đã xóa bí danh mô-đun nội bộ bị phản đối ``flask.session``. Sử dụng
    ``flask.sessions`` thay thế để lấy mô-đun session. Điều này không được
    nhầm lẫn với ``flask.session`` là proxy session.
-   Các template hiện có thể được render mà không cần ngữ cảnh yêu cầu. Hành vi
    hơi khác một chút vì các đối tượng ``request``, ``session`` và ``g``
    sẽ không có sẵn và các bộ xử lý ngữ cảnh của blueprint không được gọi.
-   Đối tượng config hiện có sẵn cho template như một biến toàn cục thực sự
    và không thông qua một bộ xử lý ngữ cảnh, điều này làm cho nó có sẵn ngay cả trong
    các template được import theo mặc định.
-   Đã thêm một tùy chọn để tạo JSON được mã hóa không phải ascii, điều này sẽ
    dẫn đến ít byte được truyền qua mạng hơn. Nó bị tắt theo mặc định để không gây
    nhầm lẫn với các thư viện hiện có có thể mong đợi ``flask.json.dumps`` trả về byte theo mặc định.
-   ``flask.g`` hiện được lưu trữ trên ngữ cảnh ứng dụng thay vì ngữ cảnh yêu cầu.
-   ``flask.g`` hiện đã có thêm một phương thức ``get()`` để không bị lỗi trên
    các mục không tồn tại.
-   ``flask.g`` hiện có thể được sử dụng với toán tử ``in`` để xem những gì
    được định nghĩa và nó hiện có thể lặp lại và sẽ yield tất cả các thuộc tính được lưu trữ.
-   ``flask.Flask.request_globals_class`` đã được đổi tên thành
    ``flask.Flask.app_ctx_globals_class``, đây là một cái tên tốt hơn cho những gì
    nó làm kể từ 0.10.
-   ``request``, ``session`` và ``g`` hiện cũng được thêm vào như các proxy cho
    ngữ cảnh template, điều này làm cho chúng có sẵn trong các template được import.
    Tuy nhiên, người ta phải rất cẩn thận với những thứ đó vì
    việc sử dụng bên ngoài macro có thể gây ra bộ nhớ đệm.
-   Flask sẽ không còn gọi sai các trình xử lý lỗi nếu một ngoại lệ proxy
    được truyền qua.
-   Đã thêm một giải pháp thay thế cho cookie của chrome trong localhost không hoạt động như
    dự định với tên miền.
-   Đã thay đổi logic để chọn mặc định cho các giá trị cookie từ session
    để hoạt động tốt hơn với Google Chrome.
-   Đã thêm tín hiệu ``message_flashed`` giúp đơn giản hóa việc kiểm thử flashing.
-   Đã thêm hỗ trợ sao chép các ngữ cảnh yêu cầu để làm việc tốt hơn
    với greenlets.
-   Đã xóa các lớp con ngoại lệ HTTP JSON tùy chỉnh. Nếu bạn đang dựa vào
    chúng, bạn có thể giới thiệu lại chúng một cách dễ dàng. Tuy nhiên, việc sử dụng
    chúng không được khuyến khích vì giao diện bị lỗi.
-   Yêu cầu Python đã thay đổi: yêu cầu Python 2.6 hoặc 2.7 ngay bây giờ để
    chuẩn bị cho cổng Python 3.3.
-   Đã thay đổi cách hệ thống teardown được thông báo về các ngoại lệ. Điều này
    hiện đáng tin cậy hơn trong trường hợp một cái gì đó xử lý một ngoại lệ giữa chừng
    trong quá trình xử lý lỗi.
-   Bảo tồn ngữ cảnh yêu cầu trong chế độ gỡ lỗi hiện giữ thông tin ngoại lệ
    xung quanh, điều đó có nghĩa là các trình xử lý teardown có thể
    phân biệt lỗi với các trường hợp thành công.
-   Đã thêm biến cấu hình ``JSONIFY_PRETTYPRINT_REGULAR``.
-   Flask hiện sắp xếp các khóa JSON theo mặc định để không làm hỏng bộ nhớ đệm HTTP do
    các hạt giống băm khác nhau giữa các worker khác nhau.
-   Đã thêm các tín hiệu ``appcontext_pushed`` và ``appcontext_popped``.
-   Phương thức run tích hợp hiện tính đến ``SERVER_NAME``
    khi chọn cổng mặc định để chạy.
-   Đã thêm ``flask.request.get_json()`` thay thế cho thuộc tính cũ
    ``flask.request.json``.


Version 0.9
-----------

Đã phát hành 2012-07-01, tên mã Campari

-   ``Request.on_json_loading_failed`` hiện trả về phản hồi định dạng JSON
    theo mặc định.
-   Hàm ``url_for`` hiện có thể tạo các neo đến các liên kết được tạo.
-   Hàm ``url_for`` hiện cũng có thể tạo rõ ràng các quy tắc URL
    cụ thể cho một phương thức HTTP nhất định.
-   Logger hiện chỉ trả về cài đặt nhật ký gỡ lỗi nếu nó không được thiết lập
    rõ ràng.
-   Hủy đăng ký phụ thuộc vòng tròn giữa môi trường WSGI và
    đối tượng yêu cầu khi tắt yêu cầu. Điều này có nghĩa là
    environ ``werkzeug.request`` sẽ là ``None`` sau khi phản hồi được
    trả về máy chủ WSGI nhưng có lợi thế là bộ thu gom rác
    không cần thiết trên CPython để xé bỏ yêu cầu trừ khi
    người dùng tự tạo ra các phụ thuộc vòng tròn.
-   Session hiện được lưu trữ sau các callback để nếu payload session
    được lưu trữ trong session, bạn vẫn có thể sửa đổi nó trong một callback sau yêu cầu.
-   Lớp ``Flask`` sẽ tránh import tên import được cung cấp nếu
    có thể (tham số đầu tiên bắt buộc), để mang lại lợi ích cho các công cụ xây dựng
    các thể hiện Flask theo chương trình. Lớp Flask sẽ quay lại
    sử dụng import trên các hệ thống có hook mô-đun tùy chỉnh, ví dụ: Google App
    Engine, hoặc khi tên import nằm trong kho lưu trữ zip (thường là
    egg) trước Python 2.7.
-   Các blueprint hiện có một decorator để thêm các bộ lọc template tùy chỉnh
    trên toàn ứng dụng, ``Blueprint.app_template_filter``.
-   Các lớp Flask và Blueprint hiện có một phương thức không phải decorator để
    thêm các bộ lọc template tùy chỉnh trên toàn ứng dụng,
    ``Flask.add_template_filter`` và
    ``Blueprint.add_app_template_filter``.
-   Hàm ``get_flashed_messages`` hiện cho phép render các danh mục tin nhắn
    đã flash trong các khối riêng biệt, thông qua đối số ``category_filter``.
-   Phương thức ``Flask.run`` hiện chấp nhận ``None`` cho các đối số ``host`` và
    ``port``, sử dụng các giá trị mặc định khi ``None``. Điều này cho phép
    gọi run bằng cách sử dụng các giá trị cấu hình, ví dụ:
    ``app.run(app.config.get('MYHOST'), app.config.get('MYPORT'))``,
    với hành vi thích hợp cho dù tệp cấu hình có được cung cấp hay không.
-   Phương thức ``render_template`` hiện chấp nhận một iterable của
    tên template hoặc một tên template duy nhất. Trước đây, nó chỉ
    chấp nhận một tên template duy nhất. Trên một iterable, template đầu tiên
    được tìm thấy sẽ được render.
-   Đã thêm ``Flask.app_context`` hoạt động rất giống với ngữ cảnh yêu cầu
    nhưng chỉ cung cấp quyền truy cập vào ứng dụng hiện tại. Điều này
    cũng thêm hỗ trợ cho việc tạo URL mà không cần ngữ cảnh yêu cầu
    hoạt động.
-   Các hàm view hiện có thể trả về một tuple với thể hiện đầu tiên là
    một thể hiện của ``Response``. Điều này cho phép trả về
    ``jsonify(error="error msg"), 400`` từ một hàm view.
-   ``Flask`` và ``Blueprint`` hiện cung cấp một hook ``get_send_file_max_age``
    cho các lớp con để ghi đè hành vi phục vụ các tệp tĩnh
    từ Flask khi sử dụng ``Flask.send_static_file`` (được sử dụng cho
    trình xử lý tệp tĩnh mặc định) và ``helpers.send_file``. Hook này được
    cung cấp một tên tệp, ví dụ cho phép thay đổi kiểm soát bộ nhớ đệm
    theo phần mở rộng tệp. Max-age mặc định cho ``send_file``
    và các tệp tĩnh có thể được cấu hình thông qua biến cấu hình mới
    ``SEND_FILE_MAX_AGE_DEFAULT``, được sử dụng
    trong triển khai ``get_send_file_max_age`` mặc định.
-   Đã sửa một giả định trong triển khai session có thể phá vỡ
    message flashing trên các triển khai session sử dụng bộ nhớ ngoài.
-   Đã thay đổi hành vi của các giá trị trả về tuple từ các hàm. Chúng
    không còn là đối số cho đối tượng phản hồi, chúng hiện có một ý nghĩa
    xác định.
-   Đã thêm ``Flask.request_globals_class`` để cho phép một lớp cụ thể
    được sử dụng khi tạo thể hiện ``g`` của mỗi yêu cầu.
-   Đã thêm thuộc tính ``required_methods`` vào các hàm view để buộc thêm
    các phương thức khi đăng ký.
-   Đã thêm ``flask.after_this_request``.
-   Đã thêm ``flask.stream_with_context`` và khả năng đẩy ngữ cảnh
    nhiều lần mà không tạo ra hành vi không mong muốn.


Version 0.8.1
-------------

Đã phát hành 2012-07-01

-   Đã sửa một vấn đề với mô-đun ``flask.session`` không có tài liệu để không
    hoạt động bình thường trên Python 2.5. Nó không nên được sử dụng nhưng đã gây ra
    một số vấn đề cho các trình quản lý gói.


Version 0.8
-----------

Đã phát hành 2011-09-29, tên mã Rakija

-   Đã cấu trúc lại hỗ trợ session thành một giao diện session để việc
    triển khai các session có thể thay đổi mà không cần phải
    ghi đè lớp Flask.
-   Các cookie session trống hiện được xóa đúng cách tự động.
-   Các hàm view hiện có thể chọn không nhận triển khai OPTIONS
    tự động.
-   Các ngoại lệ HTTP và lỗi Bad Request hiện có thể bị bẫy để chúng
    hiển thị bình thường trong traceback.
-   Flask trong chế độ gỡ lỗi hiện đang phát hiện một số vấn đề phổ biến và cố gắng
    cảnh báo bạn về chúng.
-   Flask trong chế độ gỡ lỗi hiện sẽ phàn nàn với một lỗi assertion nếu một
    view được đính kèm sau khi yêu cầu đầu tiên được xử lý. Điều này cung cấp
    phản hồi sớm hơn khi người dùng quên import mã view trước.
-   Đã thêm khả năng đăng ký các callback chỉ được kích hoạt một lần
    khi bắt đầu yêu cầu đầu tiên với
    ``Flask.before_first_request``.
-   Dữ liệu JSON không đúng định dạng hiện sẽ kích hoạt một ngoại lệ HTTP bad request
    thay vì lỗi giá trị thường dẫn đến lỗi máy chủ nội bộ 500
    nếu không được xử lý. Đây là một thay đổi không tương thích
    ngược.
-   Các ứng dụng hiện không chỉ có đường dẫn gốc nơi chứa tài nguyên và
    mô-đun mà còn có đường dẫn instance là nơi được
    chỉ định để thả các tệp được sửa đổi khi chạy (tải lên
    v.v.). Ngoài ra, về mặt khái niệm, điều này chỉ phụ thuộc vào instance và nằm ngoài
    kiểm soát phiên bản nên đây là nơi hoàn hảo để đặt các tệp cấu hình
    v.v.
-   Đã thêm biến cấu hình ``APPLICATION_ROOT``.
-   Đã triển khai ``TestClient.session_transaction`` để dễ dàng sửa đổi
    các session từ môi trường kiểm thử.
-   Đã cấu trúc lại test client nội bộ. Biến cấu hình ``APPLICATION_ROOT``
    cũng như ``SERVER_NAME`` hiện được sử dụng đúng cách
    bởi test client làm mặc định.
-   Đã thêm ``View.decorators`` để hỗ trợ việc trang trí đơn giản hơn cho các view
    có thể cắm (dựa trên lớp).
-   Đã sửa một vấn đề trong đó test client nếu được sử dụng với câu lệnh "with"
    đã không kích hoạt việc thực thi các trình xử lý teardown.
-   Đã thêm kiểm soát tốt hơn đối với các tham số cookie session.
-   Các yêu cầu HEAD đến một method view hiện tự động gửi đến
    phương thức ``get`` nếu không có trình xử lý nào được triển khai.
-   Đã triển khai gói ảo ``flask.ext`` để import các tiện ích mở rộng
    từ đó.
-   Việc bảo tồn ngữ cảnh trên các ngoại lệ hiện là một thành phần không thể thiếu
    của chính Flask và không còn là của test client nữa. Điều này đã làm sạch
    một số logic nội bộ và giảm tỷ lệ các ngữ cảnh yêu cầu chạy trốn
    trong unittests.
-   Đã sửa phương thức ``list_templates`` của môi trường Jinja không
    trả về tên chính xác khi các blueprint hoặc mô-đun có
    liên quan.


Version 0.7.2
-------------

Đã phát hành 2011-07-06

-   Đã sửa một vấn đề với các bộ xử lý URL không hoạt động bình thường trên
    các blueprint.


Version 0.7.1
-------------

Đã phát hành 2011-06-29

-   Đã thêm import future bị thiếu làm hỏng khả năng tương thích 2.5.
-   Đã sửa một vấn đề chuyển hướng vô hạn với các blueprint.


Version 0.7
-----------

Đã phát hành 2011-06-28, tên mã Grappa

-   Đã thêm ``Flask.make_default_options_response`` có thể được sử dụng bởi
    các lớp con để thay đổi hành vi mặc định cho các phản hồi ``OPTIONS``.
-   Các biến cục bộ không bị ràng buộc hiện ném ra một ``RuntimeError`` thích hợp thay vì một
    ``AttributeError``.
-   Đoán Mimetype và hỗ trợ etag dựa trên các đối tượng tệp hiện
    đã bị phản đối cho ``send_file`` vì nó không đáng tin cậy. Truyền
    tên tệp thay thế hoặc đính kèm etag của riêng bạn và cung cấp một
    mimetype thích hợp bằng tay.
-   Xử lý tệp tĩnh cho các mô-đun hiện yêu cầu tên của thư mục tĩnh
    phải được cung cấp rõ ràng. Việc tự động phát hiện trước đó không
    đáng tin cậy và gây ra sự cố trên Google's App Engine. Cho đến 1.0
    hành vi cũ sẽ tiếp tục hoạt động nhưng đưa ra cảnh báo phụ thuộc.
-   Đã sửa một vấn đề để Flask chạy trên jython.
-   Đã thêm một biến cấu hình ``PROPAGATE_EXCEPTIONS`` có thể được
    sử dụng để lật cài đặt lan truyền ngoại lệ mà trước đây
    chỉ được liên kết với ``DEBUG`` và hiện được liên kết với ``DEBUG``
    hoặc ``TESTING``.
-   Flask không còn phụ thuộc nội bộ vào các quy tắc được thêm thông qua
    hàm ``add_url_rule`` và hiện cũng có thể chấp nhận các quy tắc werkzeug
    thông thường được thêm vào bản đồ url.
-   Đã thêm một phương thức ``endpoint`` vào đối tượng ứng dụng flask cho phép
    đăng ký một callback đến một endpoint tùy ý với một
    decorator.
-   Sử dụng Last-Modified để gửi tệp tĩnh thay vì Date được
    giới thiệu không chính xác trong 0.6.
-   Đã thêm ``create_jinja_loader`` để ghi đè quy trình tạo loader.
-   Đã triển khai một cờ im lặng cho ``config.from_pyfile``.
-   Đã thêm decorator ``teardown_request``, cho các hàm nên chạy
    ở cuối yêu cầu bất kể ngoại lệ có xảy ra hay không.
    Ngoài ra, hành vi cho ``after_request`` đã được thay đổi. Nó hiện không
    còn được thực thi khi một ngoại lệ được ném ra.
-   Đã triển khai ``has_request_context``.
-   Phản đối ``init_jinja_globals``. Ghi đè phương thức
    ``Flask.create_jinja_environment`` thay thế để đạt được
    chức năng tương tự.
-   Đã thêm ``safe_join``.
-   Việc giải nén dữ liệu yêu cầu JSON tự động hiện xem xét tham số
    mimetype charset.
-   Không sửa đổi session trên ``get_flashed_messages`` nếu không có
    tin nhắn nào trong session.
-   Các trình xử lý ``before_request`` hiện có thể hủy bỏ các yêu cầu với
    các lỗi.
-   Không thể định nghĩa các trình xử lý ngoại lệ người dùng. Bằng cách đó bạn
    có thể cung cấp các thông báo lỗi tùy chỉnh từ một trung tâm trung tâm cho các
    lỗi nhất định có thể xảy ra trong quá trình xử lý yêu cầu (ví dụ
    lỗi kết nối cơ sở dữ liệu, thời gian chờ từ các tài nguyên từ xa v.v.).
-   Các blueprint có thể cung cấp các trình xử lý lỗi cụ thể cho blueprint.
-   Đã triển khai các view dựa trên lớp chung.


Version 0.6.1
-------------

Đã phát hành 2010-12-31

-   Đã sửa một vấn đề trong đó phản hồi ``OPTIONS`` mặc định không
    hiển thị tất cả các phương thức hợp lệ trong header ``Allow``.
-   Cú pháp tải template Jinja hiện cho phép "./" trước một
    đường dẫn tải template. Trước đây điều này gây ra sự cố với các
    thiết lập mô-đun.
-   Đã sửa một vấn đề trong đó cài đặt tên miền phụ cho các mô-đun bị bỏ qua
    đối với thư mục tĩnh.
-   Đã sửa một vấn đề bảo mật cho phép máy khách tải xuống các tệp tùy ý
    nếu máy chủ lưu trữ là hệ điều hành dựa trên windows và
    máy khách sử dụng dấu gạch chéo ngược để thoát khỏi thư mục mà các tệp được
    hiển thị.


Version 0.6
-----------

Đã phát hành 2010-07-27, tên mã Whisky

-   Các hàm sau yêu cầu hiện được gọi theo thứ tự ngược lại của
    đăng ký.
-   OPTIONS hiện được Flask tự động triển khai trừ khi
    ứng dụng thêm rõ ràng 'OPTIONS' làm phương thức vào quy tắc URL. Trong
    trường hợp này, không có xử lý OPTIONS tự động nào khởi động.
-   Các quy tắc tĩnh hiện thậm chí còn được áp dụng nếu không có thư mục tĩnh cho
    mô-đun. Điều này được triển khai để hỗ trợ GAE sẽ xóa
    thư mục tĩnh nếu nó là một phần của ánh xạ trong tệp .yml.
-   ``Flask.config`` hiện có sẵn trong các template dưới dạng ``config``.
-   Các bộ xử lý ngữ cảnh sẽ không còn ghi đè các giá trị được truyền trực tiếp đến
    hàm render.
-   Đã thêm khả năng giới hạn dữ liệu yêu cầu đến với giá trị cấu hình mới
    ``MAX_CONTENT_LENGTH``.
-   Endpoint cho phương thức ``Module.add_url_rule`` hiện là tùy chọn
    để nhất quán với hàm cùng tên trên
    đối tượng ứng dụng.
-   Đã thêm một hàm ``make_response`` giúp đơn giản hóa việc tạo các thể hiện
    đối tượng phản hồi trong các view.
-   Đã thêm hỗ trợ tín hiệu dựa trên blinker. Tính năng này hiện là
    tùy chọn và được cho là sẽ được sử dụng bởi các tiện ích mở rộng và ứng dụng. Nếu
    bạn muốn sử dụng nó, hãy đảm bảo đã cài đặt ``blinker``.
-   Đã cấu trúc lại cách tạo bộ điều hợp URL. Quá trình này hiện
    hoàn toàn có thể tùy chỉnh với phương thức ``Flask.create_url_adapter``.
-   Các mô-đun hiện có thể đăng ký cho một tên miền phụ thay vì chỉ một tiền tố
    URL. Điều này làm cho nó có thể liên kết toàn bộ mô-đun với một
    tên miền phụ có thể cấu hình.


Version 0.5.2
-------------

Đã phát hành 2010-07-15

-   Đã sửa một vấn đề khác với việc tải template từ các thư mục khi
    các mô-đun được sử dụng.


Version 0.5.1
-------------

Đã phát hành 2010-07-06

-   Sửa một vấn đề với việc tải template từ các thư mục khi các mô-đun
    được sử dụng.


Version 0.5
-----------

Đã phát hành 2010-07-06, tên mã Calvados

-   Đã sửa một lỗi với các tên miền phụ gây ra bởi việc không thể
    chỉ định tên máy chủ. Tên máy chủ hiện có thể được thiết lập với
    khóa cấu hình ``SERVER_NAME``. Khóa này hiện cũng được sử dụng để thiết lập
    cookie session trên toàn tên miền phụ.
-   Autoescaping không còn hoạt động cho tất cả các template. Thay vào đó nó
    chỉ hoạt động cho ``.html``, ``.htm``, ``.xml`` và ``.xhtml``. Bên trong
    các template, hành vi này có thể được thay đổi với thẻ ``autoescape``.
-   Đã cấu trúc lại Flask nội bộ. Nó hiện bao gồm nhiều hơn một tệp
    duy nhất.
-   ``send_file`` hiện phát ra etags và có khả năng thực hiện các phản hồi
    có điều kiện tích hợp sẵn.
-   (tạm thời) bỏ hỗ trợ cho các ứng dụng nén. Đây là một
    tính năng hiếm khi được sử dụng và dẫn đến một số hành vi khó hiểu.
-   Đã thêm hỗ trợ cho các thư mục template và tệp tĩnh theo gói.
-   Đã xóa hỗ trợ cho ``create_jinja_loader`` không còn được sử dụng
    trong 0.5 do hỗ trợ mô-đun được cải thiện.
-   Đã thêm một hàm trợ giúp để hiển thị các tệp từ bất kỳ thư mục nào.


Version 0.4
-----------

Đã phát hành 2010-06-18, tên mã Rakia

-   Đã thêm khả năng đăng ký các trình xử lý lỗi toàn ứng dụng từ
    các mô-đun.
-   Các trình xử lý ``Flask.after_request`` hiện cũng được gọi nếu yêu cầu
    chết với một ngoại lệ và một trang xử lý lỗi khởi động.
-   Test client không có khả năng bảo tồn ngữ cảnh yêu cầu cho
    lâu hơn một chút. Điều này cũng có thể được sử dụng để kích hoạt các yêu cầu tùy chỉnh
    không pop ngăn xếp yêu cầu để kiểm thử.
-   Vì thư viện chuẩn Python lưu trữ các logger, tên của
    logger hiện có thể định cấu hình để hỗ trợ tốt hơn cho unittests.
-   Đã thêm công tắc ``TESTING`` có thể kích hoạt các trình trợ giúp unittesting.
-   Logger chuyển sang chế độ ``DEBUG`` ngay bây giờ nếu gỡ lỗi được bật.


Version 0.3.1
-------------

Đã phát hành 2010-05-28

-   Đã sửa một lỗi báo cáo lỗi với ``Config.from_envvar``.
-   Đã xóa một số mã không sử dụng.
-   Bản phát hành không còn bao gồm các tệp còn sót lại của quá trình phát triển (thư mục .git
    cho các chủ đề, tài liệu đã xây dựng trong tệp zip và pdf và một số
    tệp .pyc)


Version 0.3
-----------

Đã phát hành 2010-05-28, tên mã Schnaps

-   Đã thêm hỗ trợ cho các danh mục cho các tin nhắn đã flash.
-   Ứng dụng hiện cấu hình một ``logging.Handler`` và sẽ ghi nhật ký
    các ngoại lệ xử lý yêu cầu vào logger đó khi không ở chế độ gỡ lỗi.
    Điều này làm cho nó có thể nhận thư về lỗi máy chủ chẳng hạn
    ví dụ.
-   Đã thêm hỗ trợ cho ràng buộc ngữ cảnh không yêu cầu sử dụng
    câu lệnh with để chơi trong bảng điều khiển.
-   Ngữ cảnh yêu cầu hiện có sẵn trong câu lệnh with
    làm cho nó có thể đẩy thêm ngữ cảnh yêu cầu hoặc pop nó.
-   Đã thêm hỗ trợ cho các cấu hình.


Version 0.2
-----------

Đã phát hành 2010-05-12, tên mã Jägermeister

-   Các bản sửa lỗi khác nhau
-   Tích hợp hỗ trợ JSON
-   Đã thêm hàm trợ giúp ``get_template_attribute``.
-   ``Flask.add_url_rule`` hiện cũng có thể đăng ký một hàm view.
-   Đã cấu trúc lại việc gửi yêu cầu nội bộ.
-   Máy chủ lắng nghe trên 127.0.0.1 theo mặc định ngay bây giờ để sửa các vấn đề với
    chrome.
-   Đã thêm hỗ trợ URL bên ngoài.
-   Đã thêm hỗ trợ cho ``send_file``.
-   Hỗ trợ mô-đun và cấu trúc lại xử lý yêu cầu nội bộ để hỗ trợ tốt hơn
    các ứng dụng có thể cắm.
-   Các session có thể được thiết lập là vĩnh viễn ngay bây giờ trên cơ sở từng session.
-   Báo cáo lỗi tốt hơn về các khóa bí mật bị thiếu.
-   Đã thêm hỗ trợ cho Google Appengine.


Version 0.1
-----------

Đã phát hành 2010-04-16

-   Bản phát hành xem trước công khai đầu tiên.
