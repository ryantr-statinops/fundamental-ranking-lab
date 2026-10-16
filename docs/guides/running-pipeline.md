# Chạy pilot Stage 01

## Điều kiện trước

Từ root repo, cài dependencies đã khóa và kiểm tra môi trường:

```powershell
uv sync --locked --extra dev
uv run frl doctor --config configs/sample.toml
```

Pilot dùng roster ứng viên tại `configs/pilot-roster.csv`. Các dòng này chưa xác nhận listing lịch sử, SIC, share class hoặc flags về lỗ/corporate actions. Trước khi kết luận về coverage, bổ sung và kiểm tra bằng chứng historical theo [Stage 01](../plan/01-data-feasibility-pilot.md). Không thay mã vì khó thu thập dữ liệu.

## SEC contact

SEC yêu cầu request nhận diện ứng dụng và contact. `FRL_SEC_USER_AGENT` là chuỗi dạng `Tên ứng dụng email-liên-hệ`; đây không phải tài khoản hay API key. Dùng email liên hệ thật mà bạn kiểm soát. Đặt biến trong cửa sổ PowerShell đang dùng, ví dụ thay placeholder trước khi chạy:

```powershell
$env:FRL_SEC_USER_AGENT = "Fundamental Ranking Lab your-real-contact@example.com"
```

Giá trị chỉ nằm trong môi trường local, không đưa vào TOML, Git, logs hay chat. Nếu biến chưa có, collector không gọi mạng, ghi blocker `sec_contact_not_configured` và trả exit code 3.

## Chạy và replay

```powershell
uv run frl pilot --config configs/pilot.toml
uv run frl pilot --config configs/pilot.toml --input-run <run_id>
```

Lệnh đầu tạo run mới dưới `artifacts/<run_id>` và raw payload dưới `data/raw`. Run output gồm manifest, selection, raw index, coverage 160 cells, facts/ratios Parquet, reconciliation CSV, group gates, blockers và feasibility report Markdown/HTML. Lệnh thứ hai đọc cache và manifest của run chỉ định; thiếu raw hoặc checksum sai thì thất bại, không tự tải lại. Hai lần transform cùng dữ liệu nên có cùng hashes facts/ratios/coverage dù run IDs khác nhau.

Exit code: `0` tất cả group gates đã qua và mọi doanh nghiệp có snapshot; `2` config sai; `3` dữ liệu/gate còn blocked hoặc chờ review; `1` lỗi thực thi. Exit `3` là run đã được ghi nhận nhưng chưa đạt khả thi dữ liệu.

## Cách đọc kết quả

Mở `feasibility.md` hoặc `feasibility.html`, sau đó kiểm tra `blockers_final.json`, `group_gates.json` và `coverage.json`. Manifest pin hash inputs/outputs và content hashes. `reconciliation.csv` bắt đầu ở trạng thái chờ đối chiếu, không tự điền giá trị expected hay phê duyệt. Chỉ sửa bản CSV kiểm tra theo workflow review được cấu hình; mọi approval phải tham chiếu đúng parent run, hashes, template và reviewer.

Không dùng run fixtures hay empty coverage làm bằng chứng đầu tư. Chưa có snapshot thật thì nhóm vẫn blocked; audit toàn universe cũng là bước riêng trước backtest.
