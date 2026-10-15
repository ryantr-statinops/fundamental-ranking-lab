# Concept và output

## Research question

Fundamental score có giúp nhận diện cổ phiếu và ngành hấp dẫn, đồng thời tạo danh mục tốt hơn baseline định trước không? Câu hỏi tách thành ba câu con, horizon một quý.

| Câu hỏi | Phạm vi | Đại lượng |
|---|---|---|
| Q1 | Score cao có dự báo return một quý tới tốt hơn nhóm đối chiếu cùng ngành? | Rank IC |
| Q2 | Ngành điểm cao có outperform ngành điểm thấp? Tính trên universe đủ điều kiện. | Top-minus-comparison return |
| Q3 | Danh mục có tạo giá trị sau chi phí so baseline? | Net/excess return |

Horizon một quý là mặc định đề xuất; các horizon khác và nhóm đối chiếu chi tiết chốt ở [03](03-hypothesis-validation.md).

“Tiềm năng” ở v1 nghĩa là hấp dẫn theo fundamentals tại thời điểm đánh giá. Khả năng sinh lời tương lai là giả thuyết cần kiểm chứng.

## Phạm vi v1

Trong phạm vi:

- Factor ranking: công thức/trọng số do nhà nghiên cứu định nghĩa.
- Ranking ngành và ranking mã trong ngành.
- Portfolio construction cùng holdings và tỷ trọng.
- Backtest ngoài mẫu và statistical inference.

Ngoài phạm vi (hoãn giai đoạn sau):

- ML ranking và ML reranking.
- News-aware ranking.
- Clustering động.
- Chọn mã theo năm/chu kỳ dài.
- Cross-encoder văn bản, không phải lựa chọn mặc định cho features số.

## Pipeline

1. Universe tại từng thời điểm.
2. Lọc điều kiện dữ liệu và khả năng đầu tư, tạo universe đủ điều kiện.
3. Đo Quality, Growth, Financial Health, Valuation và tổng hợp điểm.
4. Ranking ngành trên universe đủ điều kiện.
5. Chọn khoảng 100 ứng viên theo top-100 score và ranking mã trong ngành.
6. Tạo danh mục theo quy tắc tỷ trọng; ranking ngành có ảnh hưởng tới construction.
7. Backtest ngoài mẫu và statistical inference.

Thứ tự đã chốt: đánh giá ngành trên universe đủ điều kiện, tách khỏi tập ứng viên; chọn 100 mã bằng top-100 score. Quy tắc ties và trường hợp thiếu ứng viên ở [02](02-universe-factors-ranking.md); cơ chế ranking ngành ảnh hưởng portfolio ở [05](05-portfolio-roadmap.md).

## Output mỗi quý

- Ranking ngành: điểm từng trục, điểm tổng hợp, thay đổi hạng, độ phủ dữ liệu.
- Khoảng 100 ứng viên: ngành, factor scores, thứ hạng, lý do chọn/loại.
- Danh mục: holdings và tỷ trọng.
- Báo cáo lịch sử: ranking metrics, performance, risk, chi phí và độ bất định.

## Phân ngành

Dùng nhãn ngành có sẵn. v1 dùng một hệ thống phân ngành và một cấp; doanh nghiệp đa ngành xử lý theo quy tắc nhãn chính. Hệ thống, cấp phân ngành và quy tắc đa ngành cụ thể để mở, gắn với lựa chọn thị trường ở [06](06-open-decisions-references.md).

Classification ML chỉ cần khi muốn dự đoán nhãn còn thiếu. Clustering tìm nhóm theo dữ liệu, không nhất thiết trùng ngành, là hướng mở rộng. Kiểm định không phải phương pháp phân cụm.

## Vai trò model

- Factor ranking: công thức/trọng số do nhà nghiên cứu định nghĩa; là model của v1.
- ML ranking: học kết hợp features để xếp hạng theo target tương lai; giai đoạn sau.
- ML reranking: đánh giá lại tập ứng viên hoặc ranking ban đầu; giai đoạn sau.

Lọc 100 mã chưa tự tạo thành reranking.

## Glossary

- **Universe đủ điều kiện:** tập cổ phiếu vượt hard filters về dữ liệu và khả năng đầu tư tại thời điểm đánh giá.
- **Candidate pool:** khoảng 100 mã lấy từ top-100 score của universe đủ điều kiện; chưa phải holdings.
- **Nhóm đối chiếu:** nhóm so sánh xác định trước dùng để đo hiệu quả, ví dụ nhóm score thấp cùng ngành.
- **Holdings:** các mã và tỷ trọng thực sự nắm giữ trong danh mục.
- **Horizon:** khoảng thời gian đo return tương lai; mặc định một quý.
- **Tiềm năng:** hấp dẫn theo fundamentals tại thời điểm đánh giá, không phải dự báo lợi nhuận chắc chắn.
