# Quyết định và nguồn

## Cách đọc trạng thái

- **Đã chốt:** quyết định về mục tiêu/phạm vi hoặc quy tắc đã được chọn; thay đổi cần lý do và version trước đánh giá mới.
- **Mặc định nghiên cứu:** giá trị cụ thể để triển khai, chưa được chứng minh tối ưu; chỉ sửa trước khóa test và ghi tác động.
- **Chờ kiểm chứng dữ liệu:** chưa được phép xem như khả dụng/đã đạt; phải có bằng chứng cổng.
- **Hoãn:** ngoài primary v1; không tự thêm vào implementation.

File nội dung 01–05 là nguồn quy tắc; file 07 chỉ tổng hợp. Thay đổi cập nhật đồng thời nội dung, bảng này và bảng tham số. Không biến đề xuất thành quyết định đã chốt.

## Sổ quyết định

| Vấn đề | Trạng thái / giá trị | Lý do và điều kiện thay đổi |
|---|---|---|
| Mục tiêu v1 | Đã chốt: ranking mã/ngành, portfolio, inference; nghiên cứu có thể âm | Trả lời Q1–Q3; đổi scope phải ghi lại câu hỏi |
| Thị trường/ngân sách | Đã chốt: Mỹ, USD, dữ liệu miễn phí | Không tự mua dữ liệu; thiếu thì giới hạn kết luận hoặc dừng ở feasibility |
| Nguồn | Chờ kiểm chứng: EDGAR as-filed, yfinance/Stooq, SIC/Ken French | Provider có API không bảo đảm đủ lịch sử; qua pilot và audit |
| Universe | Đã chốt: common stocks NYSE/NASDAQ/AMEX, exclusions và một class/doanh nghiệp theo 02 | Tránh đếm lặp; membership lịch sử phải có bằng chứng |
| Hard filters | Mặc định: ≥ 8 quý, ADV20 ≥ $1M, giá ≥ $1, đủ 20 phiên | Chỉ sửa theo audit trước xem performance |
| Ngành | Đã chốt: SIC lịch sử → Ken French 17, nhãn chính | Không dùng nhãn hiện tại backfill |
| Finan/REIT và tính tương đương lõi | Chờ kiểm chứng từng nhóm | Dictionary, meaning, coverage và filing reconciliation theo 02/05 |
| Hai score | Đã chốt: lõi cho so ngành/top-100/weights; đặc thù trong nhóm | Không trộn composites khác nghĩa |
| Lõi ratios/tags | Mặc định: 8 ratios trong 02; mapping chờ pilot | Không fallback sai context hoặc đổi theo returns |
| Score đặc thù | Chờ kiểm chứng: checklist 02, chưa đủ dictionary thì unavailable | Không tự dùng general cho nhóm khác |
| Trục/chuẩn hóa | Mặc định: Growth YoY; ba trục level; percentile, equal-weight | Change và z-score chỉ phân tích phụ |
| Missing/coverage | Mặc định: ≥ 50% ratios/trục, ≥ 3/4 trục; carry ≤ 2 quý và period age ≤ 270 ngày | Structural incompatibility chặn nhóm; không impute để qua cổng |
| Ranking ngành | Đã chốt: median lõi trên eligible universe | Không dùng candidate pool làm đại diện ngành |
| Candidate/holdings | Đã chốt: top-100 gồm ties, dưới 100 lấy hết | Không còn tầng chọn 30/50 |
| Lịch | Đã chốt: cutoff 16:00 America/New_York cuối quý, next open execution | Date-only chỉ từ ngày trước cutoff; đổi lịch phải đổi target/accounting |
| Delisting/giá thiếu | Đã chốt: phân loại và xác minh; unresolved chặn primary | −100% chỉ stress, không thay giá thực |
| Construction | Đã chốt: score-weight + tilt; λ = 0,5 mặc định | Công thức/water-filling ở 05; không tuning bằng final test |
| Caps | Mặc định: ngành 20%, doanh nghiệp 5% NAV tại rebalance | Tham chiếu methodology không chứng minh tối ưu; sensitivity 15%/25% ngành |
| Cash | Đã chốt: giữ phần không phân bổ, không mở rộng pool | Cash tính vào NAV/performance; lợi suất 0% mặc định |
| Chi phí | Mặc định: 10 bps một chiều, sensitivity 0/25/50 | Chưa gắn vốn; không kết luận impact/capacity |
| Baseline | Đã chốt: eligible universe equal-weight, cùng lịch/phí | Ablations top-100 EW và không tilt có cùng caps |
| Inference | Đã chốt: Q1 slope, Q2 spread ngành, Q3 net excess; một phía α 0,05 | Family chính 3 tests; phụ riêng, không nâng exploratory thành primary |
| HAC/bootstrap | Mặc định: NW lag công thức, blocks 4 quý, 5000 lần, seed cố định | Báo N nhỏ/missing; không khẳng định power |
| Sample/split | Chờ audit: tín hiệu 2010Q1–2025Q4; research 2010–2019 / validation 2020–2022 / test 2023–2025 | Outcome đến open Q2/2026; purge 2019Q4 và 2022Q4, scope khóa trước returns |
| Pilot | Đã chốt: 40 doanh nghiệp × 4 cutoff, kiểm tra filing ≥ 10 | Cổng nhóm và audit toàn universe tách biệt, chi tiết 05 |
| ML/news/clustering, no-trade band, component cost | Hoãn | Chỉ mở sau baseline; cần spec và đánh giá riêng |

