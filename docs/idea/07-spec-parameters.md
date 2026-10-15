# Bảng tham số tổng hợp

Gom toàn bộ tham số đã chốt của v1 để tra cứu một chỗ. Giá trị là v1 default, xem lại khi có dữ liệu; chi tiết và lý do ở các file [01](01-concept.md)–[06](06-open-decisions-references.md).

## Thị trường và nguồn

| Tham số | Giá trị |
|---|---|
| Thị trường | Cổ phiếu Mỹ |
| Tiền tệ | USD |
| Fundamentals | SEC EDGAR, as-filed XBRL (companyfacts/submissions) |
| Giá | yfinance (chính), Stooq (dự phòng) |
| Ngành | SEC SIC → Ken French 17 ngành |
| Factor/benchmark | Ken French Data Library |
| Chi phí dữ liệu | Miễn phí |

## Universe và hard filters

| Tham số | Giá trị |
|---|---|
| Lịch sử tối thiểu | ≥ 8 quý báo cáo |
| Dữ liệu đầy đủ | đủ score so ngành, ≥ 3/4 trục |
| Thanh khoản | ADV 20 ngày ≥ 1 triệu USD |
| Niêm yết | còn giao dịch tại cutoff |
| Khả năng đầu tư | giá ≥ 1 USD; NYSE/NASDAQ/AMEX |
| Ngành | Ken French 17; một hệ thống, một cấp; nhãn chính |

## Bốn trục và ratios

| Tham số | Giá trị |
|---|---|
| Trục | Quality, Growth, Financial Health, Valuation |
| Cấu trúc mỗi trục | level (TTM 4 quý) + change (YoY), 50/50 |
| General (15 ngành) | 4 ratio/trục |
| Finan | sub-block ngân hàng (SIC 60xx) / bảo hiểm (63xx) / REIT (65xx, 6798) |
| Utils | bộ ratio riêng |
| FFO (REIT) | xấp xỉ Net Income + depreciation − gains |
| Nguồn tính | tự tính từ EDGAR XBRL |

## Chuẩn hóa, missing, độ phủ

| Tham số | Giá trị |
|---|---|
| Chuẩn hóa chính | percentile rank cross-section tại cutoff |
| Kiểm tra độ bền | winsorize 1/99 + z-score |
| Missing structural | lõi chung + block ngành; reweight |
| Missing temporal | carry-forward ≤ 2 quý rồi bỏ + reweight; không impute |
| Mẫu số âm/zero | không xác định |
| Độ phủ trục | ≥ 50% ratio áp dụng |
| Độ phủ score | ≥ 3/4 trục |
| Ngưỡng chất lượng (breadth) | composite score ≥ phân vị 50 universe |
| Trọng số | equal-weight trong trục và giữa bốn trục |

## Ranking

| Tham số | Giá trị |
|---|---|
| Hai score | score so ngành (toàn universe) và score trong ngành |
| Score so ngành dùng cho | rank ngành + chọn top-100 |
| Score trong ngành dùng cho | rank mã trong ngành |
| Score ngành | median member, equal-weight |
| Candidate pool | top-100 theo score so ngành, lấy hết ties |
| Universe < 100 | lấy hết, số lượng biến động |

## Portfolio

| Tham số | Giá trị |
|---|---|
| Holdings | 30/50/100 (cấu hình) |
| Chọn holdings | subset của candidate pool |
| Tilt ngành | hệ số theo rank ngành; λ ∈ [0, 1], mặc định 0.5; + trần ngành |
| Trọng số mặc định | score-weight (biến thể cap-weight) |
| Trần mã | 10% |
| Trần ngành | 25% |
| No-trade band | 1% |
| Chi phí | commission 0.5 bps; spread = nửa bid-ask; impact = hệ số × sqrt(participation) |
| Delisting return | −100% khi thiếu giá |

## Kiểm định

| Tham số | Giá trị |
|---|---|
| Horizon | 1 quý |
| Q1 (chính) | Fama–MacBeth slope; bổ trợ Rank IC, sign test, monotonicity, spread |
| Q2/Q3 | trung bình spread/excess theo thời gian |
| HAC | Newey–West, auto lags |
| Bootstrap | block 4 quý, 5000 lần lặp |
| Kiểm định | một phía |
| α | 0.05 |
| Multiple testing | Benjamini–Hochberg, một family toàn study |
| Baseline chính | universe equal-weight |
| Baseline khác | cùng ngành/giới hạn rủi ro; ngẫu nhiên cùng cỡ |
| Comparison phụ | tercile bottom cùng ngành, cap-weight |

## Thời gian

| Tham số | Giá trị |
|---|---|
| Cadence | hàng quý |
| Cutoff | ngày giao dịch cuối quý, 16:00 ET |
| Execution | mở phiên giao dịch kế tiếp |
| Sample | 2010Q1–2025Q4 |
| Research | 2010–2019 |
| Validation | 2020–2022 |
| Test | 2023–2025 |
| Embargo | 1 quý ở ranh giới split |

## Ghi chú

Giá trị là v1 default. Thay đổi phải cập nhật file nguồn ([01](01-concept.md)–[06](06-open-decisions-references.md)) và bảng trạng thái ở [06](06-open-decisions-references.md). Bộ tài liệu là research specification, không phải cam kết performance.
