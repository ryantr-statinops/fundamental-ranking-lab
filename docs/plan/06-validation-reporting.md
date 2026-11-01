# Stage 06 — Validation, inference và báo cáo

Trạng thái: **Đã triển khai baseline validation & statistical inference engine**. Phụ thuộc: [stage 05](05-portfolio-backtest.md), dữ liệu/feature/ranking gates đã đạt. Quy tắc gốc: [hypothesis validation](../idea/03-hypothesis-validation.md).

### Tiến độ implementation:
- [x] Xây dựng Data Contracts & Parquet Schemas cho Evaluation (`FamaMacBethRecord`, `TercileSpreadRecord`, `ExcessReturnRecord`, `HypothesisSummary`).
- [x] Hiện thực hàm tính Forward Gross Returns open-to-open giữa các mốc cutoff.
- [x] Hiện thực kiểm định Q1: Cross-Sectional OLS Fama–MacBeth kiểm soát biến giả ngành.
- [x] Hiện thực kiểm định Q2: Industry Top-Minus-Bottom Tercile Spread (cutpoints linear 1/3 và 2/3).
- [x] Hiện thực kiểm định Q3: Net Strategy Return vs Net Universe Equal-Weight Baseline sau chi phí 10 bps.
- [x] Hiện thực suy luận thống kê Newey–West HAC (Bartlett kernel tự động chọn lag) và hiệu chỉnh đa giả thuyết Benjamini–Hochberg FDR control ($\alpha=0.05$).
- [x] Tích hợp lệnh CLI `uv run frl evaluate --input-ranking <path>` xuất các bảng Parquet kiểm định `fama_macbeth.parquet`, `industry_terciles.parquet`, `excess_returns.parquet`, `hypothesis_summary.parquet`.
- [x] Smoke check thành công trên run thật của Stage 01.

## Mục tiêu và đầu vào
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