## Nguồn và giới hạn suy luận

- [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces): submissions và XBRL, giới hạn taxonomy/context của API aggregate; không tự cung cấp lịch sử security universe hoàn chỉnh.
- [SEC developer resources](https://www.sec.gov/about/developer-resources): truy cập filings và lịch sử nguồn.
- [SEC financial statement datasets](https://www.sec.gov/dera/data/financial-statement-data-sets): nguồn as-filed bổ trợ; vẫn cần version/availability audit.
- [Ken French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html): bảng SIC/17 industries và factors; lưu version mapping, không coi industry portfolio returns là benchmark strategy tương đương.
- [yfinance](https://github.com/ranaroussi/yfinance), [Stooq](https://stooq.com/): nguồn giá dự kiến; coverage delisted/events cần audit.
- [S&P Quality Indices Methodology](https://www.spglobal.com/spdji/en/documents/methodologies/methodology-sp-quality-indices.pdf), 09/2025, trang 8/11: tiền lệ top-100 và security cap 5% có điều kiện, GICS sector cap 40%. Không chứng minh cap Ken French 20% tối ưu.
- [MSCI Quality Advanced Select Methodology](https://www.msci.com/indexes/documents/methodology/4_MSCI_Quality_Advanced_Select_Indexes_Methodology_20230801.pdf), 02/2025: ví dụ kiểm soát sector tương đối parent; khác quy tắc tuyệt đối v1.
- [Statsmodels HAC](https://www.statsmodels.org/stable/generated/statsmodels.stats.sandwich_covariance.cov_hac.html), [multipletests](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html): công cụ triển khai inference; không thay giả định thống kê.
- [LightGBM parameters](https://lightgbm.readthedocs.io/en/latest/Parameters.html): chỉ tham khảo giai đoạn ML hoãn.

Các nguồn không chứng minh factors tạo alpha. Trạng thái hiện tại: thiết kế nghiên cứu đã xác định; chưa thực hiện pilot, audit, pipeline hoặc backtest.

## Lịch sử thay đổi

2026-10-15: thay khẳng định spec hoàn tất bằng các cổng; tách lõi/đặc thù, cụ thể hóa universe/PIT, portfolio top-100 + tilt, caps 20%/5%, cash và chi phí bps; sửa family kiểm định/split. Thay đổi theo review trước khi triển khai hoặc xem kết quả; mọi hiệu quả còn là giả thuyết.
