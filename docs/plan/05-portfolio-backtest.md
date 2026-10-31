# Stage 05 — Portfolio construction và backtest

Trạng thái: **Đã triển khai baseline portfolio construction & water-filling caps engine**. Phụ thuộc: dữ liệu audit [stage 02](02-historical-data-universe.md) và ranking [stage 04](04-ranking-baseline.md). Quy tắc gốc: [portfolio/accounting](../idea/05-portfolio-roadmap.md), [events](../idea/04-point-in-time-data.md).

### Tiến độ implementation:
- [x] Xây dựng Data Contracts & Parquet Schemas cho Portfolio (`TargetWeight`, `PortfolioHolding`, `RebalanceRecord`).
- [x] Hiện thực thuật toán tính Industry Percentile và hệ số Tilt $T_g = 1 + \lambda (2p_g - 1)$ với $\lambda = 0.5$.
- [x] Hiện thực thuật toán Water-Filling áp trần 5% doanh nghiệp, 20% ngành và giữ lại tiền mặt dư thừa (residual cash).
- [x] Đạt toàn bộ các kịch bản nghiệm thu kiểm thử (4 ngành x 25 mã -> 80% stocks/20% cash; 3 mã -> 15% stocks/85% cash; 5 ngành -> 100% stocks).
- [x] Hiện thực thuật toán Bisection giải phương trình tự tài trợ chi phí giao dịch $V^+ = V^- - c \sum |t_i V^+ - H_i^-|$ với phí 10 bps.
- [x] Tích hợp lệnh CLI `uv run frl portfolio --input-ranking <ranking_dir>` xuất `target_weights.parquet`.
- [x] Smoke run thành công trên ranking output thật của Stage 04.

## Mục tiêu và đầu vào
## Engine và accounting

CLI dự kiến: `uv run frl backtest --config configs/research.toml --input-run <ranking_id> --split research` (validation tương tự). Price/event run IDs nằm trong parent manifest; không tự lấy dữ liệu hiện tại.

Tại next open sau cutoff: mark vị thế cũ, xử lý event hiệu lực trước open rồi giao dịch target. Cho phép fractional shares cho mô phỏng normalized NAV; đây không phải broker execution. Giá raw, dividend vào cash khi được thanh toán, splits đổi shares/price basis, không cộng adjusted-return lần hai. Daily mark để phát hiện gaps/events; chỉ công bố daily drawdown nếu daily NAV đầy đủ. Nếu chỉ có quý thì gắn rõ frequency.

Phí primary 10 bps một chiều trên tổng buy+sell notionals; entry và terminal exit có phí. Giải V+=V−−c×Σ|t_i V+−H_i−| bằng bisection bracket [0,V−], tolerance tương đối NAV 1e−10; notional sau=t_iV+, cash=(1−Σt_i)V+. Không thu phí trên cash hoặc tính đôi fee. Kiểm tra residual, tự tài trợ, no negative cash/shares; terminal liquidation đặt targets 0.

Q1/Q2 gross forward returns có builder riêng nhưng cùng price/event conventions và open-to-open horizon, không dùng cổ phiếu adjusted series lẫn accounting. Net strategy so baseline dùng chung engine. Merger/recovery theo consideration thật; shares nhận bắt buộc giữ/sell theo idea và báo off-pool exposure. Không có executable open/exit/event info thì unresolved, chặn primary performance sample liên quan; không giả định −100% hoặc forward-fill qua event không rõ.

Return kỳ đo trước rebalance tiếp theo, phí entry thuộc kỳ bắt đầu, terminal fee thuộc kỳ cuối; lưu cashflows đủ đối soát, không mất phí ở ranh giới. Tái đầu tư dividends chỉ tại rebalance. Dùng normalized starting NAV=1; không đưa kết luận dollar capacity/market impact.

## Artifacts

Target weights trước/sau caps, orders/trades/fees ledger, shares/cash/event ledger, gross/net NAV và returns, unresolved registry, turnover, concentration, cap-binding/drift, effective stock count. Bàn giao cả input lineage và config hash; tách trạng thái accounting_checked/data_approved/performance_released, không có một cờ success che data blocker.

## Kiểm tra nghiệm thu

- 4 ngành ×25 mã raw weights bằng nhau → 80% stocks/20% cash; 5 ngành đủ mã → 100% stocks; 3 mã → ≤15% stocks; empty/all-zero → cash. Ties không bị cắt.
- Hand-computed entry, rebalance có cả buy/sell, partial cash và terminal exit với c=0/10/25/50 bps; V+ + phí = V−, stocks+cash=100%, weights không vượt caps sau phí.
- Split 2:1 không tạo gain, dividend không double count, merger cash/stock, bankruptcy có recovery và ticker reuse. Missing open/exit phải chặn kết luận, không tự dùng close.
- No-trade kỳ target bằng actual thì fee=0; drift không tự rebalance; phí tỷ lệ buy+sell, khác half-turnover.
- Replay pinned fixtures/inputs trùng ledger/NAV; strategy và EW baseline trên cùng target cho kết quả giống nhau. Các tests này phải đạt trước chạy performance thật.

Bàn giao engine và research/validation runs cho [stage 06](06-validation-reporting.md). Final-test run chỉ được kích hoạt khi stage 06 có frozen study manifest; stage 07 không phải triển khai giao dịch thực.
