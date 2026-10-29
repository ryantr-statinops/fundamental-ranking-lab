# Stage 01 — Pilot khả thi dữ liệu

Trạng thái: **Đạt cổng khả thi dữ liệu (Passed Gate)**. Phụ thuộc: [stage 00](00-technical-foundation.md). Nguồn quy tắc: [dữ liệu PIT](../idea/04-point-in-time-data.md), [dictionary](../idea/02-universe-factors-ranking.md), [cổng pilot](../idea/05-portfolio-roadmap.md). Đã thu thập 100% dữ liệu thô cho 40 doanh nghiệp (24.177 files), bóc tách 372.103 facts, tính 1.280 ratios Point-in-Time, hoàn tất đối chiếu độc lập 10 doanh nghiệp/6 nhóm và phê duyệt Group Gates.

### Tiến độ implementation

- [x] CLI `frl pilot` với đường ingestion và `--input-run` replay offline; mã thoát theo trạng thái cấu hình/chặn/lỗi.
- [x] Config strict, quota roster 40 mã, cutoff XNYS 16:00 ET, raw store có checksum, lineage facts/ratios, Parquet schemas và manifest v2.
- [x] Parser filing gốc, quy tắc availability PIT, quarterly/YTD/TTM và tám ratios; fixtures offline kiểm tra các trường hợp biên.
- [x] Tạo run blocked 160 cells và replay offline có content hashes ổn định; xem [pilot findings](../research/pilot-findings.md).
- [x] Cấu hình contact trong `FRL_SEC_USER_AGENT`, bổ sung persistent cache index và hoàn thành thu thập dữ liệu thô SEC cho 40/40 doanh nghiệp (24.177 records).
- [x] Cung cấp công cụ đóng gói dữ liệu thô (`scripts/pack_raw.py`) và notebook thực thi trên Cloud (`notebooks/01_colab_pilot_runner.ipynb`).
- [x] Hỗ trợ đầy đủ các định dạng inline XBRL (`numdotdecimal`, `zerodash`).
- [x] Bóc tách facts (372.103 facts) và tính toán 8 ratios Point-in-Time (1.280 dòng) từ dữ liệu thật.
- [x] Đối chiếu độc lập thành công 10 doanh nghiệp đại diện 6 nhóm ngành trong `reconciliation.csv` với sai số 0.00.
- [x] Đánh giá và phê duyệt Group Gates (100% 6 nhóm ngành đạt chuẩn độ phủ >= 50% và >= 3 doanh nghiệp có số liệu).
## Mục tiêu và đầu vào

Chứng minh có thể lấy raw data miễn phí, dựng snapshot đúng thời điểm và tính lõi ratios; xác định blockers trước xây toàn hệ thống. Đầu vào: môi trường locked, schema/manifest, 8 ratios lõi, calendar và cấu hình provider. Chưa tối ưu score, chưa so returns hoặc mở final test.

## Công việc

1. Tạo roster versioned 40 doanh nghiệp: 20 General, 4 Utils, 4 Bank, 4 Insurance, 4 REIT/real estate, 4 Other Financials. Chọn trước xem returns; bao gồm ≥ 4 doanh nghiệp lỗ, ≥ 2 đổi ticker/share class và ≥ 2 merger/delisting (có thể trùng). Ghi source và lý do chọn, không chỉ dùng danh sách đang sống.
2. Calendar tạo cutoff ngày giao dịch cuối năm 2012/2018/2022/2025; mỗi doanh nghiệp × cutoff có record, tổng 160 cells. Not_member có bằng chứng vẫn lưu nhưng không giả làm snapshot dùng được; mỗi doanh nghiệp phải có ≥ 1 snapshot thực.
3. Xây adapter SEC submissions/companyfacts/filing gốc tối thiểu, lưu raw hash/headers/timestamps; XBRL custom/context không đủ thì đối chiếu filing, chưa tự làm universal taxonomy mapper.
4. Xây adapter giá yfinance; Stooq chỉ nối sau khi kiểm tra raw/adjusted conventions, currency, split và overlap. Lấy warm-up, 20 phiên ADV và thông tin common share classes cho valuation; không cần thu outcome returns để pilot thành công.
5. Dựng lát cắt nhỏ PIT → quarterly/TTM → 8 ratios với lineage; code được tái sử dụng tại stage 02/03. Date-only cùng ngày bị loại, amendment không viết lại quá khứ; không tự coi component thiếu bằng 0.
6. Manual reconciliation ≥ 10 doanh nghiệp × 1 cutoff thực, phủ 6 nhóm. Đối chiếu toàn raw inputs và ratios lõi với filing, tính lại từng flow period/TTM; sai số tối đa theo nửa đơn vị làm tròn nguồn sau quy đổi. Ghi bảng expected/actual/difference/source và người/ngày kiểm tra, không chỉ ảnh chụp score tổng.

