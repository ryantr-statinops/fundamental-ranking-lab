# Hypothesis testing và đánh giá

## Vai trò

Kiểm định đánh giá bằng chứng lịch sử, không xác nhận cổ phiếu chắc chắn tăng. Phân biệt return dương, outperform benchmark và giá trị gia tăng của phương pháp chọn mã.

## Đối tượng và giả thuyết

Ba câu hỏi con ở [01](01-concept.md); horizon một quý. Cả ba kiểm định một phía: H0 E[·] ≤ 0, H1 E[·] > 0.

| Đối tượng | Câu hỏi | Nhóm so sánh | Đại lượng |
|---|---|---|---|
| Q1 Factor score | Score cao liên hệ kết quả tương lai tốt hơn? | Tercile top vs bottom trong ngành, cap-weight | Fama–MacBeth slope; Rank IC |
| Q2 Ranking ngành | Ngành điểm cao outperform ngành điểm thấp? | Top vs bottom tercile ngành theo median | Top-minus-comparison return |
| Q3 Portfolio | Phương pháp tạo giá trị sau chi phí? | Net danh mục trừ universe equal-weight | Net excess return |

Q1: hệ số (slope) của score trong cross-sectional regression kỳ vọng dương. Q2 và Q3: trung bình spread/excess theo thời gian kỳ vọng dương.

Q1 chia tercile trong ngành, so top với bottom, cap-weight. Ngành nhỏ vẫn chia tercile, không gộp; chấp nhận nhiễu và ghi rõ trong báo cáo. Cap-weight nhóm so sánh có thể lệch theo size, cần lưu ý khi diễn giải.

Spread portfolio là công cụ nghiên cứu, không bắt buộc giao dịch short. Nhóm, trọng số và horizon chốt trước khi đánh giá.

## Phương pháp

**Q1 — chính: Fama–MacBeth.** Mỗi quý chạy cross-sectional regression forward return theo score (kèm industry), lấy trung bình hệ số theo thời gian và test bằng Newey–West. **Bổ trợ:** Rank IC mỗi quý; sign test tỷ lệ quý IC > 0; monotonicity giữa các bucket; portfolio spread để đo độ lớn kinh tế.

**Q2 và Q3 — trung bình theo thời gian.** Kiểm định trung bình spread/excess bằng HAC (Newey–West, auto lags) và block bootstrap theo thời gian (block 4 quý, 5000 lần lặp) để kiểm tra độ bền.

Không xem các mã cùng quý là quan sát độc lập; baseline là chuỗi kết quả danh mục theo quý.

Mức ý nghĩa α = 0.05, kiểm định một phía. Định nghĩa một family of tests cho toàn study (Q1/Q2/Q3 cùng các biến thể factor/ngành/horizon) và hiệu chỉnh Benjamini–Hochberg; báo cáo cả p-value raw và adjusted. BH có điều kiện về phụ thuộc, không áp máy móc.

Excess return đơn giản không tự đồng nghĩa risk-adjusted alpha; alpha regression cần factor model riêng. Ranking ngành dựa score; p-value không phải điểm hấp dẫn.

## Thiết kế ngoài mẫu

Chia theo thời gian: 60% research, 20% validation, 20% test. Embargo một quý ở ranh giới split để tránh chồng lấn label; horizon một quý và rebalance rời rạc nên yêu cầu nhẹ.

Khóa factors, trọng số, horizon và portfolio trước final test. Không chọn cấu hình bằng kết quả final test.

Baselines: universe equal-weight (chính), danh mục cùng ngành/giới hạn rủi ro, danh mục ngẫu nhiên cùng cỡ.

## Metrics

- Ranking: Spearman Rank IC theo quý, return theo score buckets, stability, monotonicity. NDCG tùy chọn nếu định nghĩa được relevance.
- Portfolio: net/excess return, Sharpe, maximum drawdown, turnover, liquidity, concentration, information ratio, hit rate, Calmar, profit factor (bổ trợ), CAGR (số tóm tắt mô tả).
- Inference: effect size, confidence interval, p-value raw và BH-adjusted, số quan sát.

## Diễn giải

10 năm có khoảng 40 kỳ quý. Nhiều mã không tự bù số kỳ thời gian thấp.

P-value nhỏ không đảm bảo hiệu quả tương lai. Không bác bỏ H0 không chứng minh phương pháp vô dụng. Statistical significance không thay thế hiệu quả kinh tế sau chi phí. CAGR chỉ là số tóm tắt, không dùng làm mục tiêu suy diễn. Kết quả âm vẫn là kết quả nghiên cứu hợp lệ.
