# Stage 07 — Vận hành nghiên cứu hàng quý

Trạng thái: **Đã triển khai baseline vận hành nghiên cứu hàng quý, replay và backup engine**. Phụ thuộc: [stage 06](06-validation-reporting.md) và các cổng dữ liệu/engine đã đạt. Mục tiêu là tạo artifacts nghiên cứu đều đặn; không tích hợp broker hoặc thực hiện giao dịch thật.

### Tiến độ implementation:
- [x] Xây dựng Data Contracts & Parquet Schemas cho Quarterly Operations (`QuarterlyPhaseRecord`, `ExecutionFillRecord`, `BackupManifest`).
- [x] Hiện thực cơ chế Writer Lock nguyên tử (`file_lock`) chống tranh chấp và bảo vệ tính toàn vẹn dữ liệu.
- [x] Hiện thực Pha 1 `signal`: Pipeline tự động từ bóc tách cutoff $\to$ features $\to$ ranking $\to$ proposed target weights.
- [x] Hiện thực Pha 2 `reconcile`: Đọc giá Open, tính simulated execution fills và chốt actual holdings sau phí 10 bps.
- [x] Hiện thực Offline Replay Engine với cơ chế xác minh mã băm SHA-256 toàn vẹn trước khi tái lập.
- [x] Hiện thực công cụ Sao lưu an toàn `backup_run()` xuất `checksums.sha256` và `backup_manifest.json`.
- [x] Tích hợp lệnh CLI `uv run frl quarterly` và `uv run frl replay`.
- [x] Biên soạn Sổ tay Vận hành Thực tế: [Quarterly Runbook](../guides/quarterly-runbook.md).

## Đầu vào và điều kiện vận hành
## Publish, quan sát và phục hồi

- Output bundle: industry ranking, candidate reasons, target/holdings/cash, coverage/gates, proposed-vs-simulated execution, manifest và report HTML/CSV. Ghi rõ phase và as-of; chưa có fills thì không gọi targets là actual holdings.
- JSONL logs có run/stage/source/status/duration/count/retry/quarantine; redact contact/secret. Summary hiển thị approved/blocked groups, unknown identity, stale ratios, unresolved events, top-10/cash/cap exposure và data lag.
- Một writer lock theo data root/cutoff; lần chạy thứ hai báo busy, không trộn output. Resume từ checkpoint nhưng mỗi attempt có run_id; pinned successful outputs bất biến. Atomic publish; latest pointer riêng theo cutoff/phase chỉ trỏ approved run.
- Data revision hoặc bug fix tạo version/run mới kèm supersedes và lý do; giữ bản gốc, so diff business outputs. Không overwrite audit trail để “sửa lịch sử”.
- Backup raw index, raw blobs, normalized inputs, manifests và reports ra vị trí local thứ hai do người vận hành cấu hình trước dùng thường xuyên; kiểm tra hash và restore một sample run. Không xóa raw/snapshots tự động, không cam kết retention khi chưa có backup.

## Kiểm tra nghiệm thu

Dry run bằng fixtures offline đi hết signal → reconcile → outcome. Replay sau khi provider thay dữ liệu vẫn tái tạo snapshot cũ; amended filing sau cutoff không thay targets. Thiếu open thì reconcile blocked, có open hợp lệ thì accounting/fees đạt stage 05 invariants.

Mô phỏng timeout/429, mất nguồn, disk full, invalid schema, interrupted write, concurrent run và corrupt checksum: không publish partial/approved output, giữ log/checkpoint, restart an toàn. Backup restore phải chạy lại được ít nhất một approved run và xác minh input hashes.

Bàn giao runbook gồm environment setup từ lockfile, các lệnh/phase, vị trí dữ liệu, gate triage, replay/backup/restore và cách cập nhật versions. Sau dry run đạt mới thực hiện một cutoff hiện có với manual review quality report. Việc thêm scheduler, thông báo ra ngoài, public hosting hoặc broker execution cần phạm vi/ủy quyền riêng; không nằm trong v1 này.
