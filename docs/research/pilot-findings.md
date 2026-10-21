# Kết quả pilot khả thi dữ liệu — Stage 01

## Phạm vi và trạng thái

Ngày chạy: 2026-10-16. Chạy roster ứng viên 40 doanh nghiệp × 4 cutoff cuối năm, tổng 160 cells. Không tải returns và không dùng returns để chọn roster. Các fixture XML trong tests là dữ liệu tổng hợp, không phải quan sát thị trường.

`FRL_SEC_USER_AGENT` đã được cấu hình thành công trong môi trường local/secrets. Pipeline thu thập dữ liệu thô từ SEC EDGAR đã hoàn tất thu thập cho **40 / 40 doanh nghiệp** (24.177 records được lập chỉ mục trong `data/raw/.records_cache.json`).

### Bài học kinh nghiệm về kích thước và dung lượng thu thập:
1. **Kích thước file toàn văn:** Các file `.txt` submission toàn văn (`<SEC-DOCUMENT>`) của các tổ chức tài chính lớn có kích thước từ 50MB đến 200MB/file, chiếm tới gần 70% dung lượng thô (~66 GB).
2. **Tách biệt dữ liệu lõi:** Pipeline bóc tách chỉ yêu cầu các file XML/XBRL gốc và JSON metadata (~25 GB). Bộ công cụ `scripts/pack_raw.py` đã được tạo để đóng gói gọn dữ liệu cốt lõi (ước tính 2.5 - 3.5 GB) phục vụ việc chạy trên Cloud/Google Colab.
3. **Khả năng Resume:** Đã bổ sung persistent cache index vào `RawStore` và `SECProvider`, cho phép dừng và tiếp tục quá trình thu thập/xử lý mà không bị tải lại hoặc thất thoát dữ liệu.

Roster hiện tại vẫn là candidate roster đang chờ kiểm chứng lịch sử và đối chiếu độc lập (reconciliation). Bước parsing và tính ratios trên tập dữ liệu thật đang được triển khai.

## Run và khả năng tái lập

Run blocked ban đầu: `20261016T141702.644186Z-04aa3bd0-fb9b-4140-bd55-5ab3d3d125a9`. Replay parent đó: `20261016T141711.104161Z-5a6aebd5-43cf-490e-bbc3-5dcf06dd93ae`. Replay dùng raw index rỗng và không gọi mạng.

Lần thu thập dữ liệu thô thực tế ngày 2026-10-20 đã hoàn thành 40 CIKs với 24.177 raw records. Quá trình tính toán facts và ratios đang được phân bổ thực thi trên môi trường Google Colab để tối ưu tài nguyên tính toán (RAM/Disk).

## Blockers và việc cần làm

1. ~~Cấu hình contact email trong `FRL_SEC_USER_AGENT`~~ *(Đã hoàn thành)*.
2. ~~Thu thập SEC raw dữ liệu thật cho 40 doanh nghiệp~~ *(Đã hoàn thành 100%)*.
3. Đóng gói và chạy parsing / 8 ratios trên môi trường Cloud (Google Colab) qua `notebooks/01_colab_pilot_runner.ipynb`.
4. Kiểm chứng roster và cutoff-level membership/identifier/SIC/corporate-action evidence.
5. Đối chiếu độc lập parser/facts với filing gốc ít nhất 10 doanh nghiệp thuộc đủ sáu nhóm.
6. Tạo review gắn parent run và checksums; người dùng kiểm tra expected/actual, đơn vị, thời kỳ, nguồn và tolerance trước khi duyệt cổng.
## Giới hạn

Kết quả này chỉ chứng minh đường chạy có thể ghi một run blocked 160 cells và replay offline. Nó không đánh giá coverage hoặc hiệu suất, không xác nhận survivor-free universe, và không đủ căn cứ loại/giữ bất kỳ nhóm ngành nào trong nghiên cứu.
