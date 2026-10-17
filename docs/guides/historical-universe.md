# Historical universe — Stage 02 offline

Implementation offline có sẵn; Stage 01 chưa có dữ liệu thật đạt cổng, Stage 02 chưa đạt cổng dữ liệu. Không cần SEC contact cho các lệnh mặc định dưới đây.

## Chạy bằng fixtures

Từ root repo, sau `uv sync --locked --extra dev`:

```powershell
uv run frl ingest --config configs/history.toml
uv run frl audit-universe --config configs/history.toml --input-run <ingest_run_id>
uv run frl ingest --config configs/history.toml --input-run <ingest_run_id>
uv run frl ingest --config configs/history.toml --resume-run <ingest_run_id>
```

Mỗi lệnh tạo run mới; thay placeholder bằng run ID được in. `--input-run` đọc bundle/raw đã pin, không gọi mạng. `--resume-run` tái sử dụng checkpoint hợp lệ và chỉ tiếp tục requests chưa xong trong live mode; không sửa run nguồn. Không kết hợp hai flags. Replay/audit yêu cầu history fingerprint khớp; đổi đường dẫn local không đổi research fingerprint.

Sample dùng fixtures tổng hợp, hai common classes và sự kiện chưa xác minh; không có giá thị trường thật. Exit 3 là kết quả mong đợi. Exit 0 của ingestion chỉ xác nhận tác vụ thu thập hoàn tất, không chứng nhận universe. Exit 2 là config/input không hợp lệ; exit 1 là lỗi thực thi hoặc integrity.

## Đọc artifacts

Ingest tạo `bundle.json`, `raw_index.json`, `checkpoints.json`, `discovery.json`, blockers và manifest. Discovery từ SEC master indexes, submissions/history và filing headers chỉ tạo candidates; có filing không chứng minh listing.

Audit tạo 12 Parquet tables, `coverage.json`, `source_coverage.json`, `quarantine.json`, `discrepancies.json`, `unresolved_events.json`, `scope.json` và `audit.md`. Coverage giữ mẫu số independent list riêng với số candidates đã biết. `scope.approved=false` và `performance_permitted=false` với fixtures; không thể dùng để kết luận survivor-free hoặc performance.

## Chuẩn bị dữ liệu thật sau này

Đổi sang live chỉ sau khi Stage 01 được review. Config cần `mode="live"`, pilot run được duyệt và approved groups phù hợp. Cấu hình SEC contact local theo [pilot guide](running-pipeline.md); không ghi contact vào config hoặc Git.

Bundle JSON theo `HistoryBundle` gồm evidence có revision/public known_at/effective intervals/raw SHA-256, prices, mapping ranges + checksum, raw files, requests và independent membership lists theo ngày cutoff. Đường dẫn raw tương đối với bundle; không được thoát thư mục. Mapping checksum dùng canonical JSON theo `canonical_sha256`.

Requests chứa đúng `url`, `kind`, `entity_id`, `start`, `end`; checkpoint key bao gồm toàn request. SEC kinds: master_index, submissions, submissions_history, filing_text, filing_index, companyfacts. Price kind `prices` dùng URL `yfinance:SYMBOL`, end là ngày cutoff; adapter hiện lấy cửa sổ 75 ngày trước cutoff. Nhiều cửa sổ phải khai báo thành nhiều requests; chưa có crawler tự khám phá toàn bộ lịch sử. Adapter giá dùng rate budget chung trong run.

Raw mới tải chỉ là bằng chứng đầu vào. Discovery và giá provider không tự chuyển thành verified membership hoặc verified raw price convention. Người vận hành phải đối chiếu rồi nhập bundle evidence/price chuẩn hóa có lineage tới raw files được pin. Không coi nguồn miễn phí đã đủ coverage trước audit thật.

Scope completeness cần evidence kind `scope` được tham chiếu trong `completeness_evidence_ids`, hiệu lực tại cutoff, có `completeness_verified=true`, reviewer và independent_source khác source; đồng thời independent list phải khớp. Các trường này ghi nhận đánh giá con người, không tự chứng minh nguồn đầy đủ. Warm-up/outcome checks hiện chỉ là kiểm tra phạm vi tối thiểu; còn phải audit dữ liệu thật trước sử dụng.

Không có nguồn trả phí, Stooq, fuzzy identity matching, ranking hoặc backtest trong đợt này.