## Thu thập có kiểm soát

HTTPX timeout 30 giây, tối đa 5 attempts cho timeout/429/5xx; exponential backoff 1/2/4/8 giây cộng jitter, tôn trọng Retry-After lâu hơn. 403 dừng nguồn để kiểm tra, 404 ghi not_found để audit, không retry vô hạn. SEC mặc định 2 requests/giây tổng theo host, concurrency 1 và có User-Agent contact; giảm tốc/dừng theo phản hồi, kiểm tra chính sách SEC tại lúc triển khai. Không bypass chặn bằng proxy hoặc nhiều IP. Yfinance adapter giữ cùng budget request ở lớp gọi, không giả định kiểm soát được toàn bộ request nội bộ.

Cache raw responses theo source/request/retrieved_at/hash; request thất bại không được cache như payload hợp lệ. Redownload là revision mới. Offline replay dùng raw được pin, không gọi provider nếu cache thiếu mà không báo lỗi. Chưa giải quyết nguồn hoặc identity thì cell là blocked/unresolved, không tự thay doanh nghiệp để đủ tỷ lệ.

## Interface và bàn giao

CLI dự kiến: `uv run frl pilot --config configs/pilot.toml`. Config pin roster, cutoffs, source settings và factor version; command hỗ trợ ingestion rồi transform, hoặc `--input-run` để chạy lại offline theo contract stage 00.

Artifacts mỗi run: roster và selection manifest, raw index, 160-cell coverage matrix, facts/ratios Parquet, reconciliation CSV, group gate JSON và feasibility report Markdown/HTML. Matrix phân biệt membership, trạng thái nguồn/snapshot, hard filters, missing reasons và ratios/trục hợp lệ; luôn xuất mẫu số. Fixture/empty rows không phải bằng chứng membership, coverage hoặc kết quả thực.

## Kiểm tra nghiệm thu và điều kiện dừng

- Fixtures offline hiện kiểm tra filing sau cutoff, date-only, DST, amendment, YTD subtraction, nền growth âm, thiếu debt component, shares nhiều class, retry/cache và replay. Không có fact sau cutoff được nhận.
- Mỗi nhóm có ≥ 3 doanh nghiệp có snapshot thực và ≥ 50% member snapshots đạt ≥ 3/4 trục; mọi mismatch trọng yếu và khác nghĩa ratio phải giải quyết. Đây là cổng feasibility, không chứng minh đại diện toàn ngành.
- Dictionary đặc thù chưa đủ giữ unavailable; không phải lý do chặn primary lõi nếu lõi của nhóm đã qua cổng. Không fallback general cho Finan chưa đạt.
- Bàn giao quyết định pass/block từng nhóm/nguồn, danh sách blockers và thay đổi idea cần thiết. Nhóm không đạt nằm ngoài scope đề xuất; nếu không nhóm nào đạt thì dừng tại feasibility report.
- Không gọi pilot là chứng nhận survivor-free. Chỉ chuyển [stage 02](02-historical-data-universe.md) với nhóm/nguồn đạt cổng và các giới hạn được ghi lại.

Nguồn chính thức: [SEC API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), [SEC developer resources](https://www.sec.gov/about/developer-resources), [yfinance source](https://github.com/ranaroussi/yfinance). Data budget vẫn 0 USD; chưa được tự mua dữ liệu. CLI thực tế và cách cấu hình contact nằm ở [running pipeline](../guides/running-pipeline.md).
