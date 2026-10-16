# Kế hoạch bổ sung và bàn giao tài liệu

Ngày lập: 2026-10-16. Trạng thái: đã tổ chức mục tài liệu; technical references, Stage 01 source assessment, blocked pilot findings và running guide đã được cập nhật theo implementation. Các file còn lại vẫn theo backlog stage.

Đây là workstream xuyên suốt [stage 00–07](README.md), không phải stage 08 và không phải điều kiện để viết sẵn toàn bộ docs trước code. Mục tiêu: kết thúc mỗi stage có đủ tài liệu giải thích hệ thống đã xây, bằng chứng đã thu và cách sử dụng đã kiểm tra.

## Phạm vi và nguyên tắc

Đầu vào: [idea](../idea/README.md), plan hiện có và trạng thái repo chỉ chứa Markdown. Trong đợt tổ chức này tạo [bản đồ docs](../README.md) và README cho [technical](../technical/README.md), [research](../research/README.md), [guides](../guides/README.md); thêm link điều hướng ở README dự án/plan. Chưa tạo code, config chạy thật, kết quả nghiên cứu hoặc lệnh giả.

Research rules giữ nguồn chính ở idea; plan là công việc dự kiến; technical là contract/implementation reference; research là bằng chứng/diễn giải; guides là cách thực hiện tác vụ. Nội dung giao nhau phải dẫn nguồn, không giữ nhiều bản công thức hoặc tham số độc lập.

## Ma trận bàn giao từng file

Các đường dẫn dạng code là file **sẽ tạo** khi có implementation/bằng chứng, chưa phải link tài liệu đã tồn tại. Mỗi dòng có nội dung tối thiểu và bằng chứng hoàn thành.

| File trong docs/ | Stage | Nội dung bắt buộc | Nghiệm thu |
|---|---|---|---|
| `technical/architecture.md` | 00; cập nhật 01–07 | Module map, data flow, provider boundary, Parquet/DuckDB vai trò, offline/online separation | Khớp source modules và một end-to-end fixture run; gắn commit |
| `technical/data-contracts.md` | 00; mở rộng 01–06 | Columns/types/keys/null/units/status/reasons của bảng đã có, Arrow/schema version, valid/invalid examples | Validator tests thể hiện constraints và version; chưa có bảng thì ghi planned |
| `technical/configuration-and-cli.md` | 00; mở rộng theo command | Required/default fields, nguồn config/env, precedence, unknown-key errors, options, exit codes, hashes | Khớp config models và CLI help; tests config sai/đúng và private-value redaction |
| `technical/data-lineage-and-versioning.md` | 00–03; cập nhật khi output đổi | Manifest/raw/input hashes, temporal joins, effective/publication/ingestion time, immutable revisions, rebuild/migration | Trace một ratio về raw; future amendment không đổi snapshot; schema upgrade có test |
| `technical/decisions.md` | 00 trở đi | ID/ngày/status, context, lựa chọn, alternatives/tradeoffs, liên kết plan và implementation | Không ghi planned như implemented; thay quyết định có supersedes, không xóa lịch sử |
| `research/source-assessment.md` | 01–02 | Nguồn/endpoint, access date, historical range, delisted/shares/events coverage, sample evidence, điều kiện dùng/phân phối | Có requests/raw refs đã kiểm tra; unknown ghi unknown, không coi API tồn tại là đủ lịch sử |
| `research/pilot-findings.md` | 01 | Roster version, 160-cell matrix, ≥10 manual checks, group gates, mismatches và blockers | Link run/checksum và bảng reconciliation; đạt/không đạt có mẫu số và nguồn |
| `research/universe-audit.md` | 02 | Historical membership evidence, discrepancies, completeness limits, unresolved events, locked scope/sample | Pin scope manifest trước performance; kết luận survivor-free chỉ khi có bằng chứng |
| `research/experiment-register.md` | 06 trước mở test | Study IDs, hypotheses primary/secondary, splits/purge, frozen config/inputs, seed, test-access log | Registry khóa trước test; thay study sau xem test ghi exploratory |
| `research/validation-findings.md` | 06 | Q1–Q3, T/CI/p-values, ablations, cash/cost/risk, scope, negative/unavailable và kết luận | Bảng đối soát artifacts và manifest; không đổi primary để chọn kết quả đẹp |
| `guides/setup.md` | 00 | Prerequisites, uv/Python locked environment, doctor/test smoke, Windows và Linux CI scope | Fresh checkout cài theo lock chạy được; ghi môi trường/commit và expected outputs |
| `guides/configuration.md` | 00; cập nhật theo stage | Copy sample config, biến môi trường, path/research/provider distinctions, validation và private data | Một config hợp lệ và một config sai có kết quả đúng; không chứa secret/contact thật |
| `guides/running-pipeline.md` | 01–06 | Commands đã có, thứ tự, network vs replay, parent run inputs, outputs và gates | Happy path fixtures và một gate-failure path; CLI reference khớp implementation |
| `guides/troubleshooting.md` | 00–07 | Symptom/exit code, cách kiểm tra log, nguyên nhân, recovery và tiêu chí kết thúc | Mỗi mục có test hoặc ca đã ghi nhận; không đề xuất xóa raw hay hạ gate để chạy tiếp |
| `guides/reading-reports.md` | 04–06 | Coverage/scores trước, targets vs holdings/cash sau; metrics/inference khi có | Đọc một sample report có negative/unavailable; không gọi targets là giao dịch đã xảy ra |
| `guides/quarterly-runbook.md` | 07 | Signal/reconcile/outcome, as-of, phase prerequisites, manual quality review và publish status | Dry run cả 3 phases, thiếu open blocked, approved/latest chỉ đổi đúng lúc |
| `guides/backup-and-restore.md` | 07 | Phạm vi raw/index/manifest/artifacts, backup root, hashes, restore path và offline replay | Restore một approved run sang vị trí khác, xác minh hash và replay; không chỉ ghi đã copy |

