# Stage 02 — Dữ liệu lịch sử và universe

Trạng thái: chưa bắt đầu. Phụ thuộc: [pilot](01-data-feasibility-pilot.md) đạt cổng cho từng nhóm/nguồn. Nguồn quy tắc: [universe](../idea/02-universe-factors-ranking.md), [identity/PIT](../idea/04-point-in-time-data.md).

## Mục tiêu và đầu vào

Mở rộng ingestion và chứng minh scope lịch sử có thể tái lập, không chỉ danh sách doanh nghiệp đang tồn tại. Đầu vào: raw pilot, adapters, group gate results, dictionary version và mục tiêu tín hiệu 2010Q1–2025Q4; cần warm-up và outcome cuối tới open quý II/2026. Chưa chọn scope theo kết quả returns.

## Công việc

1. Dựng catalog historical evidence từ SEC filing indexes/filing headers, tài liệu sàn/doanh nghiệp và nguồn giá miễn phí có thể kiểm chứng. Ghi candidate source, date range, quyền sử dụng và giới hạn; EDGAR current tickers hoặc yfinance search không đủ làm master universe lịch sử.
2. Dựng entities/securities và lịch sử ticker/exchange/class theo valid intervals và known_at. Xác minh country/security type/exclusions; tách CIK khỏi security_id. Phát hiện ticker reuse, CIK nhiều classes và mapping conflicts, không fuzzy merge tự động khi thiếu bằng chứng.
3. Dựng membership và historical SIC từ filings tại cutoff; pin mapping Ken French 17 bằng hash. REIT override 6798 theo idea; thiếu historical SIC thì reason code và không lấy SIC hiện tại backfill.
4. Thu raw prices/OHLCV, shares và events cho cả mã rời sàn. Chuẩn hóa split/dividend/merger/recovery và source provenance; giá raw với adjusted tách cột, không nối provider khác thang đo. Raw histories mới tải không sửa snapshots cũ.
5. Tính selection một class/doanh nghiệp bằng ADV20 đã biết; không dùng winner hiện tại cho cả lịch sử. Kiểm tra 8 quý công bố và hard filters ở từng cutoff; raw ratios/coverage được hoàn thiện stage 03.
6. Lập audit theo cutoff: số candidate, verified member, excluded từng lý do, unknown listing/identity/industry, coverage giá/shares/events và các mã delisted. So danh sách với nguồn historical evidence độc lập; pin bằng chứng và giải thích discrepancies.

## Hợp đồng đầu ra và CLI

CLI dự kiến: `frl ingest --config configs/history.toml` thu sources vào raw; `frl audit-universe --config configs/history.toml --input-run <ingest_id>` chạy offline. Dùng `uv run` trước các commands. Ingestion theo checkpoints/source/security/date, restart không tạo duplicate; rate/retry theo stage 01.

Output Parquet theo schema stage 00: securities, identifier_history, memberships, industry_history, filings/facts index, prices, shares, corporate_actions. Artifact audit gồm source coverage table, discrepancies/quarantine, unresolved event registry và scope manifest.

Scope manifest khóa cutoffs, approved groups, lịch sử được chứng minh, exclusions có lý do, source/mapping versions và completeness status. Schema unknown không được biến thành pass; uncertainty về danh sách bị thiếu phải ghi distinct với tỷ lệ coverage của danh sách đã biết. Không dùng “100% giá có trong downloaded list” để suy ra universe hoàn chỉnh.

## Kiểm tra nghiệm thu

- Tests ticker reuse, class switch, overlapping interval, duplicate entity/class, corporate event trước/sau hiệu lực và known_at tương lai. Hiện tại ticker đổi không làm đổi join quá khứ.
- Listing phải có nguồn ngoài việc “có giá”; exclusions đúng; đối chiếu ngẫu nhiên và mọi discrepancy trọng yếu với bằng chứng gốc. Không có hard conflict bị bỏ qua.
- Các cutoff được đề xuất có evidence audit và unresolved counts; giá/event chưa rõ trong sample ảnh hưởng được đánh dấu blocked cho primary performance. Không dùng −100% hay drop mã để sửa coverage.
- Coverage được tính trên danh sách lịch sử đã xác minh và ghi giới hạn nguồn. Audit chỉ có thể tuyên bố survivor-free khi nguồn chứng minh được đầy đủ, không suy từ việc có mã delisted.
- Rerun pinned raw cho output tương đương; staging/partition publish không làm lẫn phiên bản hoặc partial download.

## Điều kiện dừng và chuyển stage

Nếu không thể xác minh historical universe miễn phí, bàn giao data-feasibility limitation report. Có thể đề xuất thu hẹp nhóm/ngày theo bằng chứng trước xem performance, cập nhật idea/decision log rồi khóa manifest mới; không âm thầm chuyển sang present-day survivors hoặc nguồn trả phí. Không có scope lịch sử đủ bằng chứng thì chỉ tiếp tục prototype bằng fixtures, primary backtest bị chặn.

[Stage 03](03-point-in-time-features.md) nhận raw/index và scope manifest đã audit. Việc kiểm tra biến đổi features có thể làm trên phần dữ liệu đã xác minh; không làm phát sinh quyền kết luận performance cho phần còn blocked.
