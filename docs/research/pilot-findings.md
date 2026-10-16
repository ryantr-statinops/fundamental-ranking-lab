# Kết quả pilot khả thi dữ liệu — Stage 01

## Phạm vi và trạng thái

Ngày chạy: 2026-10-16. Chạy roster ứng viên 40 doanh nghiệp × 4 cutoff cuối năm, tổng 160 cells. Không tải returns và không dùng returns để chọn roster. Các fixture XML trong tests là dữ liệu tổng hợp, không phải quan sát thị trường.

Live SEC ingestion chưa chạy vì `FRL_SEC_USER_AGENT` chưa được cấu hình. Roster hiện tại chưa có xác nhận lịch sử cho membership, ticker/share class, SIC hoặc candidate flags. Vì vậy lần chạy tạo đủ coverage records nhưng có **0 snapshot thực**, 0 filing fact, 0 ratio có giá trị, 0 doanh nghiệp đối chiếu thực và 0 group pass. Tất cả sáu nhóm ở trạng thái blocked; Stage 01 chưa qua cổng.

## Run và khả năng tái lập

Run bị chặn và lần replay offline được ghi dưới `artifacts/` local; các payload rỗng/metadata không được commit. Lần chạy: `20261016T141702.644186Z-04aa3bd0-fb9b-4140-bd55-5ab3d3d125a9`. Replay parent đó: `20261016T141711.104161Z-5a6aebd5-43cf-490e-bbc3-5dcf06dd93ae`. Cả hai đều exit 3, status `blocked`, có 160 cells và 0 snapshot thực. Replay dùng raw index rỗng và không gọi mạng.

Pinned source-code SHA-256: `d385584bf492fab7fed892f5410bdbf3342f0030363d7afaaf267140bde787ef`. Roster CSV SHA-256: `de96af88be89cf19aa16d772e2cc9e84a679dd3eaf2fadf38b177522f948e5a2`. Content hashes (facts / ratios / coverage): `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` / `11857bf8addc8b5187be805881f86599fb8d33d4f0410e55f28904af4f94d616` / `df11b329ddbf7526b6414affbf3a330fcc9b12716b2767da09adb5ce3f3d64d2`. Initial and replay content hashes matched exactly.

Manifest lưu config, roster, evidence, source code, lockfile, runtime, schema/factor/mapping và output hashes. `reconciliation.csv` là template đang chờ kiểm tra; không có expected values được bịa hoặc approval giả. Hai blockers ghi trong run nguồn là `sec_contact_not_configured` và `independent_reconciliation_and_user_review_pending`; replay còn blocker review vì absence of contact chỉ áp dụng cho đường thu thập.

## Blockers và việc cần làm

1. Người vận hành cấu hình contact email thật trong `FRL_SEC_USER_AGENT` ở môi trường local; không đưa contact vào repository hoặc chat.
2. Kiểm chứng roster và cutoff-level membership/identifier/SIC/corporate-action evidence; không thay ứng viên dựa trên độ dễ lấy dữ liệu.
3. Thu SEC raw và giá theo policy, đối chiếu parser/facts với filing gốc ít nhất 10 doanh nghiệp thuộc đủ sáu nhóm.
4. Tạo review gắn parent run và checksums; người dùng kiểm tra expected/actual, đơn vị, thời kỳ, nguồn và tolerance trước khi nhóm có thể pass.
5. Chạy lại pilot, lưu source assessment và group gate results. Audit toàn universe vẫn cần hoàn tất trước backtest.

## Giới hạn

Kết quả này chỉ chứng minh đường chạy có thể ghi một run blocked 160 cells và replay offline. Nó không đánh giá coverage hoặc hiệu suất, không xác nhận survivor-free universe, và không đủ căn cứ loại/giữ bất kỳ nhóm ngành nào trong nghiên cứu.
