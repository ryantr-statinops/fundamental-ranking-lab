# Sổ tay Vận hành Nghiên cứu Hàng quý (Quarterly Runbook)

Tài liệu này là quy trình chuẩn (SOP) dành cho người vận hành thực hiện chu kỳ tái cân bằng danh mục định lượng mỗi quý, sao lưu dữ liệu và tái lập kết quả offline.

---

## 1. Lịch Vận hành 3 Pha (3-Phase Lifecycle)

| Pha | Thời điểm thực hiện | Tác vụ chính | Lệnh CLI |
|---|---|---|---|
| **Pha 1: `signal`** | **16:00 ET** Ngày giao dịch cuối quý (Cutoff) | Bóc tách báo cáo tài chính đã nộp trước cutoff, tính điểm 4 trục và tạo **Proposed Target Weights**. | `uv run frl quarterly --cutoff YYYY-MM-DD --phase signal` |
| **Pha 2: `reconcile`** | **09:30 ET** Mở phiên giao dịch hôm sau | Đọc giá Mở cửa (Open Price), giải bisection phí 10 bps, khớp lệnh mô phỏng và chốt **Actual Holdings**. | `uv run frl quarterly --phase reconcile --input-run <signal_dir>` |
| **Pha 3: `outcome`** | Cuối quý tiếp theo | Đo lường lợi nhuận thực tế (Return), đối soát cổ tức/chia tách và ghi nhận báo cáo nộp muộn. | `uv run frl evaluate --input-ranking <ranking_dir>` |

---

## 2. Hướng dẫn chi tiết từng bước

### Bước 1: Pha Signal (16:00 ET ngày cuối quý)
Vào ngày giao dịch cuối cùng của quý (ví dụ: ngày 31/12):
```bash
uv run frl quarterly --cutoff 2025-12-31 --phase signal
```
- Hệ thống tự động kích hoạt **Writer Lock** chống ghi đè.
- Xuất ra `proposed_targets.parquet` và báo cáo chất lượng signal.
- *Lưu ý quan trọng:* Lúc này chưa có giá mở cửa nên chưa coi targets là actual holdings.

### Bước 2: Pha Reconcile (09:30 ET sáng hôm sau)
Khi thị trường mở cửa phiên giao dịch đầu tiên của quý mới:
```bash
uv run frl quarterly --phase reconcile --input-run artifacts/quarterly/2025-12-31/<signal_run_id>
```
- Khớp lệnh mô phỏng theo giá Open thực tế.
- Khấu trừ phí giao dịch tự tài trợ ($10\text{ bps}$).
- Xuất ra `actual_holdings.parquet` và `execution_fills.parquet`.

### Bước 3: Đánh giá Hiệu quả Ngoài mẫu (Sau 1 quý)
Đo lường các kiểm định Q1 (Fama-MacBeth OLS), Q2 (Industry Terciles) và Q3 (Net Active Return):
```bash
uv run frl evaluate --input-ranking artifacts/quarterly/2025-12-31/<signal_run_id>/ranking
```

---

## 3. Quy trình Tái lập Offline (Offline Replay)

Để chạy lại kết quả của một quý trong quá khứ mà hoàn toàn không cần gọi mạng internet và đảm bảo dữ liệu không bị thay đổi:
```bash
uv run frl replay --input-run artifacts/quarterly/2025-12-31/<run_id>
```
Hệ thống sẽ:
1. Đọc file `manifest.json`.
2. Kiểm tra mã băm SHA-256 của toàn bộ các file đầu vào.
3. Nếu có bất kỳ file nào bị sửa đổi $\to$ Báo lỗi `Checksum mismatch` và dừng ngay lập tức.
4. Tái tạo 100% kết quả vào thư mục `replay-<id>/`.

---

## 4. Xử lý Sự cố thường gặp (Troubleshooting)

1. **Lỗi `LockAcquisitionError: Operation locked`:**  
   - Nguyên nhân: Có một tiến trình chạy trước chưa hoàn thành hoặc bị tắt đột ngột để lại file `.operation.lock`.  
   - Xử lý: Kiểm tra xem có tiến trình nào đang chạy ngầm (`ps aux | grep python`), nếu không có thì xóa file `.operation.lock` trong thư mục artifact của cutoff đó rồi chạy lại.
2. **Lỗi `Cannot run signal for future cutoff`:**  
   - Nguyên nhân: Bạn chọn ngày cutoff ở tương lai. Hệ thống từ chối để tránh vi phạm nguyên tắc Point-in-Time.
3. **Lỗi `Missing target_weights.parquet` ở pha Reconcile:**  
   - Nguyên nhân: Bạn chưa truyền đúng đường dẫn `--input-run` trỏ tới thư mục của pha Signal trước đó.
