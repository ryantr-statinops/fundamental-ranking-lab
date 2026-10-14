# Hypothesis testing và đánh giá

## Vai trò

Kiểm định đánh giá bằng chứng lịch sử, không xác nhận cổ phiếu chắc chắn tăng. Phân biệt return dương, outperform benchmark và giá trị gia tăng của phương pháp chọn mã.

## Đối tượng kiểm định

| Đối tượng | Câu hỏi | Đại lượng |
|---|---|---|
| Factor score | Score cao liên hệ kết quả tương lai tốt hơn? | Rank IC mỗi quý |
| Ranking ngành | Ngành top outperform nhóm đối chiếu? | Top-minus-comparison return |
| Portfolio | Phương pháp tạo giá trị sau chi phí? | Net return trừ benchmark |

Ưu tiên kiểm định phương pháp qua nhiều kỳ, không chọn từng mã chỉ vì p-value thấp.

## Giả thuyết chính đề xuất

Các mã score cao có kết quả tương lai tốt hơn nhóm đối chiếu sau khi xét ảnh hưởng ngành.

`D_t = return nhóm score cao kỳ tiếp theo − return nhóm đối chiếu cùng kỳ`

- H0: E[D_t] ≤ 0.
- H1: E[D_t] > 0.

Nhóm đối chiếu có thể là nhóm score thấp trong cùng ngành. Spread portfolio là công cụ nghiên cứu, không bắt buộc giao dịch short. Chốt nhóm, trọng số và horizon trước đánh giá.

Giả thuyết ngành kiểm định riêng: ngành score cao outperform ngành score thấp. Tách hiệu quả chọn ngành và chọn mã trong ngành. Excess return đơn giản không tự đồng nghĩa risk-adjusted alpha; alpha regression cần factor model riêng.

## Phương pháp đề xuất

- Báo cáo effect size, confidence interval và số kỳ.
- Kiểm định trung bình bằng intercept regression với HAC/Newey–West khi phù hợp; chốt lags và kiểm định một phía.
- Block bootstrap theo thời gian để kiểm tra độ bền; chốt block length và repetitions.
- Không xem 100 mã cùng quý là 100 quan sát độc lập. Baseline là chuỗi kết quả danh mục theo quý.
- Nhiều factors/ngành/horizons cần định nghĩa family of tests và multiple-testing correction phù hợp. BH có điều kiện về phụ thuộc; không áp máy móc.

Ranking ngành hiện tại dựa score. Inference xác thực hiệu quả lịch sử; không xếp hạng bằng p-value vì p-value phụ thuộc variance và sample size.

## Thiết kế ngoài mẫu

Chia theo thời gian; khóa factors, trọng số, horizon, portfolio trước final test. Purge các labels tương lai chồng lấn ranh giới split. Không chọn cấu hình bằng kết quả final test.

Baselines đề xuất: universe equal-weight, score đơn giản, danh mục cùng ngành/giới hạn rủi ro. Chốt baseline chính trước nghiên cứu.

## Metrics

- Ranking: Spearman Rank IC theo quý, score buckets, stability; NDCG tùy chọn nếu định nghĩa relevance labels.
- Portfolio: net/excess return, Sharpe, maximum drawdown, turnover, liquidity, concentration.
- Inference: effect size, confidence interval, p-value, số quan sát.

10 năm có khoảng 40 kỳ quý. Nhiều mã không tự bù số kỳ thời gian thấp. Daily returns của portfolio quarterly có thể phục vụ đánh giá nhưng vẫn phụ thuộc theo thời gian.

P-value nhỏ không đảm bảo hiệu quả tương lai. Không bác bỏ H0 không chứng minh phương pháp vô dụng. Statistical significance không thay thế hiệu quả kinh tế sau chi phí. Kết quả âm vẫn là kết quả nghiên cứu hợp lệ.
