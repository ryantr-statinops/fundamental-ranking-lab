# Fundamental Ranking Lab

Nghiên cứu định lượng về việc sử dụng dữ liệu tài chính doanh nghiệp để xếp hạng cổ phiếu và ngành tại thị trường Mỹ, xây dựng danh mục cập nhật hàng quý và kiểm chứng hiệu quả ngoài mẫu sau chi phí.

**Trạng thái: thiết kế nghiên cứu đã xác định; bước tiếp theo là kiểm chứng dữ liệu.** Repository hiện chứa tài liệu nghiên cứu. Chưa triển khai pipeline, chưa thực hiện pilot hoặc backtest và chưa có kết quả performance. Tên dự án là tên tạm thời.

## Mục tiêu nghiên cứu

Doanh nghiệp có fundamentals tốt chưa chắc tạo ra khoản đầu tư hấp dẫn ở mọi mức giá. Fundamental Ranking Lab kết hợp chất lượng, tăng trưởng, sức khỏe tài chính và định giá để kiểm tra ba câu hỏi:

| Câu hỏi | Nội dung | Cách đánh giá chính |
|---|---|---|
| Q1 — Cổ phiếu | Score cao có liên hệ với lợi nhuận quý tiếp theo tốt hơn sau khi kiểm soát ngành? | Hệ số Fama–MacBeth |
| Q2 — Ngành | Ngành được xếp hạng cao có vượt nhóm ngành xếp hạng thấp? | Chênh lệch lợi nhuận nhóm trên và dưới |
| Q3 — Danh mục | Phương pháp có cải thiện kết quả sau chi phí so với danh mục tham chiếu? | Lợi nhuận ròng trừ universe equal-weight |

Nghiên cứu hướng tới một quy trình có thể tái lập, giải thích được cách chấm điểm và công bố độ bất định. Kết luận âm hoặc chưa đủ bằng chứng vẫn là kết quả nghiên cứu hợp lệ.

## Phạm vi v1

| Thành phần | Thiết kế hiện tại |
|---|---|
| Thị trường | Cổ phiếu phổ thông Mỹ trên NYSE/NASDAQ/AMEX; một share class mỗi doanh nghiệp |
| Ngành | SIC lịch sử ánh xạ sang Ken French 17 ngành |
| Chu kỳ | Đánh giá và tái cân bằng hàng quý; horizon một quý |
| Phương pháp | Factor ranking theo công thức; bốn trục Quality, Growth, Financial Health, Valuation |
| Chọn mã | Top-100 theo score lõi chung; lấy hết mã bằng điểm ở ranh giới, lấy hết nếu dưới 100 |
| Danh mục | Long-only, không leverage; score-weight kết hợp điều chỉnh tỷ trọng theo hạng ngành |
| Giới hạn mặc định | Tối đa 20% NAV mỗi ngành, 5% mỗi doanh nghiệp tại rebalance; phần dư giữ tiền mặt |
| Đối chiếu chính | Toàn bộ cổ phiếu đủ điều kiện, tỷ trọng bằng nhau, cùng lịch và chi phí |

Score **lõi chung** dùng để so ngành, chọn mã và tính tỷ trọng. Score **đặc thù** phục vụ xếp hạng và giải thích trong từng nhóm; chỉ sử dụng khi định nghĩa và dữ liệu đã được kiểm chứng. Bank, insurance, REIT và Other Financials phải vượt cổng kiểm tra riêng trước khi vào kết quả chính.

ML ranking/reranking, news, clustering động, mô hình market impact và triển khai giao dịch thực được để cho giai đoạn sau.

## Quy trình dự kiến

1. **Dựng universe lịch sử:** xác minh chứng khoán, trạng thái niêm yết, ngành và thay đổi identifier theo thời gian.
2. **Tạo snapshot point-in-time:** chỉ dùng thông tin đã công bố tại cutoff, giữ nguồn và phiên bản để truy nguyên.
3. **Lọc điều kiện:** kiểm tra thanh khoản, lịch sử báo cáo và độ phủ raw ratios trước chuẩn hóa.
4. **Chấm điểm và xếp hạng:** tính bốn trục, score lõi chung, ranking ngành và ranking trong nhóm.
5. **Xây dựng danh mục:** chọn khoảng 100 mã, tính trọng số, áp trần và giữ tiền mặt chưa phân bổ.
6. **Kiểm chứng ngoài mẫu:** so với baseline, phân tích chi phí, rủi ro, đóng góp của từng thành phần và độ bất định.

Cutoff là 16:00 `America/New_York` vào ngày giao dịch cuối quý; giao dịch mô phỏng tại mở phiên kế tiếp. Lịch sử mục tiêu gồm tín hiệu 2010Q1–2025Q4, với outcome cuối đến mở phiên quý II/2026. Phạm vi thực tế phải được xác nhận qua audit dữ liệu trước khi đánh giá performance.

## Đầu ra dự kiến

