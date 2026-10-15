# Bảng tham số tổng hợp

Bảng tra cứu, không phải nguồn quy tắc độc lập. Trạng thái theo [06](06-open-decisions-references.md); định nghĩa nằm ở 01–05. “Mặc định” không nghĩa là tối ưu hoặc đã có dữ liệu.

## Thị trường, dữ liệu và thời gian

| Tham số | Giá trị / trạng thái | Nguồn |
|---|---|---|
| Thị trường / tiền tệ | Common stocks Mỹ / USD; đã chốt | 01, 02 |
| Sàn / loại trừ | NYSE/NASDAQ/AMEX; loại ETF/fund/preferred/warrant/ADR/OTC | 02 |
| Share class | Một class/doanh nghiệp, ADV20 USD cao nhất tại cutoff | 02 |
| Ngân sách | 0 USD; không tự dùng nguồn trả phí | 04 |
| Nguồn dự kiến | SEC EDGAR as-filed; yfinance/Stooq; chờ audit | 04 |
| Ngành | SIC lịch sử → Ken French 17, nhãn chính; mapping versioned | 02, 04 |
| Cutoff | Ngày giao dịch cuối quý 16:00 America/New_York | 04 |
| Date-only filing | Chỉ nhận ngày trước ngày cutoff | 04 |
| Horizon/execution | Next open → next open sau cutoff quý kế tiếp | 04 |
| Tín hiệu mục tiêu | 2010Q1–2025Q4; chờ audit | 03, 04 |
| Outcome cuối | Phiên mở đầu quý II/2026 | 04 |
| Warm-up | Trước 2010 đủ 8 quý và stock đầu kỳ cần thiết | 04 |
| Split | Research 2010–2019; validation 2020–2022; test 2023–2025 | 03 |
| Purge | Loại 2019Q4/2022Q4 vì outcome qua split; không thêm embargo tự động | 03 |
| Giá/event unresolved | Chặn primary performance sample liên quan; −100% chỉ stress | 04 |

## Universe, factors và ranking

| Tham số | Giá trị / trạng thái | Nguồn |
|---|---|---|
| Hard filters mặc định | ≥ 8 quý; ADV20 ≥ $1M; raw close ≥ $1; đủ 20 phiên; listing được xác minh | 02 |
| Eligibility | Hard filters + cổng nhóm + raw coverage trước chuẩn hóa | 02 |
| Lõi Quality | NI/average A, NI/average common E | 02 |
| Lõi Growth | Revenue TTM YoY, NI TTM YoY | 02 |
| Lõi Financial Health | Common E/A cao tốt, interest-bearing D/A thấp tốt | 02 |
| Lõi Valuation | NI/M, common E/M; M tổng common share classes | 02 |
| Dictionary/tag mapping | Mặc định cần pilot; scope/unit/period/fallback phải xác minh | 02 |
| Cấu trúc trục | Growth YoY; 3 trục còn lại level; không level/change 50/50 | 02 |
| Mẫu số ≤ 0 | Undefined; tử số âm giữ khi có ý nghĩa | 02 |
| Temporal carry | ≤ 2 quý từ first usable cutoff và period age ≤ 270 ngày | 02 |
| Structural missing | Không tự reweight lõi để vượt cổng; kiểm chứng nhóm | 02 |
| Độ phủ | ≥ 50% ratios/trục, ≥ 3/4 trục; reweight đều phần hợp lệ | 02 |
| Chuẩn hóa | Percentile midrank [0,1]; n=1: 0,5; n=0: unavailable | 02 |
| Equal-weight | Ratios hợp lệ trong trục và trục hợp lệ trong composite | 02 |
| Lõi chung dùng cho | So ngành, top-100 và trọng số | 01, 02 |
| Đặc thù dùng cho | Ranking/giải thích trong nhóm; chưa đủ dictionary thì unavailable | 02 |
| Cổng nhóm | General/Utils audit; Bank/Insurance/REIT/Other Financials kiểm chứng riêng | 02, 05 |
| Ranking ngành | Median lõi trên eligible universe; ties midrank | 02 |
| Breadth | Tỷ lệ composite ≥ median universe, xuất mẫu số | 02 |
| Candidate pool | Top-100 lõi, lấy hết ties; dưới 100 lấy hết | 02 |
| Robustness | Winsorize 1/99 + z-score; phân tích phụ | 02 |

