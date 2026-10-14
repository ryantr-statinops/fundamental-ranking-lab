# Concept và output

## Research question

Fundamental score có giúp nhận diện ngành và cổ phiếu hấp dẫn, đồng thời tạo danh mục tốt hơn phương pháp đối chiếu xác định trước không?

## Pipeline đề xuất

1. Universe tại từng thời điểm.
2. Lọc điều kiện dữ liệu và khả năng đầu tư.
3. Đo Quality, Growth, Financial Health, Valuation.
4. Tổng hợp và ranking ngành.
5. Chọn khoảng 100 ứng viên và ranking mã trong ngành.
6. Tạo danh mục theo quy tắc tỷ trọng.
7. Backtest ngoài mẫu và statistical inference.

Thứ tự chọn 100 mã và đánh giá ngành cần chốt theo phạm vi đại diện mong muốn.

## Output mỗi quý

- Ranking ngành: điểm từng trục, điểm tổng hợp, thay đổi hạng, độ phủ dữ liệu.
- Khoảng 100 ứng viên: ngành, factor scores, thứ hạng, lý do chọn/loại.
- Danh mục: holdings và tỷ trọng nếu đã chốt quy tắc construction.
- Báo cáo lịch sử: ranking metrics, performance, risk, chi phí và độ bất định.

“Tiềm năng” ở v1 nghĩa là hấp dẫn theo fundamentals tại thời điểm đánh giá. Khả năng sinh lời tương lai là giả thuyết cần kiểm chứng.

## Phân ngành

Dùng nhãn ngành có sẵn; cần chốt hệ thống, cấp phân ngành và cách xử lý doanh nghiệp đa ngành. Classification ML chỉ cần khi muốn dự đoán nhãn còn thiếu. Clustering tìm nhóm theo dữ liệu, không nhất thiết trùng ngành, là hướng mở rộng. Kiểm định không phải phương pháp phân cụm.

## Vai trò model

- Factor ranking: công thức/trọng số do nhà nghiên cứu định nghĩa.
- ML ranking: học kết hợp features để xếp hạng theo target tương lai.
- ML reranking: đánh giá lại tập ứng viên hoặc ranking ban đầu.

Lọc 100 mã chưa tự tạo thành reranking. Cross-encoder văn bản không phải lựa chọn mặc định cho features số.

Chọn mã theo năm/chu kỳ dài, clustering động và news-aware ranking được tạm hoãn.
