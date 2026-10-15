# Hypothesis testing và đánh giá

## Ba kiểm định chính

Horizon từ mở phiên sau cutoff tới mở phiên sau cutoff quý kế tiếp. Score là lõi chung; universe và cổng nhóm theo [02](02-universe-factors-ranking.md). Các giả thuyết một phía H0: E[đại lượng] ≤ 0; H1: > 0.

| ID | Đại lượng chính | Định nghĩa |
|---|---|---|
| Q1 | Fama–MacBeth slope | Mỗi quý OLS forward total return theo score, intercept và industry dummies (bỏ một dummy); mỗi doanh nghiệp một quan sát, equal-weight |
| Q2 | Top-minus-bottom ngành | Chia các ngành có eligible member thành terciles theo median score; return ngành equal-weight member, mỗi phía equal-weight ngành |
| Q3 | Net excess return | Net return danh mục score-weight + tilt trừ net return universe equal-weight |

Q1 dùng score liên tục, không phải kiểm định chênh lệch tercile. Không fit nếu score không có biến thiên độc lập với industry dummies hoặc không còn bậc tự do; ghi quý unavailable và lý do, không điền slope 0. Q2 cần ít nhất 3 ngành; ties tại ranh giới giữ cùng bucket bằng cutpoints phân vị 1/3 và 2/3 (bottom ≤ q1, top > q2); nếu phía nào trống thì quý unavailable. Không tách ties tùy ý để tạo spread.

Returns Q1/Q2 là gross total returns để đo tín hiệu; spread là công cụ nghiên cứu, không giả định giao dịch short. Q3 là hiệu quả thực thi sau phí/cash. Không xem mã cùng quý là các quan sát thời gian độc lập.

## Inference và phân tích phụ

Kiểm định trung bình chuỗi slope/spread/excess bằng Newey–West, Bartlett kernel; lag mặc định floor(4 × (T/100)^(2/9)), chặn tại T−1. Báo T và lag thực. Block bootstrap bổ trợ theo thời gian, circular moving blocks 4 quý, 5000 lần, seed 20261015; báo percentile 95% CI hai phía. Không nối các đoạn sample bị thiếu như liên tiếp khi tạo blocks; đoạn không đủ 4 quý không bootstrap, ghi rõ.

Family chính chỉ gồm Q1/Q2/Q3, BH với α = 0,05; raw và adjusted p-value đều công bố. Không loại test unavailable để thu nhỏ family: giữ slot với p = 1 cho hiệu chỉnh và gắn nhãn chưa kiểm định, không coi là bằng chứng H0 đúng. BH có giả định phụ thuộc; báo Holm bổ trợ nếu cấu trúc phụ thuộc không được biện minh. Không diễn giải BH như bảo đảm độc lập với giả định.

Phụ: Spearman Rank IC trong ngành, sign test, monotonicity buckets, top-minus-bottom tercile cổ phiếu trong ngành (cap-weight với market cap point-in-time); z-score, cap/chi phí sensitivity và ablation. Đăng ký manifest các phép phân tích phụ trước chạy; hiệu chỉnh BH riêng toàn family phụ được đăng ký và ghi exploratory, không đưa kết quả đẹp lên primary. Nhóm ngành < 3 mã bỏ phân tích tercile cổ phiếu, vẫn công bố coverage.

Net excess không tự là risk-adjusted alpha. Factor regression Ken French chỉ bổ trợ khi đồng bộ frequency và risk-free rate, không dùng tên alpha cho excess đơn giản.

## Ngoài mẫu và khóa cấu hình

Khoảng tín hiệu mục tiêu 2010Q1–2025Q4, outcome đến phiên mở đầu quý II/2026. Research 2010–2019; validation 2020–2022; test 2023–2025. Không mô tả xấp xỉ 60/20/20 như split chính xác.

Purge observation nếu outcome kết thúc sau ranh giới split: loại tín hiệu 2019Q4 khỏi research và 2022Q4 khỏi validation vì exits sang năm sau. Theo cùng nguyên tắc xử lý sample thực sau audit; không thêm “embargo một quý” thứ hai mà không có lý do. Primary test tối đa 12 kỳ quý; công bố số kỳ thực và CI, không khẳng định đủ statistical power chỉ vì có nhiều mã.

Audit scope/sample theo dữ liệu trước xem performance; ghi manifest dates, exclusions, factor/tag version, universe/industry mapping, weights, costs, primary/secondary tests. Nếu phạm vi thay đổi sau khi đã xem test, kết quả mới là exploratory; muốn xác nhận cần dữ liệu chưa dùng.

Khóa factors, λ = 0,5, caps 20%/5%, top-100, chi phí và baseline trước mở final test. Validation kiểm tra feasibility/độ bền; thay đổi có lý do phải version lại, không tự chọn cấu hình có return đẹp nhất. Không tuning trên final test.

## Baselines và attribution

Baseline chính: mọi doanh nghiệp eligible cùng cutoff, equal-weight, cùng lịch open-to-open, xử lý corporate actions, chi phí một chiều và terminal exit. Baseline này không áp caps chủ động của strategy; báo khác biệt concentration và cash để tránh quy hết hiệu quả cho score.

Ablations cùng candidate pool: top-100 equal-weight và score-weight không tilt (λ = 0), cùng caps/cost/cash algorithm để tách weighting và tilt. Báo thêm benchmark có tỷ lệ cash khớp strategy để nhận diện cash drag; không thay baseline chính. Sensitivity ngành 15%/25%, chi phí 0/25/50 bps không dùng chọn cấu hình bằng test.

## Metrics và diễn giải

Ranking: Rank IC, buckets, monotonicity, rank stability và độ phủ. Portfolio: gross/net/excess, CAGR mô tả, quarterly Sharpe/IR (annualize √4), maximum drawdown theo tần suất NAV thực có, turnover, cash, top-10, issuer/industry concentration và số mã hiệu dụng. Không gọi quarterly drawdown là daily drawdown. Inference: effect size, CI, raw/adjusted p, T, unavailable periods và data blockers.

Kết quả âm hoặc chưa đủ bằng chứng vẫn hoàn thành nghiên cứu nếu tái lập và báo trung thực. Nếu unresolved dữ liệu ngăn return đáng tin, chỉ hoàn thành feasibility, chưa hoàn thành backtest/inference. Không bác bỏ H0 không chứng minh vô dụng; significance không thay hiệu quả kinh tế hoặc quyết định sử dụng vốn.