## Portfolio và chi phí

| Tham số | Giá trị / trạng thái | Nguồn |
|---|---|---|
| Holdings | Candidate pool, không chọn subset 30/50; zero-score có thể zero-weight | 05 |
| Weight thô | s_i × [1 + λ × (2p_ngành − 1)] | 05 |
| λ | 0,5 primary; p_ngành [0,1], tốt nhất cao nhất | 05 |
| Caps | Ngành 20%, doanh nghiệp 5% NAV sau phí tại rebalance | 05 |
| Phân bổ | Water-filling theo a_i; không chuẩn hóa lại để phá caps | 05 |
| Cash | Phần dư, lợi suất 0%; NAV bao gồm cash | 05 |
| Empty/all-zero scores | Toàn tiền mặt | 05 |
| Rebalance | Đầy đủ tới target; thoát mã rời pool/mất eligibility | 05 |
| No-trade band | Hoãn | 05 |
| Chi phí primary | 10 bps một chiều × tổng giá trị mua/bán; entry và terminal exit có phí | 05 |
| Cost sensitivity | 0/25/50 bps; không cộng component fees trùng | 05 |
| Cap sensitivity | Ngành 15%/25%, doanh nghiệp giữ 5% | 05 |
| Vốn / impact / capacity | Chưa gắn vốn; hoãn component model và kết luận capacity | 05 |
| Accounting | Giải NAV sau phí tự tài trợ; stock + cash = 100% | 05 |

## Kiểm định và cổng nghiên cứu

| Tham số | Giá trị / trạng thái | Nguồn |
|---|---|---|
| Primary Q1 | Fama–MacBeth slope, OLS score + intercept + industry dummies | 03 |
| Primary Q2 | Gross spread tercile ngành, EW member rồi EW ngành | 03 |
| Primary Q3 | Net strategy trừ net eligible-universe EW | 03 |
| Baseline | Cùng lịch, accounting, phí; universe EW không caps chủ động | 03 |
| Ablations | Top-100 EW; score-weight λ=0; cùng caps/phí | 03 |
| Inference | Một phía α=0,05; BH family chính 3 tests, exploratory family riêng | 03 |
| HAC | Bartlett NW; floor(4 × (T/100)^(2/9)), tối đa T−1 | 03 |
| Bootstrap | Circular blocks 4 quý, 5000 lần, seed 20261015; không nối gap | 03 |
| Pilot | 40 doanh nghiệp × cutoff cuối năm 2012/2018/2022/2025 | 05 |
| Roster | 20 General + 4 mỗi nhóm Utils/Bank/Insurance/REIT/Other Financials | 05 |
| Manual check | ≥ 10 doanh nghiệp, 1 cutoff thực/mã, phủ 6 nhóm | 05 |
| Cổng nhóm | ≥ 3 doanh nghiệp có snapshot; ≥ 50% member snapshots đạt 3/4 trục; không mismatch trọng yếu | 05 |
| Audit universe | Cổng riêng trước primary backtest, không suy từ pilot | 04, 05 |
| Thành công nghiên cứu | Tái lập và kết luận cùng độ bất định; không bắt buộc return dương | 01, 03, 05 |
| Hoãn | ML/news/clustering, horizon khác, no-trade band, component impact | 01, 05 |

Thay đổi phải ghi lý do, version và cập nhật file nguồn cùng 06/07 trước mở final test. Scope/sample thay sau xem test chỉ được báo exploratory.
