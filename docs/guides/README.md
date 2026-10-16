# Hướng dẫn sử dụng và vận hành

Mục này dành cho người cần cài môi trường, chạy pilot và xử lý sự cố. Hướng dẫn được đánh dấu theo đúng mức đã kiểm chứng; pilot có đường offline và live collection còn phụ thuộc contact SEC cùng roster evidence.

Dùng tên `guides/` cho cả hướng dẫn sử dụng và vận hành v1; không tạo thêm thư mục `operations/` có nội dung trùng lặp. File cấu hình thực tế sẽ nằm ở `configs/` root; tài liệu configuration ở đây giải thích cách dùng.

## Kế hoạch nội dung

| File dự kiến | Người đọc sẽ làm được gì? | Stage |
|---|---|---|
| `setup.md` | Cài môi trường locked, xác minh Python/package/CLI trên Windows; đối chiếu Linux CI | 00 |
| `configuration.md` | Chuẩn bị config và env local, phân biệt research/provider/path settings, kiểm tra config hợp lệ | 00; bổ sung theo stage |
| `troubleshooting.md` | Chẩn đoán config lỗi, nguồn lỗi, gate thất bại, cache/identity/unit issues và replay mismatch | 00–07, chỉ ghi tình huống đã kiểm tra |
| [running-pipeline.md](running-pipeline.md) | Chuẩn bị contact local, chạy pilot/replay, đọc artifacts và exit codes | 01 |
| `reading-reports.md` | Đọc coverage, scores, targets/cash, performance và inference đúng phạm vi | 04–06 |
| `quarterly-runbook.md` | Chạy signal → reconcile → outcome hàng quý, phân biệt targets với simulated holdings | 07 |
| `backup-and-restore.md` | Backup artifacts/raw inputs, kiểm tra checksum, restore và replay một run | 07 |

Chi tiết bàn giao và nghiệm thu: [kế hoạch tài liệu](../plan/documentation-delivery.md). Mỗi file chỉ được tạo khi stage tương ứng có chức năng hoặc workflow thực để kiểm tra; không tạo hàng loạt hướng dẫn placeholder.

## Chuẩn của một guide

1. Nêu tác vụ, điều kiện trước, hệ điều hành và commit/version đã thực hành; ghi network/data requirements và outputs dự kiến.
2. Dùng command thực đã đối chiếu `--help`, đường dẫn theo repo và ví dụ không chứa thông tin riêng. Placeholder cần thay phải được chỉ rõ.
3. Phân biệt bước chỉ đọc với bước tạo dữ liệu, tải mạng hoặc sửa config. Không mặc định người dùng đã có local datasets/artifacts chỉ vì có file docs.
4. Ghi cách biết bước đã thành công, vị trí manifest/log/report, exit code và cách xử lý lỗi có thể gặp.
5. Link tới technical reference khi cần danh sách schema/config đầy đủ, và tới research findings để hiểu giới hạn; không chép lại các công thức dễ lệch version.

Hướng dẫn không dùng hành động phá hủy để “reset cho sạch”. Recovery mặc định tạo run mới hoặc rebuild cache có thể tái tạo, giữ raw data và audit trail; mọi bước xóa phải có phạm vi rõ và không là mặc định tự động.

Một guide hoàn thành khi người khác chạy được happy path và ít nhất một failure path đã nêu bằng môi trường/fixtures được ghi lại. Khi command/options đổi, cập nhật guide trong cùng đợt sửa code.

Quay lại [bản đồ docs](../README.md) hoặc [technical](../technical/README.md) để tra thiết kế.
