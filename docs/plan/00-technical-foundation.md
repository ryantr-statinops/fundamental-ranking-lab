# Stage 00 — Nền tảng kỹ thuật

Trạng thái: đã triển khai; acceptance cục bộ và CI Windows/Linux đã qua. Stage 01 tiếp tục với pilot dữ liệu thật. Stage này chỉ dựng foundation bằng fixtures, chưa thu thập dữ liệu diện rộng hoặc tính hiệu quả đầu tư.

## Mục tiêu và đầu vào

Tạo package Python chạy local trên Windows hiện tại, có thể tái lập trên Linux CI, với cấu hình kiểm tra được, storage bất biến và CLI thống nhất. Đầu vào là quy tắc trong idea, không có code hay dependency manifest sẵn.

## Stack được chọn

| Lớp | Lựa chọn | Vai trò |
|---|---|---|
| Runtime | CPython 3.13; requires-python >=3.13,<3.14 | Một minor version cho v1, giảm biến thiên môi trường |
| Dependencies/build | uv, pyproject.toml, uv.lock, Hatchling | Package src-layout; khóa dependency và cài bằng uv sync --locked |
| Tables/numerics | pandas, NumPy | Biến đổi bảng và tính toán; chưa thêm Polars |
| Storage/query | PyArrow Parquet, DuckDB embedded | Parquet là dữ liệu chuẩn; DuckDB views/cache có thể dựng lại |
| Providers | HTTPX; yfinance adapter riêng | HTTP timeout/retry/cache; không để provider types đi vào domain logic |
| Validation/config/CLI | Pydantic v2, TOML qua tomllib, Typer | Typed config và commands; từ chối khóa cấu hình không biết |
| Calendar | exchange-calendars, tzdata | Sessions XNYS và America/New_York; xác minh lịch NASDAQ/AMEX và ngoại lệ |
| Analysis/reporting | SciPy, statsmodels, Matplotlib, Jinja2 | Thêm khi stage 06 cần; HTML tĩnh, CSV và PNG |
| Development | pytest, Ruff, mypy; JupyterLab optional | Fixtures offline, lint/type checks; notebook không giữ business logic |

Đây là lựa chọn kiến trúc, chưa phải kiểm chứng thư viện chạy tương thích. Khi thực hiện stage 00: chọn patch Python 3.13 được hỗ trợ mới nhất, pin chính xác trong `.python-version`; resolve dependency stable tương thích một lần và commit uv.lock. Ghi cả uv version dùng vào manifest. Nếu thiếu wheel Windows/CI hoặc có lỗi tương thích, ghi blocker trước đổi minor/stack; không hạ version âm thầm. Không cài công cụ trong đợt viết plan này.

## Cấu trúc và cấu hình

Tạo `src/fundamental_ranking_lab/` gồm data, universe, features, ranking, backtest, evaluation, reporting; entrypoint `frl`. Configs TOML ở `configs/`, tests theo unit/integration/fixtures; notebooks chỉ gọi package.

Các thư mục runtime: `data/raw/` lưu phản hồi/filing gốc theo source/hash, `data/normalized/` lưu bảng chuẩn, `data/snapshots/` theo cutoff/version, `artifacts/<run_id>/` lưu manifest/log/outputs/reports. Data/artifacts/cache/.venv và thông tin riêng phải gitignore; chỉ commit fixtures nhỏ đã kiểm tra và config không chứa secret. DuckDB catalog là cache local, chỉ một writer; không là nguồn sự thật duy nhất.

Primary config tách research parameters khỏi provider settings; không có silent defaults thay quy tắc đã khóa. Config chứa data_root/artifact_root, source priority, timeout/rate/retry, cutoffs, approved groups, factor/mapping versions, caps/λ/costs, sample/split/seed. SEC User-Agent có contact qua biến môi trường `FRL_SEC_USER_AGENT`, không commit email cá nhân hoặc secret. Resolve config thành JSON canonical; tách research hash khỏi execution hash đã loại private contact/secret. Research hash không chứa machine-local paths hoặc contact; manifest vẫn pin input-content hashes, code/lock/schema/factor/mapping versions. Chi tiết và acceptance ở [kế hoạch bàn giao tài liệu](documentation-delivery.md).

## Hợp đồng dữ liệu và CLI

Tạo schema version `1` cho các bảng: entities/securities, identifier_history, memberships, industry_history, filings, facts, prices, corporate_actions, gate_results. Khóa nghiệp vụ và unique constraints được kiểm tra trước publish partition; invalid rows vào quarantine có reason, không tự drop.

