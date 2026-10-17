# Historical universe implementation

Stage 02 cung cấp ingestion có checkpoint và audit offline. Đây là implementation bằng synthetic fixtures, chưa xác minh historical universe thật.

## Data flow

Strict history config → typed evidence bundle → content-addressed RawStore → immutable ingest run → offline as-of resolution/market filters → Parquet, audit report và scope manifest. SEC collector dùng lại timeout/retry/rate policy; price requests dùng YFinanceProvider hiện có. Không có pipeline fundamentals thứ hai.

Evidence revisions được chọn theo known_at trước khi áp `[valid_from, valid_to)`. Revision công bố sau cutoff không thay kết quả quá khứ. Entity ID, security ID và CIK có vai trò riêng; ticker không là join key. Ticker/class conflicts vào quarantine; listing thiếu nguồn độc lập với giá hoặc historical SIC thiếu giữ unresolved. SIC mapping không được overlap; mapping và raw payload được kiểm checksum.

Hard filters dùng 20 sessions XNYS gần nhất và price observations biết tại cutoff, USD và convention `verified_raw`. ADV20 dùng raw close × volume; class cao nhất được chọn trước các hard filters còn lại, ties theo security ID. Thiếu ADV của một class làm selection unresolved. Filings deduplicate các period trong cùng quý lịch; cần audit fiscal-calendar exceptions trên dữ liệu thật. Shares instant phải dương và có lineage; shares thiếu giữ unresolved. Events chỉ được dùng khi effective date và known_at cho phép; merger/delisting thiếu terms không giả làm mất 100%.

## Contracts và compatibility

`HISTORY_SCHEMAS` là họ Arrow contracts v1 riêng, có metadata `frl.history_table`; không thay `DOMAIN_SCHEMAS` v1 hoặc pilot facts v2. Các bảng giữ record hash, entity/security IDs, provenance, revision IDs, UTC known_at/cutoff, date intervals và trường market trực tiếp. Full typed input/decision được giữ trong canonical JSON payload; số decimal giữ dạng text. Consumers phải chọn schema family qua metadata, không chỉ schema_version.

12 bảng: entities, securities, identifier_history, memberships, industry_history, filings, shares, prices, corporate_actions, evidence, audit, scope. Evidence table giữ revisions gốc; corporate_actions giữ normalized decisions theo cutoff. Identity definitions chưa đủ CIK vẫn nằm trong evidence payload và phải được đối chiếu trước scope thật.

Manifest v2 pin parent, research/execution hashes, source tree, Git revision, lockfile, Python version và output checksums. Content hashes loại run metadata. Publish dùng run mới và immutable Parquet primitives; checkpoint không sửa parent. Replay kiểm mọi output checksum và raw payload trước biến đổi, thiếu raw không fallback network. Provider exception text không được ghi vì có thể chứa contact.

## Gate limits

Fixture mode/prototype provenance luôn chặn approval. Live collection cần approved pilot và SEC contact; audit không cần contact nhưng vẫn kiểm pilot. Audit giữ completeness unknown khi không có reviewed independent evidence theo từng cutoff. Universe scope approved vẫn không tự cho phép performance: features/backtest/validation còn ở các stage sau.

Chưa có live source verification hoặc CI Windows/Linux được quan sát cho thay đổi này trước push. Hướng dẫn chạy và giới hạn import thủ công tại [historical universe guide](../guides/historical-universe.md).
