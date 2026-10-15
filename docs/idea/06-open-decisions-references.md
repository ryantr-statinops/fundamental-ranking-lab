# Quyết định mở và nguồn

## Cần chốt

| Vấn đề | Trạng thái |
|---|---|
| Thị trường và data provider | Mở |
| Universe, hard filters (ngưỡng) | Loại filter đã chốt; ngưỡng mở |
| Chọn ~100 mã | Đã chốt: top-100 theo score so ngành, lấy hết ties |
| 100 ứng viên hay holdings cuối cùng | Đã chốt: 100 mã là candidate pool; holdings theo 05 |
| Hệ thống/cấp ngành | Mở (v1: một hệ thống, một cấp, nhãn chính) |
| Missing, outliers, chuẩn hóa | Đã chốt: percentile rank chính; missing lõi chung + block ngành; carry-forward ≤ 2 quý; độ phủ 50%/3-of-4 |
| Ratios cụ thể | Mở |
| Score so ngành/chọn mã | Đã chốt: hai score tách biệt |
| Trọng số bốn trục | Đã chốt: equal-weight cả hai cấp |
| Cutoff và execution | Hàng quý đã chốt; ngày cụ thể mở |
| Target horizon | Một quý (đề xuất) |
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
