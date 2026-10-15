# Tài liệu kỹ thuật

Mục này mô tả thiết kế kỹ thuật và hệ thống thực tế khi được triển khai. Hiện chỉ có kế hoạch; chưa có package Python, schema code hoặc CLI. Stack được chọn xem ở [stage 00](../plan/00-technical-foundation.md), công thức nghiên cứu nằm trong [idea](../idea/README.md).

## Kế hoạch nội dung

Tên file dưới đây là dự kiến, chưa phải tài liệu đã tồn tại. Tiêu chí chi tiết nằm trong [kế hoạch bàn giao](../plan/documentation-delivery.md).

| File dự kiến | Nội dung | Bắt đầu / hoàn thiện |
|---|---|---|
| `architecture.md` | Module boundaries, data flow, provider adapters, storage, offline transforms và CLI | Stage 00; cập nhật stage 01–07 |
| `data-contracts.md` | Tables/columns/types/keys, null/reason codes, timestamps, versions và input/output invariants | Stage 00; mở rộng theo output mỗi stage |
| `configuration-and-cli.md` | Config schema, defaults/required fields, validation, env, command options/exit codes và hash semantics | Stage 00; thêm command khi đã triển khai |
| `data-lineage-and-versioning.md` | Raw hashes, as-of joins, amendments, lineage, manifests, revisions và schema evolution | Stage 00; kiểm chứng stage 01–03 |
| `decisions.md` | Quyết định kỹ thuật: bối cảnh, lựa chọn, đánh đổi, trạng thái và điều kiện thay thế | Stage 00; cập nhật khi thay đổi kiến trúc |

## Ranh giới nội dung

Technical giải thích contract và hành vi; [guides](../guides/README.md) giải thích người dùng thực hiện tác vụ. Configuration reference không chứa credentials hoặc đường dẫn riêng của máy; config thật ở `configs/` khi code có sẵn. Quyết định kỹ thuật không thay sổ quyết định nghiên cứu trong idea.

Mỗi trang kỹ thuật phân biệt **thiết kế đã chọn**, **đã triển khai** và **đã kiểm chứng**. Ghi module/schema/config version, commit liên quan và test evidence. Ví dụ dự kiến phải mang nhãn dự kiến; chưa có code thì không gắn link tới đường dẫn source giả.

## Những contract phải chốt ở stage 00

- Data tables: primary/natural keys, cardinality, nullability, units/currency, timestamp timezone, status/reason enums và ví dụ hợp lệ/không hợp lệ. Không chỉ liệt kê tên bảng.
- Temporal model: tách effective time, public availability và ingestion time. Interval không overlap được kiểm tra trong cùng business key và cùng revision/as-of view; các revisions bất biến có thể sửa một khoảng hiệu lực cũ mà không bị xóa.
- Config hashes: research hash chỉ chứa tham số ảnh hưởng nghiên cứu; execution hash chứa cấu hình vận hành đã loại private contact/secret. Output run identity pin input hashes, research hash, code/lock/schema/factor versions; đổi đường dẫn local hoặc contact SEC không tạo nghiên cứu mới.
- Tái lập: logical-content checksum khác file-byte checksum; record ordering/numeric serialization cần xác định. Manifest/log metadata biến động không làm bảng giống nhau bị coi khác về nghiệp vụ.

## Điều kiện hoàn thành

Các contracts đối chiếu được với validators/tests thực, sơ đồ module khớp source và command reference khớp `--help`. Mọi thay đổi breaking có schema/config version và hướng chuyển đổi hoặc rebuild cache. Không gọi docs kỹ thuật hoàn tất khi contracts vẫn chỉ là bản thiết kế chưa kiểm chứng.

Quay lại [bản đồ docs](../README.md) để chọn nhóm nội dung phù hợp.