Identifiers là string; CIK giữ leading zeros; calendar date tách timezone-aware timestamp UTC. Historical mapping có valid_from/valid_to và known_at, tách public availability khỏi retrieved_at; effective intervals dạng [from,to), không overlap trong cùng business key và revision/as-of view. Giữ các revisions bất biến để sửa một khoảng hiệu lực cũ mà không xóa lịch sử; quy tắc chọn revision cần được kiểm thử. Facts giữ số gốc dạng text/Decimal và unit/scale/context; chỉ chuyển float64 tại lớp ratios, missing là null kèm reason, không dùng infinity. Mọi bảng gắn source/source_record_id/schema_version; derived rows có input lineage. Prices có raw OHLCV, currency, security_id và timestamp; adjusted prices chỉ trường riêng.

Interface chung dự kiến: `uv run frl <command> --config <file>`, offline transformation thêm `--input-run <run_id>`. Commands theo stage: doctor, pilot, ingest, audit-universe, snapshots, features, rank, backtest, evaluate, quarterly, replay. Chỉ đăng ký command khi được triển khai; stage chưa hỗ trợ phải báo rõ, không xuất success giả. `doctor` không tự cài dependency hoặc tải dữ liệu.

Exit codes: 0 đạt cổng, 2 cấu hình sai, 3 data gate thất bại, 1 lỗi chương trình/IO/network không khắc phục. Run thất bại vẫn lưu manifest và JSONL log; không xuất artifact trạng thái approved. Run ID dùng UTC timestamp + UUID; write vào thư mục tạm cùng volume rồi atomic rename khi hoàn chỉnh. `latest` pointer chỉ đổi sau thành công, không overwrite run cũ.

## Công việc và nghiệm thu

### Checklist bàn giao

- [x] Khởi tạo package `src/`, entrypoint `frl`, config TOML mẫu và validator từ chối khóa lạ.
- [x] Thêm helper manifest/hash và Parquet writer có kiểm schema, publish atomic, không overwrite.
- [x] Thêm schema version 1 và bộ kiểm thử offline cho khóa trùng, interval overlap, UTC timestamps, units, missing reasons, lineage, Parquet và `doctor`.
- [x] Thêm CI Windows/Linux chạy locked sync, Ruff, mypy và pytest.
- [x] Bổ sung technical references, setup/config/troubleshooting guides và cập nhật README.
- [x] Resolve và commit `uv.lock`; cài môi trường dev trên CPython 3.13.
- [x] Chạy pytest, Ruff, mypy, CLI doctor và import/calendar/Parquet smoke thành công trên Windows.
- [x] CI Windows và Linux xanh trên commit đã push.
- [x] Đối chiếu checklist cuối; giữ các kiểm tra về dữ liệu thật và audit ở stage 01/02.

Các ô được đánh dấu hoàn thành chỉ xác nhận file đã được tạo; chúng không thay thế các cổng chạy thực tế ở dưới.

1. Khởi tạo package, config models, CLI doctor, manifest/hash và storage adapters tối thiểu; sample config không có credentials.
2. Tạo fixtures đủ thử timezone, raw-to-Parquet, identity interval, null reason và lineage. Offline transform không được gọi mạng ngầm.
3. Thêm GitHub Actions Windows/Linux: uv sync --locked, Ruff check/format --check, mypy, pytest offline; không gọi provider thật trong CI mặc định. Smoke network là lệnh riêng có chủ đích, không cron.
4. Kiểm tra schema validation từ chối duplicate/overlap/bad unit/naive timestamp; rollback publish nếu lỗi; logs không chứa contact/secret. Hai lần transform cùng input/config/version cho bảng và checksums nội dung tương đương, bỏ metadata run_id/timestamp khỏi phép so.
5. Bàn giao lockfile, dependency inventory, config reference, artifact/schema examples và hướng dẫn môi trường khi code tồn tại. Viết technical references cùng setup/config guides theo [ma trận bàn giao](documentation-delivery.md); README dẫn tới tài liệu đã kiểm chứng. Kiểm tra đổi local path/contact không đổi research hash, đổi logical input phải được nhận diện qua input hash. Chưa qua import/Parquet/calendar smoke trên cả Windows/Linux thì chưa đạt stage 00.

## Nguồn kỹ thuật

[Python version lifecycle](https://devguide.python.org/versions/), [uv project workflow](https://docs.astral.sh/uv/guides/projects/), [uv locking/sync](https://docs.astral.sh/uv/concepts/projects/sync/), [PyArrow Parquet](https://arrow.apache.org/docs/python/parquet.html), [DuckDB Parquet](https://duckdb.org/docs/stable/data/parquet/overview). `--locked` yêu cầu lock khớp project; không dùng `--frozen` để che lockfile lỗi thời. Các lựa chọn trên phục vụ quy mô nghiên cứu local, không phải benchmark tốc độ đã đo của dự án.
