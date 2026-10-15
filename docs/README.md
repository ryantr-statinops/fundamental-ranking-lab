# Bản đồ tài liệu

`docs/` tách mục tiêu nghiên cứu, kế hoạch thực hiện, thiết kế kỹ thuật, bằng chứng và hướng dẫn sử dụng. Ngày tổ chức: 2026-10-16.

**Trạng thái hiện tại:** đã có research specification và kế hoạch stage 00–07. Chưa triển khai code, môi trường, pilot hoặc backtest. Các mục mới technical/research/guides hiện là trang định hướng và backlog tài liệu, chưa xác nhận hệ thống đã được xây hoặc kiểm chứng.

## Các nhóm tài liệu

| Nhóm | Câu hỏi được trả lời | Nguồn nội dung |
|---|---|---|
| [idea](idea/README.md) | Nghiên cứu gì, giả thuyết nào, dùng quy tắc nào? | Research specification, giả định và quyết định nghiên cứu |
| [plan](plan/README.md) | Làm theo thứ tự nào và nghiệm thu ra sao? | Công việc dự kiến, phụ thuộc, đầu vào/đầu ra và cổng triển khai |
| [technical](technical/README.md) | Hệ thống được thiết kế và hiện thực như thế nào? | Kiến trúc, data contracts, lineage, config/CLI và quyết định kỹ thuật |
| [research](research/README.md) | Đã kiểm chứng được gì, bằng chứng và giới hạn ở đâu? | Đánh giá nguồn, pilot, đối chiếu, study manifest và kết luận thí nghiệm |
| [guides](guides/README.md) | Người dùng cài đặt, chạy và xử lý lỗi như thế nào? | Hướng dẫn đã thực hành với code/config và fixtures cụ thể |

## Thứ tự đọc

1. Đọc [README dự án](../README.md) để nắm mục tiêu và trạng thái.
2. Đọc [idea](idea/README.md), rồi tra [sổ quyết định](idea/06-open-decisions-references.md) và [tham số](idea/07-spec-parameters.md) khi cần chi tiết.
3. Chọn stage tiếp theo từ [plan](plan/README.md); hiện bắt đầu ở [stage 00](plan/00-technical-foundation.md).
4. Khi triển khai, cập nhật technical và guides cùng code; khi có dữ liệu/thí nghiệm, cập nhật research cùng bằng chứng.

[Kế hoạch bàn giao tài liệu](plan/documentation-delivery.md) chỉ rõ từng file sẽ được tạo ở stage nào, nội dung cần có và tiêu chí hoàn thành. Đây là công việc xuyên suốt stage 00–07, không phải stage mới sau vận hành.

## Quy tắc phân loại và cập nhật

- Công thức/scoring, universe, portfolio hoặc giả thuyết đổi: cập nhật idea, sổ quyết định và tham số; plan/code phải phản ánh thay đổi đó.
- Cách thực thi hoặc acceptance đổi: cập nhật plan; khi đã triển khai thì cập nhật technical tương ứng, không coi kế hoạch là bằng chứng implementation.
- Thêm schema, config field hoặc command: cập nhật code/tests, technical reference và guide liên quan trong cùng đợt công việc.
- Có phát hiện thực nghiệm: ghi research cùng run_id, versions, nguồn và giới hạn; không sửa giả thuyết ban đầu để khớp kết quả.
- Lệnh chưa có chỉ xuất hiện với nhãn dự kiến trong plan. Guides chỉ hướng dẫn các command đã tồn tại và được kiểm tra, ghi rõ môi trường và ngày/commit kiểm tra.

File config chạy thật nằm ở `configs/` root khi được triển khai; tài liệu giải thích config ở technical/guides. Raw data, bảng lớn, logs, charts và báo cáo tự sinh nằm trong `data/` hoặc `artifacts/`, không chép toàn bộ vào docs. Research giữ phần diễn giải và artifact references có checksum; đường dẫn local không được mô tả như artifact công khai truy cập được từ GitHub.

Không tạo hàng loạt file trống hoặc đánh dấu hoàn tất chỉ vì có Markdown. Các README nhóm theo dõi tài liệu dự kiến bằng tên file dạng code; chỉ chuyển thành link khi file thực sự tồn tại.
