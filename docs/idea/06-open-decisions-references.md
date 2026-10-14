# Quyết định mở và nguồn

## Cần chốt

| Vấn đề | Trạng thái |
|---|---|
| Thị trường và data provider | Mở |
| Universe, hard filters | Mở |
| Top-100 cố định hay số pass thay đổi | Mở |
| 100 ứng viên hay holdings cuối cùng | Mở |
| Hệ thống/cấp ngành | Mở |
| Ratios, missing, outliers, staleness | Mở |
| Score so ngành/chọn mã | Mở |
| Trọng số bốn trục | Equal-weight baseline đề xuất |
| Cutoff và execution | Hàng quý đã chốt; ngày cụ thể mở |
| Target horizon | Một quý đề xuất, chưa chốt |
| Benchmark, comparison portfolio | Mở |
| Weights, constraints, costs | Mở |
| Hypotheses, significance level, multiple testing | Mở |
| Research/validation/test dates | Mở |

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
