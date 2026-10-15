# Quyết định mở và nguồn

## Cần chốt

| Vấn đề | Trạng thái |
|---|---|
| Thị trường và data provider | Đã chốt: Mỹ; fundamentals SEC EDGAR (as-filed), giá yfinance/Stooq, ngành SEC SIC/Ken French, factor Ken French (free) |
| Universe, hard filters (ngưỡng) | Loại filter đã chốt; ngưỡng mở |
| Chọn ~100 mã | Đã chốt: top-100 theo score so ngành, lấy hết ties |
| 100 ứng viên hay holdings cuối cùng | Đã chốt: candidate pool ~100; holdings 30/50/100 |
| Hệ thống/cấp ngành | Đã chốt: Ken French 17 ngành; nhãn chính |
| Missing, outliers, chuẩn hóa | Đã chốt: percentile rank chính; missing lõi chung + block ngành; carry-forward ≤ 2 quý; độ phủ 50%/3-of-4 |
| Ratios cụ thể | Đã chốt: 4 ratio/trục general; Finan tách sub-block (bank/insurance/REIT); Utils riêng |
| Score so ngành/chọn mã | Đã chốt: hai score tách biệt |
| Trọng số bốn trục | Đã chốt: equal-weight cả hai cấp |
| Cutoff và execution | Hàng quý đã chốt; ngày cụ thể mở |
| Delisting return | Đã chốt: −100% khi thiếu giá |
| Target horizon | Một quý (đề xuất) |
| Benchmark, comparison portfolio | Benchmark chính đã chốt (universe equal-weight); comparison portfolio phụ mở |
| Weights, constraints, costs | Đã chốt: score-weight mặc định + cap-weight; trần mã 10% / ngành 25%; no-trade band 1%; component cost |
| Hypotheses, significance level, multiple testing | Đã chốt: một phía, α = 0.05, BH một family toàn study |
| Research/validation/test dates | Cấu trúc đã chốt (60/20/20, embargo 1 quý); ngày cụ thể mở |

## Nguồn đã tham khảo

- [Sentence Transformers retrieve/rerank](https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html): reranking văn bản.
- [LightGBM parameters](https://lightgbm.readthedocs.io/en/latest/Parameters.html): LambdaRank và label_gain.
- [Statsmodels HAC source](https://github.com/statsmodels/statsmodels/blob/main/statsmodels/stats/sandwich_covariance.py): Newey–West.
- [Statsmodels multipletests](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html): multiple-testing correction.
- [SEC as-filed datasets](https://www.sec.gov/dera/data/fsds.pdf): lịch sử filings và amendments.
- [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces): submissions/XBRL cho thị trường Mỹ.

Các nguồn giải thích công cụ/dữ liệu, không chứng minh factors tạo alpha. SEC chỉ phù hợp nếu chọn thị trường Mỹ. Inference cụ thể cần xác nhận theo dữ liệu và cấu trúc phụ thuộc.

## Chỉnh sửa tiếp

Cập nhật quyết định vào file tương ứng và bảng trạng thái, lưu lý do. Không biến đề xuất thành quyết định đã chốt. Bộ tài liệu là nền tảng research specification, không phải cam kết performance.
