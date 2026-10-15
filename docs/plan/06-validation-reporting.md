# Stage 06 — Validation, inference và báo cáo

Trạng thái: chưa bắt đầu. Phụ thuộc: [stage 05](05-portfolio-backtest.md), dữ liệu/feature/ranking gates đã đạt. Quy tắc gốc: [hypothesis validation](../idea/03-hypothesis-validation.md).

## Mục tiêu và đầu vào

Trả lời Q1–Q3 bằng đánh giá ngoài mẫu có thể tái lập, tách primary khỏi exploratory. Đầu vào: audited scope, feature/ranking versions, engine tests, research/validation runs và primary config. Chưa được gọi performance test là unseen nếu đã xem hoặc dùng chọn cấu hình.

## Trình tự nghiên cứu

1. Sample mục tiêu tín hiệu 2010Q1–2025Q4, outcome tới open Q2/2026; research 2010–2019, validation 2020–2022, test 2023–2025. Purge 2019Q4/2022Q4 do outcome vượt split; áp tương tự nếu scope audit thay đổi. Primary test tối đa 12 quý.
2. Dùng research/validation kiểm tra đúng đắn và độ bền. Mọi thay đổi factor/tag/eligibility/weights phải có lý do, version, cập nhật idea và rerun affected stages; không tuning bằng test.
3. Freeze study manifest trước mở test: data/scope/group/schema/config/factor hashes, git/lock, dates/purge, cost, caps/λ, primary tests, secondary registry, missing handling và random seed. CLI mặc định từ chối split test nếu không có manifest.
4. Chạy stage 05 với `--split test --study-manifest <file>`; mọi lần xem/rerun ghi audit. Rerun cùng inputs chỉ tái lập; thay cấu hình sau xem test chuyển nghiên cứu mới thành exploratory và cần sample mới để xác nhận.
5. Đánh giá và xuất cả kết quả âm/unavailable. Gate unresolved data chặn primary performance, không chỉ gắn disclaimer vào biểu đồ vẫn mang nhãn xác nhận.

## Kiểm định và baselines

Primary: Q1 quarterly OLS forward gross return ~ score + intercept + industry dummies (drop một dummy), mean slopes; Q2 gross top-minus-bottom tercile ngành, EW member rồi EW ngành; Q3 net strategy trừ net universe EW. Q1 singular/no residual degrees of freedom hoặc Q2 <3 ngành/empty bucket là unavailable.

Tercile cutpoints phân vị tuyến tính 1/3 và 2/3 (NumPy method=linear), bottom ≤ q1/top > q2, giữ ties. Dùng cùng convention trong exploratory terciles; bỏ nhóm cổ phiếu <3 members. Trước triển khai ghi convention này vào study manifest, không thay theo spread.

NW Bartlett lag floor(4×(T/100)^(2/9)), tối đa T−1; one-sided α=0,05. Temporal gaps không được coi là liền kề: HAC lags theo quarter index thực; nếu estimator chưa hỗ trợ missing spacing đúng thì báo inference unavailable, không compress time. T<3 hoặc zero/invalid SE thì p/CI unavailable. Báo effect size, T, lags, one-sided raw p và BH-adjusted p cho family chính 3 slots; slot unavailable dùng p=1 chỉ để correction, giữ p thực là unavailable. Holm bổ trợ khi không biện minh được dependency cho BH.

Bootstrap circular moving blocks 4 quý/5000 iterations, seed 20261015, percentile 95% CI hai phía; không vượt gap, segments ngắn <4 không bootstrap, báo sample bootstrap thực. Khóa cách chọn blocks theo segment trước chạy: resample từng segment đủ dài tới độ dài gốc rồi gộp statistic; không tạo adjacency giữa segments.

Baseline chính universe EW, cùng lịch/fees/events, không caps chủ động. Ablations top-100 EW và score-weight λ=0 dùng cùng caps/cash engine. Cash-matched diagnostic giữ cash fraction strategy tại rebalance rồi đầu tư phần còn lại vào universe EW, tự tính phí theo trades của chính nó. Secondary registry gồm IC, buckets, ablations, z-score, caps ngành 15%/25%, cost 0/25/50; BH riêng các secondary hypotheses đã đăng ký, không hiệu chỉnh vào descriptive metrics không có p-value.

## CLI, outputs và kiểm tra nghiệm thu

CLI dự kiến: `uv run frl evaluate --config configs/research.toml --input-run <backtest_id> --study-manifest <file>`. Output gồm metrics/quarterly series/test tables Parquet+CSV, HTML/Markdown report, PNG figures và provenance bundle. Report hiển thị scope, T, unavailable/blockers, cash/concentration và giới hạn power trước diễn giải ý nghĩa.

- Synthetic slopes/spreads kiểm tra sign, dummy encoding, singular regression, tercile ties, one-sided p conversion và reference NW/BH/Holm calculations.
- Bootstrap deterministic với seed, không nối gaps; primary/secondary family counts đúng khi test unavailable. Không báo p cho nhóm không fit.
- Baselines cùng accounting; report đối soát NAV/fees/cash với ledger, CAGR/Sharpe/IR/drawdown đúng frequency. Quarterly Sharpe dùng excess risk-free cùng kỳ, IR dùng active return; thiếu RF không gắn nhãn Sharpe cho mean raw return/std. Std=0 thì metric unavailable.
- Report gồm kết quả âm và mọi registered variant, không chỉ cấu hình tốt nhất; HTML/Markdown không có bảng rỗng bị hiểu thành pass. Data blockers làm conclusion trạng thái insufficient_data.
- Replay study manifest cho kết quả nghiệp vụ tương đương. Bàn giao kết luận positive/negative/inconclusive/insufficient_data có lý do; hoàn thành nghiên cứu không phụ thuộc alpha dương.

Nguồn triển khai: [statsmodels HAC](https://www.statsmodels.org/stable/generated/statsmodels.stats.sandwich_covariance.cov_hac.html), [multipletests](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html). Reference implementation không miễn kiểm tra giả định spacing/sample nhỏ. Chuyển [stage 07](07-quarterly-operation.md) khi có kết luận phù hợp; vận hành chỉ tạo research artifacts, không tự cho phép giao dịch vốn thật.
