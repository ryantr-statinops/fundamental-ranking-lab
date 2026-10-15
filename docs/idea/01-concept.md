# Concept và output

## Research question

Fundamental score có giúp nhận diện cổ phiếu/ngành hấp dẫn và tạo danh mục tốt hơn baseline định trước không? “Tiềm năng” là hấp dẫn theo fundamentals đã biết, không phải cam kết return tương lai.

| Câu hỏi | Phạm vi | Đại lượng chính |
|---|---|---|
| Q1 | Score cao có liên hệ return quý tới tốt hơn sau kiểm soát ngành? | Fama–MacBeth slope |
| Q2 | Ngành điểm cao có outperform ngành điểm thấp? | Top-minus-bottom tercile return |
| Q3 | Danh mục có tạo giá trị sau chi phí? | Net return trừ universe equal-weight |

Horizon một quý; [03](03-hypothesis-validation.md) quy định kiểm định và đối chiếu.

## Phạm vi và trạng thái

V1 gồm factor ranking, ranking ngành/mã, portfolio, backtest ngoài mẫu và statistical inference. Thiết kế nghiên cứu đã xác định; triển khai theo cổng kiểm chứng dữ liệu. Chưa có pipeline, model triển khai hoặc kết quả backtest.

Giữ thị trường Mỹ, USD, ngân sách dữ liệu bằng 0. SEC EDGAR là nguồn fundamentals; yfinance/Stooq là nguồn giá dự kiến. Không tuyên bố lịch sử không có survivorship bias trước audit. Ngành dùng SIC tại thời điểm đánh giá ánh xạ Ken French 17; doanh nghiệp đa ngành dùng nhãn chính.

Bank, insurance, REIT và Other Financials chỉ vào kết quả chính sau khi vượt cổng riêng về định nghĩa, tính tương đương của lõi chung và độ phủ dữ liệu. Kết quả phải ghi chính xác các ngành được bao phủ; không diễn giải universe bị giới hạn như toàn thị trường.

Hoãn ML ranking/reranking, news, clustering động, horizon khác, no-trade band và mô hình market impact. Factor ranking là model công thức của v1; lọc top-100 không tự tạo thành reranking.

## Hai vai trò score

- **Score lõi chung:** cùng định nghĩa và chiều kinh tế giữa các nhóm đã đạt cổng; chuẩn hóa toàn universe đủ điều kiện. Dùng so ngành, chọn top-100 và tính trọng số.
- **Score đặc thù:** ratios có ý nghĩa trong từng nhóm; chuẩn hóa trong nhóm để ranking/giải thích. Không trộn vào score lõi chung hoặc so trực tiếp composite khác nghĩa giữa các ngành.

## Pipeline và output

1. Dựng universe lịch sử, phân ngành và identity theo thời gian; xác minh cổng dữ liệu.
2. Tính raw ratios và độ phủ; lọc eligibility trước khi chuẩn hóa.
3. Tính Quality, Growth, Financial Health, Valuation và hai loại score.
4. Rank ngành bằng median score lõi chung trên toàn eligible universe, độc lập candidate pool.
5. Chọn top-100 lõi chung, lấy hết ties; dưới 100 mã thì lấy hết.
6. Nắm candidate pool theo score-weight + tilt ngành, áp caps và giữ tiền mặt dư.
7. Đánh giá ngoài mẫu, chi phí và độ bất định sau các cổng kiểm chứng.

Mỗi quý xuất ranking ngành, scores/trục, thay đổi hạng và độ phủ; candidate pool với lý do chọn/loại; holdings và tiền mặt; tỷ trọng trước/sau caps và chi phí. Báo cáo lịch sử gồm ranking metrics, performance, concentration, các vấn đề dữ liệu và giới hạn kết luận.

## Glossary và tiêu chí thành công

- **Eligible universe:** qua hard filters, cổng nhóm và độ phủ raw ratios trước chuẩn hóa.
- **Candidate pool:** top-100 lõi chung, gồm ties; là tập mục tiêu nắm giữ của v1, không có tầng chọn 30/50 mã.
- **Holdings:** mã có tỷ trọng thực sự dương sau construction; có thể ít hơn candidate pool nếu score bằng 0 hoặc chưa thể giao dịch, phải báo cáo rõ.
- **Tiền mặt:** phần NAV chưa phân bổ; luôn nằm trong accounting và performance.

Nghiên cứu hoàn thành khi pipeline tái lập và trả lời Q1–Q3 với độ bất định, kể cả kết quả âm hoặc chưa đủ bằng chứng. Quyết định sử dụng vốn thực là bước riêng. Factors ở [02](02-universe-factors-ranking.md), dữ liệu ở [04](04-point-in-time-data.md), portfolio/cổng triển khai ở [05](05-portfolio-roadmap.md).
