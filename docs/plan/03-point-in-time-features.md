# Stage 03 — Point-in-time snapshots và features

Trạng thái: chưa bắt đầu. Phụ thuộc: [stage 02](02-historical-data-universe.md), scope manifest đã audit. Quy tắc gốc: [dictionary/missing](../idea/02-universe-factors-ranking.md), [PIT](../idea/04-point-in-time-data.md).

## Mục tiêu và đầu vào

Dựng facts/ratios đúng những gì đã biết tại cutoff, tái lập mà không tải dữ liệu mới. Đầu vào gồm pinned raw filings, timestamp evidence, security/industry histories, prices/shares, approved groups và version dictionary. Tái sử dụng phần pilot đã kiểm chứng; chưa chuẩn hóa cross-section hoặc chọn top-100.

## Công việc

1. As-of join publication/availability ≤ cutoff UTC; date-only chỉ nhận ngày trước cutoff địa phương. Chọn version đúng accession/context, amendments chỉ hiệu lực từ publication; comparative fact mới công bố không được kéo về quá khứ.
2. Chuẩn hóa unit/currency/entity context và tag fallback đúng nghĩa. Facts thiếu/conflicting giữ reason và source candidates; không tự điền 0 cho debt/preferred. Lưu công thức và references tới mọi thành phần của fact derived.
3. Phân biệt instant/duration/fiscal/calendar; dựng Q2=YTD6−Q1, Q3=YTD9−YTD6, Q4=FY−YTD9 từ facts cùng basis. TTM 4 quý liên tiếp; YoY lag 4 quý; average A/E dùng hai đầu khoảng TTM. Fiscal change hoặc reconciliation không khớp là blocked/missing, không nội suy.
4. Tính 8 ratios lõi theo dictionary, mẫu số ≤ 0 missing; NI âm giữ khi tử số có ý nghĩa. Market cap dùng tổng common classes giá × shares instant đã công bố; không dùng weighted diluted shares hoặc một giá nhân tất cả classes.
5. Áp carry ≤ 2 quý từ first usable cutoff và period age ≤ 270 ngày, không reset age khi amendment. Với metric derived, kiểm tra tuổi theo endpoint mới nhất của metric, còn từng input lag/TTM phải tồn tại và hợp lệ tại publication tương ứng; không áp tuổi 270 ngày lên quý lag cố ý dùng cho YoY. Không đổi nhãn period khi carry growth.
6. Xuất raw coverage từng ratio/trục trước normalization; structural incompatibility chặn group, không đổi mẫu số để qua cổng. Mặc định trục ≥ 50% ratios và composite ≥ 3/4 trục; reweight chỉ ở aggregation stage sau.

## Interface và artifacts

CLI dự kiến: `uv run frl snapshots --config configs/research.toml --input-run <history_id>`, sau đó `uv run frl features --config configs/research.toml --input-run <snapshot_id>`.

Output: snapshot_facts, quarterly_facts, ttm_facts, raw_ratios, coverage và lineage Parquet; key snapshot gồm cutoff/entity/metric/version, input accession/context không được mất. Ratio output có value/status/reason, numerator/denominator refs, direction, period endpoint, first_usable_cutoff, staleness và factor version. Metadata không có price/return tương lai.

Schema validation cấm duplicate key, nonfinite ratios, mixed unit hoặc timezone-naive timestamp; quarantined facts và rejected facts xuất kèm. Snapshot publish chỉ khi integrity checks đạt; bad ratio có thể là missing đã giải thích, không tự là lỗi toàn pipeline nếu coverage vẫn hợp lệ.

## Kiểm tra nghiệm thu

- Golden fixtures: cùng ngày trước/sau 16:00, date-only, DST, amendment tương lai, cùng period nhiều accessions; thêm filing tương lai không đổi snapshot quá khứ.
- Quarterly/TTM cases: YTD, 53-week year hợp lệ theo fiscal periods, fiscal-year change, overlapping duration, thiếu quý, mismatch unit/context và stock không bị cộng 4 lần.
- Negative/zero denominator, loss numerator, missing debt/preferred, nhiều share classes và stale/late filing có expected outputs cụ thể.
- Đối chiếu lại toàn bộ manual pilot cases; derived ratio truy ngược raw từng input và khớp rounding tolerance nguồn. Báo metric nào còn unavailable, không chỉ điểm composite.
- Cùng input/config/version cho snapshot/ratios tương đương; đổi dictionary tạo version mới, không overwrite lịch sử.

Nếu ratio không có định nghĩa/mapping được chứng minh hoặc sai nghĩa giữa ngành, giữ unavailable/chặn nhóm và cập nhật idea trước đổi. [Stage 04](04-ranking-baseline.md) chỉ nhận features và coverage đã đóng version, không nhận provider data trực tiếp.
