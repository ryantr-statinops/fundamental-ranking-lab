# Quyết định và nguồn

## Trạng thái quyết định

| Vấn đề | Trạng thái |
|---|---|
| Thị trường và data provider | Đã chốt: Mỹ; fundamentals SEC EDGAR (as-filed), giá yfinance/Stooq, ngành SEC SIC/Ken French, factor Ken French (free) |
| Universe, hard filters (ngưỡng) | Đã chốt: ≥ 8 quý lịch sử; ADV 20 ngày ≥ $1M; giá ≥ $1; NYSE/NASDAQ/AMEX; đủ ≥ 3/4 trục (v1 default) |
| Chọn ~100 mã | Đã chốt: top-100 theo score so ngành, lấy hết ties |
| 100 ứng viên hay holdings cuối cùng | Đã chốt: candidate pool ~100; holdings 30/50/100 |
| Hệ thống/cấp ngành | Đã chốt: Ken French 17 ngành; nhãn chính |
| Missing, outliers, chuẩn hóa | Đã chốt: percentile rank chính; missing lõi chung + block ngành; carry-forward ≤ 2 quý; độ phủ 50%/3-of-4 |
| Ngưỡng chất lượng (breadth) | Đã chốt: composite score ≥ phân vị 50 universe |
| Ratios cụ thể | Đã chốt: 4 ratio/trục general; Finan tách sub-block (bank/insurance/REIT); Utils riêng |
| Score so ngành/chọn mã | Đã chốt: hai score tách biệt |
| Trọng số bốn trục | Đã chốt: equal-weight cả hai cấp |
| Cutoff và execution | Đã chốt: cutoff ngày giao dịch cuối quý 16:00 ET; execution mở phiên kế tiếp |
| Delisting return | Đã chốt: −100% khi thiếu giá |
| Target horizon | Đã chốt: một quý |
| Benchmark, comparison portfolio | Đã chốt: benchmark chính universe equal-weight; comparison phụ nhóm score thấp cùng ngành (tercile bottom), cap-weight |
| Weights, constraints, costs | Đã chốt: score-weight mặc định + cap-weight; trần mã 10% / ngành 25%; no-trade band 1%; component cost |
| Hypotheses, significance level, multiple testing | Đã chốt: một phía, α = 0.05, BH một family toàn study |
| Research/validation/test dates | Đã chốt: sample 2010Q1–2025Q4; research 2010–2019, validation 2020–2022, test 2023–2025; embargo 1 quý |

## Nguồn đã tham khảo

- [Sentence Transformers retrieve/rerank](https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html): reranking văn bản.
- [LightGBM parameters](https://lightgbm.readthedocs.io/en/latest/Parameters.html): LambdaRank và label_gain.
- [Statsmodels HAC source](https://github.com/statsmodels/statsmodels/blob/main/statsmodels/stats/sandwich_covariance.py): Newey–West.
- [Statsmodels multipletests](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html): multiple-testing correction.
- [SEC as-filed datasets](https://www.sec.gov/dera/data/fsds.pdf): lịch sử filings và amendments.
- [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces): submissions/XBRL cho thị trường Mỹ.
- [Ken French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html): factors, benchmark và 17 industry portfolios.
- [yfinance](https://github.com/ranaroussi/yfinance): giá miễn phí; [Stooq](https://stooq.com/) làm nguồn dự phòng.

Các nguồn giải thích công cụ/dữ liệu, không chứng minh factors tạo alpha. SEC chỉ phù hợp nếu chọn thị trường Mỹ. Inference cụ thể cần xác nhận theo dữ liệu và cấu trúc phụ thuộc.

## Chỉnh sửa tiếp

Cập nhật quyết định vào file tương ứng và bảng trạng thái, lưu lý do. Không biến đề xuất thành quyết định đã chốt. Bộ tài liệu là nền tảng research specification, không phải cam kết performance.