| Đầu ra | Nội dung |
|---|---|
| Ranking ngành mỗi quý | Điểm tổng hợp và từng trục, thay đổi hạng, độ phủ và quy mô ngành |
| Danh sách cổ phiếu | Candidate pool, scores, thứ hạng, lý do chọn/loại và cờ dữ liệu |
| Danh mục | Holdings, tỷ trọng trước/sau giới hạn, tiền mặt và chi phí |
| Báo cáo nghiên cứu | Ranking metrics, lợi nhuận gross/net, rủi ro, turnover, concentration, kiểm định và giới hạn kết luận |

Các đầu ra này là mục tiêu triển khai, chưa phải artifacts đã có trong repository.

## Dữ liệu và nguyên tắc kiểm chứng

Ngân sách dữ liệu v1 là **0 USD**. Nguồn dự kiến gồm SEC EDGAR as-filed cho fundamentals, yfinance/Stooq cho giá và SEC SIC/Ken French cho phân ngành; Ken French factors phục vụ phân tích bổ trợ. Chi tiết nguồn và tài liệu gốc nằm trong [quyết định và nguồn](docs/idea/06-open-decisions-references.md).

Các nguyên tắc chi phối nghiên cứu:

- **Dữ liệu đúng thời điểm:** không dùng filing hoặc bản sửa đổi chưa công bố tại cutoff; không ghi đè lịch sử bằng dữ liệu mới nhất.
- **Universe có bằng chứng lịch sử:** không dựng backtest chỉ từ các mã còn tồn tại hôm nay; chưa tuyên bố loại được survivorship bias trước audit.
- **Xử lý giá thiếu rõ nguyên nhân:** không mặc định mất giá 100%; sự kiện chưa xác minh có thể chặn kết luận performance chính.
- **Khóa thiết kế trước final test:** tách research, validation và test; không chọn cấu hình bằng kết quả test.
- **Báo cáo cả tiền mặt và chi phí:** tiền mặt nằm trong NAV; giả định chi phí và giới hạn tập trung phải được công bố.

Trần 20%/5% và các tham số khác là mặc định nghiên cứu, chưa được chứng minh tối ưu. Nguồn miễn phí có thể không đủ lịch sử, đặc biệt với mã hủy niêm yết và corporate actions; khi đó cần giới hạn phạm vi hoặc dừng ở kết luận về khả năng xây dựng dữ liệu.

## Lộ trình và bước tiếp theo

| Giai đoạn | Kết quả cần đạt | Trạng thái |
|---|---|---|
| Thiết kế nghiên cứu | Câu hỏi, quy tắc, tham số và tiêu chí kiểm chứng được ghi rõ | Đã ghi nhận; một số giả định chờ kiểm chứng |
| Pilot dữ liệu | 40 doanh nghiệp × 4 cutoff cuối năm 2012/2018/2022/2025; đối chiếu filing gốc ít nhất 10 doanh nghiệp | Tiếp theo |
| Audit universe | Xác minh membership, identity, ngành, giá và corporate actions trên sample | Chưa thực hiện |
| Pipeline và baseline | Tái lập snapshots, scores, ranking và danh mục | Chưa triển khai |
| Validation và final test | Báo cáo ngoài mẫu, độ bất định và kết luận Q1–Q3 | Chưa thực hiện |
| Mở rộng ML | Đánh giá giá trị tăng thêm so với factor baseline | Hoãn |

Pilot kiểm tra khả năng lấy và tính đúng dữ liệu; audit toàn universe là cổng riêng trước backtest chính. Tiêu chí qua từng cổng nằm trong [portfolio và lộ trình nghiên cứu](docs/idea/05-portfolio-roadmap.md).

## Bản đồ tài liệu

| Tài liệu | Đọc khi cần |
|---|---|
| [Tổng quan bộ idea](docs/idea/README.md) | Theo dõi các quyết định thiết kế chính |
| [Concept và output](docs/idea/01-concept.md) | Hiểu câu hỏi nghiên cứu, vai trò score và phạm vi v1 |
| [Universe, factors và ranking](docs/idea/02-universe-factors-ranking.md) | Tra eligibility, factor dictionary, missing và chuẩn hóa |
| [Hypothesis testing và đánh giá](docs/idea/03-hypothesis-validation.md) | Tra baseline, split thời gian, kiểm định và cách diễn giải |
| [Thông tin được phép dùng](docs/idea/04-point-in-time-data.md) | Tra timestamp, versioning, identity và corporate actions |
| [Portfolio và lộ trình](docs/idea/05-portfolio-roadmap.md) | Tra construction, accounting, chi phí, pilot và acceptance scenarios |
| [Quyết định và nguồn](docs/idea/06-open-decisions-references.md) | Phân biệt đã chốt, mặc định, chờ kiểm chứng và hoãn |
| [Bảng tham số tổng hợp](docs/idea/07-spec-parameters.md) | Tra nhanh giá trị và vị trí quy tắc gốc |

Hiện chưa có ứng dụng hoặc CLI để cài đặt/chạy. Hướng dẫn môi trường, lệnh tái lập và cấu trúc mã nguồn sẽ được bổ sung khi pipeline đầu tiên được triển khai. Khi thay đổi thiết kế, cập nhật tài liệu nguồn trong `docs/idea`, sổ quyết định và bảng tham số; README này giữ vai trò tổng quan.
