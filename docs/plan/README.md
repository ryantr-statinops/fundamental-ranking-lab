# Kế hoạch thực thi Fundamental Ranking Lab

Ngày lập: 2026-10-15; cập nhật: 2026-10-16. Bộ tài liệu này chuyển [research specification](../idea/README.md) thành các stage thực thi. Stage 00 đã đạt cổng nền tảng. Stage 01 đã có implementation và chạy offline; feasibility pilot vẫn bị chặn vì chưa cấu hình contact SEC và chưa có dữ liệu/đối chiếu thực. Backtest chưa triển khai.

## Thứ tự và phụ thuộc

| Stage | Kế hoạch | Phụ thuộc | Trạng thái |
|---|---|---|---|
| 00 | [Nền tảng kỹ thuật](00-technical-foundation.md) | Bộ idea hiện tại | Đạt cổng nền tảng |
| 01 | [Pilot khả thi dữ liệu](01-data-feasibility-pilot.md) | 00 | Đang triển khai; pilot thật bị chặn |
| 02 | [Dữ liệu lịch sử và universe](02-historical-data-universe.md) | 01: nhóm/nguồn đạt cổng | Có implementation offline; dữ liệu thật chưa đạt cổng |
| 03 | [Point-in-time và features](03-point-in-time-features.md) | 02: manifest phạm vi đã khóa | Chưa bắt đầu |
| 04 | [Ranking baseline](04-ranking-baseline.md) | 03 | Chưa bắt đầu |
| 05 | [Portfolio và backtest](05-portfolio-backtest.md) | 02–04: dữ liệu đạt cổng | Chưa bắt đầu |
| 06 | [Validation và báo cáo](06-validation-reporting.md) | 05, cấu hình đã khóa trước test | Chưa bắt đầu |
| 07 | [Vận hành hàng quý](07-quarterly-operation.md) | 00–06 và kết luận vận hành | Chưa bắt đầu |

Đi tuần tự; stage 01 được xây lát cắt nhỏ ingestion/features để pilot, stage 02/03 mở rộng và củng cố lại cùng code, không tạo pipeline thứ hai. Fixtures tổng hợp có thể xây trước khi dữ liệu thật đạt cổng; không dùng chúng làm bằng chứng performance.

## Bàn giao tài liệu theo stage

[Kế hoạch bổ sung tài liệu](documentation-delivery.md) phân công nội dung technical, research và guides cho từng stage, với file dự kiến và tiêu chí nghiệm thu. Đây là công việc xuyên suốt 00–07, không phải stage mới thực hiện sau 07. [Bản đồ docs](../README.md) là điểm vào chung; các README nhóm phân biệt implementation và kết quả đã quan sát.

Stage 00 bắt đầu technical references và setup/config guides cùng code; stage 01–02 ghi bằng chứng pilot/nguồn/universe; stage 04–06 bổ sung hướng dẫn đọc kết quả và study findings; stage 07 hoàn thiện quarterly/backup runbooks. Không tạo sẵn hàng loạt hướng dẫn chạy khi commands chưa tồn tại.

## Ranh giới giữa idea và plan

- `docs/idea/` quyết định câu hỏi, công thức và giả định nghiên cứu. `docs/plan/` quyết định cách hiện thực, interfaces, artifacts và kiểm tra.
- Nếu pilot phát hiện giả định không khả thi, ghi issue và bằng chứng; cập nhật file idea liên quan, sổ quyết định và bảng tham số trước đổi implementation. Không âm thầm đổi research rule trong code.
- Stack mặc định: Python 3.13, uv, pandas/NumPy, PyArrow/Parquet, DuckDB, HTTPX, Pydantic, Typer; SciPy/statsmodels và Matplotlib ở giai đoạn đánh giá. Chi tiết và nguồn chính thức ở stage 00.
- V1 chạy local qua CLI, không có web app, server database, cloud scheduler hay giao dịch broker. ML, market impact và quy mô vốn thực chưa thuộc phạm vi.

## Quy ước hoàn thành stage

Mỗi stage có đầu vào, công việc, hợp đồng đầu ra, kiểm tra nghiệm thu và điều kiện dừng. Chỉ đổi trạng thái sang hoàn tất khi có artifact cùng đường dẫn/run_id, kết quả kiểm tra và ghi chú giới hạn. Trạng thái dùng: chưa bắt đầu → đang làm → đạt cổng; hoặc bị chặn kèm bằng chứng và việc cần giải quyết. Không gọi code chạy được là đã đạt cổng dữ liệu.

Mỗi run lưu manifest gồm git commit, hash mã nguồn đang chạy, lockfile hash, Python/uv versions, config/schema/factor/mapping versions, input checksums, cutoffs, artifacts và gate results. Dữ liệu gốc bất biến; kết quả cũ không bị overwrite. Network ingestion và biến đổi offline tách riêng để tái lập.

Primary giữ theo idea: top-100 gồm ties, score lõi + tilt λ=0,5, caps ngành 20%/doanh nghiệp 5%, phần dư giữ cash với lợi suất 0%, phí 10 bps một chiều; không tuning final test. Ngành không qua cổng không tự tham gia. Giá/event chưa giải quyết chặn kết luận performance liên quan.

## Mốc bàn giao

1. Stage 00: môi trường và contract chạy được bằng fixtures offline.
2. Stage 01: bằng chứng khả thi trên pilot; chấp nhận kết luận thiếu dữ liệu.
3. Stage 02–04: lịch sử có audit, snapshots và ranking truy nguyên được.
4. Stage 05–06: backtest accounting đúng và báo cáo Q1–Q3 ngoài mẫu.
5. Stage 07: chạy hàng quý có kiểm tra, replay, backup và xử lý thất bại.

Nghiên cứu hoàn thành không bắt buộc lợi nhuận dương. Nếu dữ liệu không đủ thì bàn giao feasibility report, ghi rõ backtest/inference chưa hoàn thành. Mỗi file tài liệu được commit riêng; cập nhật sau này cũng kiểm tra diff, stage đúng file và chỉ push sau khi kiểm tra phù hợp đạt.
