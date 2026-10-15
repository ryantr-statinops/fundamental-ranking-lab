# Stage 07 — Vận hành nghiên cứu hàng quý

Trạng thái: chưa bắt đầu. Phụ thuộc: [stage 06](06-validation-reporting.md) và các cổng dữ liệu/engine đã đạt. Mục tiêu là tạo artifacts nghiên cứu đều đặn; không tích hợp broker hoặc thực hiện giao dịch thật.

## Đầu vào và điều kiện vận hành

Nhận package/uv.lock đã kiểm chứng, approved groups/dictionary/mapping versions, source settings, kết luận nghiên cứu và runbook. Kết luận performance âm không cấm forward tracking, nhưng phải ghi mục đích quan sát và không diễn giải là chiến lược đã được xác nhận. Nếu historical data blocker còn tồn tại, chỉ chạy tracking trong scope hiện tại đã xác minh; không nâng nhãn historical study thành complete.

## Luồng chạy

1. Người vận hành chọn cutoff rõ ràng từ calendar cuối quý, chạy sau cutoff; future cutoff bị từ chối. Stage 07 mặc định manual CLI, không tự tạo automation hay scheduler.
2. `uv run frl quarterly --config configs/quarterly.toml --cutoff YYYY-MM-DD` thu dữ liệu tăng dần với rate/cache/retry stage 01, tạo raw revision và manifest. Nguồn phản hồi hiện tại chỉ được đưa vào snapshot nếu publication/availability đã biết ≤ cutoff; không dùng downloaded_at thay publication.
3. Chạy gate identity/listing/price/event/coverage; sau đó snapshots → features → ranking → target weights theo approved config. Có blocker thì xuất diagnostics, exit 3 và không publish artifact approved hoặc update latest.
4. Trước phiên mở tiếp theo chỉ xuất proposed targets và quality report. Khi raw open thực có, chạy bước reconcile để tính simulated fills/fees/shares với parent target run, không giả định đã biết giá open lúc signal.
5. Khi kết thúc horizon, append outcome/reconciliation report thành run mới; snapshot/target gốc bất biến. Báo late filing, amendments và dữ liệu nguồn revise, không retroactively sửa quyết định đã công bố.

Interface bổ sung cần triển khai trong stage này: `frl quarterly ... --phase signal|reconcile|outcome` (mặc định signal), reconcile/outcome yêu cầu `--input-run <parent_id>` và dates phù hợp. `frl replay --input-run <id>` chạy offline theo manifest pin toàn bộ inputs/config/versions; thiếu input hash phải thất bại, không tự tải bản mới.

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