## Thứ tự thực hiện theo stage

1. **Stage 00:** tạo technical references và setup/config guides cùng package/validators/CLI. Chốt chi tiết schema, temporal model và config hashes trước pilot; docs phải phân biệt planned/implemented/verified. Troubleshooting bắt đầu bằng các failure cases đã kiểm tra.
2. **Stage 01:** bổ sung source assessment, pilot findings và hướng dẫn pilot thực; material không đủ dữ liệu vẫn có báo cáo blocker, không giả thành pass. Tái sử dụng cùng code/contracts khi sang stage 02/03.
3. **Stage 02–03:** cập nhật historical/source audit, pin scope và hoàn thiện temporal lineage/contracts theo facts thực. Không bỏ discrepancy để đạt completeness.
4. **Stage 04–05:** bổ sung schema scores/weights/ledgers vào contract; running-pipeline và reading-reports theo ranking/portfolio đã triển khai và accounting fixtures.
5. **Stage 06:** freeze experiment register trước test, rồi viết validation findings từ artifacts. Cập nhật report guide theo frequency/data limits thực; kế hoạch đăng ký không được ghi là kết quả.
6. **Stage 07:** bàn giao quarterly runbook, backup/restore và các failure/recovery paths đã thực hành. Không tự thêm scheduler, messaging, hosting hoặc broker integration.

## Hai quyết định kỹ thuật cần cụ thể hóa trước pilot

**Temporal model:** valid_from/valid_to mô tả thời gian hiệu lực; public_available_at/known_at mô tả thông tin đã biết; retrieved_at mô tả lúc tải. Revision mới có thể sửa effective interval cũ; uniqueness/non-overlap xét theo business key trong cùng revision/as-of view, không cấm lưu lịch sử sửa đổi. Stage 00 phải ghi quy tắc chọn revision và test ở boundary/overlap; stage 01–03 xác minh bằng facts thực. Chi tiết làm rõ này diễn giải yêu cầu immutable history, không thay cutoff nghiên cứu.

**Config identity:** tách research hash (scope/cutoffs/groups/factors/weights/costs/splits/seed) khỏi execution hash (provider/rate/timeout và settings vận hành không chứa secret). Không đưa private contact hoặc machine-local absolute path vào research hash. Run manifest vẫn pin input-content hashes, code/lock/schema/mapping versions để đổi provider payload không bị coi là cùng kết quả chỉ vì research hash giống nhau. Config có path/env khác nhưng cùng logical inputs phải tái lập được; dùng fixtures kiểm tra hai trường hợp này.

## Bằng chứng, trạng thái và thay đổi

Chủ thể thực hiện stage chịu trách nhiệm cập nhật tài liệu cùng code/bằng chứng; reviewer kiểm tra acceptance của stage và docs đi kèm. Theo dõi stage state ở plan/README; mỗi README nhóm chỉ link file đã tồn tại và giữ backlog còn lại là planned. File tài liệu cần ghi stage/version kiểm chứng và giới hạn; không phải mọi file đều hoàn thiện trong stage đầu tiên.

Research references gồm run_id, commit, config/data versions, relative artifact path và checksum. Ghi rõ artifacts local hoặc hạn chế phân phối; không tạo link chết cho file chưa có. Không commit bulk raw/logs/generated charts hoặc private contact vào docs.

Thay đổi research rule quay về idea và sổ quyết định; thay implementation behavior cập nhật technical, guides và tests. Thay artifact schema cập nhật contract/version và producer/consumer references. Nếu stage bị chặn thì hoàn thành báo cáo blocker của stage đó, không đánh dấu stage sau đạt cổng.

## Nghiệm thu và Git

- Đợt tổ chức ban đầu: đủ 5 nhóm tài liệu có index, root/plan dẫn được tới bản đồ và mọi local link tồn tại. Các trạng thái cập nhật theo implementation của Stage 00–01; planned filenames không được mô tả như code hoặc evidence đã hoàn thành.
- Mỗi stage sau: không có hướng dẫn command chưa tồn tại; schema/options khớp code, example đã chạy và có test/manifest evidence. Kiểm tra Markdown links, tables, whitespace và secrets trước commit.
- Tài liệu không được gọi verified chỉ vì file có nội dung; planned/implemented/verified được đánh giá riêng cho từng phần nếu file phục vụ nhiều stage.
- Làm trên main theo yêu cầu hiện tại: kiểm tra branch/remote/working tree; mỗi file một commit, kiểm tra staged diff rồi push origin main trước chuyển file tiếp. Không stage changes ngoài phạm vi, không force-push; push lỗi/diverged thì dừng để kiểm tra.
- Kết thúc đối chiếu commit/file count, remote HEAD và working tree sạch. Đợt này chỉ tổ chức/kế hoạch tài liệu, không chứng nhận đã triển khai stage 00.
