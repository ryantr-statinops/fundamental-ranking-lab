# Bản đồ tài liệu

`docs/` tách mục tiêu nghiên cứu, kế hoạch thực hiện, thiết kế kỹ thuật, bằng chứng và hướng dẫn sử dụng. Ngày tổ chức: 2026-10-16.

**Trạng thái hiện tại:** research specification đã có; Stage 00 nền tảng đạt cổng. Stage 01 có CLI pilot và replay offline, nhưng lần chạy hiện tại bị chặn trước ingestion thật vì chưa cấu hình SEC contact và roster evidence còn là ứng viên. Không có snapshot thật hoặc performance result. Technical, research và guides phân biệt code đã chạy với cổng dữ liệu chưa đạt.

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
3. Chọn stage tiếp theo từ [plan](plan/README.md); Stage 00 đã đạt cổng, tiếp tục xử lý blockers ở [stage 01](plan/01-data-feasibility-pilot.md).
4. Khi triển khai, cập nhật technical và guides cùng code; khi có dữ liệu/thí nghiệm, cập nhật research cùng bằng chứng.

[Kế hoạch bàn giao tài liệu](plan/documentation-delivery.md) chỉ rõ từng file sẽ được tạo ở stage nào, nội dung cần có và tiêu chí hoàn thành. Đây là công việc xuyên suốt stage 00–07, không phải stage mới sau vận hành.

## Quy tắc phân loại và cập nhật

- Công thức/scoring, universe, portfolio hoặc giả thuyết đổi: cập nhật idea, sổ quyết định và tham số; plan/code phải phản ánh thay đổi đó.
- Cách thực thi hoặc acceptance đổi: cập nhật plan; khi đã triển khai thì cập nhật technical tương ứng, không coi kế hoạch là bằng chứng implementation.
- Thêm schema, config field hoặc command: cập nhật code/tests, technical reference và guide liên quan trong cùng đợt công việc.
- Có phát hiện thực nghiệm: ghi research cùng run_id, versions, nguồn và giới hạn; không sửa giả thuyết ban đầu để khớp kết quả.
- Lệnh chưa có chỉ xuất hiện với nhãn dự kiến trong plan. Guides chỉ hướng dẫn command đã tồn tại và ghi rõ môi trường, blockers và mức kiểm tra.

File config chạy thật nằm ở `configs/` root khi được triển khai; tài liệu giải thích config ở technical/guides. Raw data, bảng lớn, logs, charts và báo cáo tự sinh nằm trong `data/` hoặc `artifacts/`, không chép toàn bộ vào docs. Research giữ phần diễn giải và artifact references có checksum; đường dẫn local không được mô tả như artifact công khai truy cập được từ GitHub.

Không tạo hàng loạt file trống hoặc đánh dấu hoàn tất chỉ vì có Markdown. Mỗi README nhóm phân biệt trang dự kiến với bằng chứng/artifact đã tồn tại.
