# Stage 04 — Eligibility, scoring và ranking baseline

Trạng thái: **Đã triển khai baseline ranking & candidate selection**. Phụ thuộc: [stage 01](01-data-feasibility-pilot.md) đã đạt cổng và trích xuất ratios Point-in-Time. Quy tắc gốc: [universe/factors/ranking](../idea/02-universe-factors-ranking.md).

### Tiến độ implementation:
- [x] Xây dựng Data Contracts & Parquet Schemas cho Ranking (`StockScore`, `IndustryRanking`, `CandidateSelection`).
- [x] Hiện thực chuẩn hóa vị thế tương đối `percentile_rank()` theo công thức Fractional Mid-Rank: $\frac{\text{midrank}-1}{n-1}$ kèm đảo chiều Low-is-Good (debt_ratio).
- [x] Hiện thực tính điểm 4 trục (`Quality`, `Growth`, `Financial Health`, `Valuation`) và tổng hợp `Core Composite Score` với ngưỡng tối thiểu $\ge 3/4$ trục.
- [x] Hiện thực xếp hạng 17 ngành Ken French bằng Median Composite của các cổ phiếu eligible.
- [x] Hiện thực thuật toán chọn Top-100 cổ phiếu `select_top_candidates()` với cơ chế xử lý ranh giới Border Ties Inclusion.
- [x] Tích hợp lệnh CLI `uv run frl rank --input-run <run_path>` xuất đủ 3 bảng Parquet: `scores.parquet`, `industry_ranking.parquet`, `top_candidates.parquet`.
- [x] Smoke check trực tiếp trên run thật của Stage 01 (`20261028T162118.392055Z-0671bf04-5bfd-445a-9bc8-f09ce09bf762`).

## Mục tiêu và đầu vào

Output: eligibility ledger (pass/fail từng filter và raw counts), ratio/axis/composite scores, industry_ranking, within_group_ranking và candidates Parquet; CSV readable cho mỗi cutoff; summary manifest và diagnostics. Mỗi tỷ lệ phải có mẫu số và scope, cả nhóm bị loại. Zero variance và low member counts là flags hiển thị, không che khỏi báo cáo.

Schema keys: cutoff/entity cho eligibility/composite, cutoff/entity/ratio cho normalized values, cutoff/industry cho ranking. Mỗi output gắn feature/config/approved-group version và parent run_id. Candidate order dùng score giảm rồi security_id tăng để trình bày; thứ tự này không được phá ties inclusion.

## Kiểm tra nghiệm thu

- Tập raw eligibility không phụ thuộc score; outliers/missing không tạo vòng lặp giữa filtering và normalization. Fixtures gồm 0/1/n members, ratio n=0/n=1 và toàn ties.
- Kiểm tra goodness direction, equal/reweight và hai mốc coverage 50%/3-of-4; compare hand-calculated score fixtures.
- 99 mã eligible lấy 99; ties vị trí 100 lấy >100; không rounded-score false ties. Một doanh nghiệp không xuất hiện hai lần.
- Median ngành không đổi khi chỉ thay số lượng candidate export; within-group score không thay primary lõi. Breadth và coverage đúng mẫu số.
- Hoán vị thứ tự input không đổi kết quả nghiệp vụ; thêm cột returns hoặc dữ liệu sau cutoff không tác động output. Stable output ordering/checksum với cùng pinned inputs.

Nếu eligibility/source gate chưa đạt thì xuất ledger và blockers, không tự hạ hard filters để đủ 100. Bàn giao candidates/scores/industry percentile inputs cho [stage 05](05-portfolio-backtest.md). Chưa khẳng định ranking có khả năng dự báo trước kiểm định ngoài mẫu.
