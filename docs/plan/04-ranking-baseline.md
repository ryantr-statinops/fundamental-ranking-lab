# Stage 04 — Eligibility, scoring và ranking baseline

Trạng thái: chưa bắt đầu. Phụ thuộc: [stage 03](03-point-in-time-features.md). Quy tắc gốc: [universe/factors/ranking](../idea/02-universe-factors-ranking.md).

## Mục tiêu và đầu vào

Tạo ranking cổ phiếu/ngành và candidate pool độc lập future returns. Đầu vào: historical membership, hard-filter data, approved group gates, raw_ratios và coverage đã pin. Không gọi provider hoặc load forward returns trong scoring module.

## Công việc

1. Áp identity/listing/group gates và hard filters: ≥ 8 quý đã công bố, ADV20 ≥ $1M, raw close ≥ $1, đủ 20 phiên giá/volume; chọn một class theo ADV20, ties security_id tăng dần. Eligibility cuối dựa raw coverage ≥ 50% ratios/trục và ≥ 3/4 trục, trước percentile.
2. Normalize mỗi ratio lõi trên nonmissing observations của eligible universe tại cutoff: (midrank−1)/(n−1), đảo chiều low-is-good, n=1 cho 0,5. n=0 unavailable; mọi ties midrank, không làm tròn trước selection.
3. Average valid ratios trong trục và valid trục trong composite; xuất số lượng và weights sau reweight. Không thêm change vào level hoặc gia tốc vào Growth chính.
4. Rank ngành bằng median composite lõi của toàn eligible universe, không chỉ candidate pool. Xuất median trục, IQR, breadth ≥ universe median, coverage, member/candidate counts, thay đổi hạng và score. Ngành không member unavailable; không gán 0.
5. Chọn top-100 composite lõi gồm toàn bộ ties tại vị trí 100; dưới 100 lấy hết, empty pool có output hợp lệ và reason. Output có thể >100, không cắt ties để tiện code.
6. Score đặc thù là nhánh tùy chọn theo group version đã qua dictionary gate, không đi vào primary selection/weights. Chưa đạt thì output unavailable. Robustness winsorize 1/99 + z-score là artifact riêng, chưa chạy để chọn primary.

## Interface và artifacts

CLI dự kiến: `uv run frl rank --config configs/research.toml --input-run <features_id>`.

Output: eligibility ledger (pass/fail từng filter và raw counts), ratio/axis/composite scores, industry_ranking, within_group_ranking và candidates Parquet; CSV readable cho mỗi cutoff; summary manifest và diagnostics. Mỗi tỷ lệ phải có mẫu số và scope, cả nhóm bị loại. Zero variance và low member counts là flags hiển thị, không che khỏi báo cáo.

Schema keys: cutoff/entity cho eligibility/composite, cutoff/entity/ratio cho normalized values, cutoff/industry cho ranking. Mỗi output gắn feature/config/approved-group version và parent run_id. Candidate order dùng score giảm rồi security_id tăng để trình bày; thứ tự này không được phá ties inclusion.

## Kiểm tra nghiệm thu

- Tập raw eligibility không phụ thuộc score; outliers/missing không tạo vòng lặp giữa filtering và normalization. Fixtures gồm 0/1/n members, ratio n=0/n=1 và toàn ties.
- Kiểm tra goodness direction, equal/reweight và hai mốc coverage 50%/3-of-4; compare hand-calculated score fixtures.
- 99 mã eligible lấy 99; ties vị trí 100 lấy >100; không rounded-score false ties. Một doanh nghiệp không xuất hiện hai lần.
- Median ngành không đổi khi chỉ thay số lượng candidate export; within-group score không thay primary lõi. Breadth và coverage đúng mẫu số.
- Hoán vị thứ tự input không đổi kết quả nghiệp vụ; thêm cột returns hoặc dữ liệu sau cutoff không tác động output. Stable output ordering/checksum với cùng pinned inputs.

Nếu eligibility/source gate chưa đạt thì xuất ledger và blockers, không tự hạ hard filters để đủ 100. Bàn giao candidates/scores/industry percentile inputs cho [stage 05](05-portfolio-backtest.md). Chưa khẳng định ranking có khả năng dự báo trước kiểm định ngoài mẫu.
