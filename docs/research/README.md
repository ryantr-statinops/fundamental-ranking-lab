# Bằng chứng và kết quả nghiên cứu

Mục này lưu diễn giải, bằng chứng và giới hạn của những gì đã kiểm tra. **Chưa có pilot, audit, thí nghiệm hoặc performance report.** Các file dưới đây là kế hoạch bàn giao, không phải kết quả đã có.

## Kế hoạch nội dung

| File dự kiến | Nội dung | Stage |
|---|---|---|
| `source-assessment.md` | Đánh giá nguồn: truy cập, coverage lịch sử, listing/delisting, shares/events, provenance và điều kiện sử dụng đã kiểm tra | 01; mở rộng 02 |
| `pilot-findings.md` | Roster version, coverage 160 cells, reconciliation, pass/block từng nhóm và blockers | 01 |
| `universe-audit.md` | Historical evidence, discrepancies, missing denominators, sample/scope manifest và kết luận completeness | 02 |
| `experiment-register.md` | Registry nghiên cứu: câu hỏi, primary/secondary, split, frozen manifest và lịch sử xem test | 06, trước final test |
| `validation-findings.md` | Kết quả Q1–Q3, ablations, CI/p-values, cash/cost/risk, giới hạn power và kết luận | 06 |

Quy tắc nghiên cứu gốc ở [idea](../idea/README.md); thủ tục thực hiện ở [plan](../plan/README.md). Template/bằng chứng bắt buộc cho mỗi file nằm trong [kế hoạch bàn giao](../plan/documentation-delivery.md).

## Cấu trúc một ghi nhận nghiên cứu

Mỗi ghi nhận cần ngày, câu hỏi, trạng thái planned/running/completed/blocked, giả định, data scope, run_id và parent runs, commit/lock/config/factor/mapping versions, cách kiểm tra, kết quả và giới hạn. Tách quan sát từ dữ liệu khỏi suy luận hoặc đề xuất thay đổi.

Artifact reference ghi artifact root tương đối, run_id, relative path, checksum và hướng dẫn tái lập. Nếu dữ liệu chỉ lưu local hoặc bị giới hạn phân phối, ghi rõ điều kiện truy cập; người đọc GitHub không được dẫn tới một file local như thể họ đã có quyền tải. Không đưa raw data, private contact hoặc credentials vào docs để làm bằng chứng.

## Tính toàn vẹn nghiên cứu

- Planned hoặc blocked không được ghi như completed; chưa có kết quả thì ghi chưa đo, không tạo bảng số ví dụ trông như dữ liệu thực.
- Kết quả âm và unavailable phải xuất hiện cùng kết quả dương; thiếu nguồn hoặc event chưa giải quyết không biến thành return 0 hay −100% mặc định.
- Primary và exploratory có registry/version rõ. Thay cấu hình sau xem test phải ghi lần thay đổi và không tiếp tục gọi kết quả mới là final test chưa thấy.
- Cập nhật phát hiện mới bằng run/version mới và liên kết supersedes; không xóa lịch sử đối chiếu để thay kết luận cũ.
- Research chứa phần diễn giải ổn định; bảng/figures/logs tự sinh ở artifacts. Không diễn giải pilot đạt cổng là universe survivor-free hoặc chứng minh alpha.

Một báo cáo được coi hoàn thành khi người khác xác định được đầu vào, phương pháp, bằng chứng và phạm vi kết luận; thiếu dữ liệu vẫn có thể hoàn thành feasibility report nhưng không đồng nghĩa hoàn thành backtest.

Quay lại [bản đồ docs](../README.md).
