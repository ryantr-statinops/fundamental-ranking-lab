# Universe, factors và ranking

## Universe và thứ tự tính

Universe mục tiêu là cổ phiếu phổ thông Mỹ trên NYSE/NASDAQ/AMEX tại cutoff. Loại ETF, fund, preferred, warrant, ADR và OTC. REIT niêm yết là nhóm có cổng riêng. Một doanh nghiệp chỉ có một share class: chọn ADV 20 phiên USD lớn nhất bằng dữ liệu biết tại cutoff; ties theo security identifier tăng dần. CIK là identifier filer, không thay thế security identifier.

Thứ tự: xác minh identity/listing/ngành và cổng nhóm → hard filters đầu tư → tính raw ratios/độ phủ → eligible universe → chuẩn hóa → composite → ranking. Không dùng composite làm điều kiện để xác định tập chuẩn hóa.

Mặc định nghiên cứu: ít nhất 8 quý báo cáo đã công bố; ADV 20 phiên ≥ 1 triệu USD; giá đóng cửa chưa điều chỉnh ≥ 1 USD; đủ 20 phiên giá/volume và đang niêm yết/giao dịch tại cutoff. Có giá đơn lẻ không đủ chứng minh listing. Thiếu dữ liệu hard filter thì loại và ghi lý do.

Top-100 theo score lõi chung, lấy hết ties tại vị trí 100, không làm tròn score trước chọn; dưới 100 lấy hết. Universe trống thì danh mục toàn tiền mặt và ranking không khả dụng.

## Factor dictionary lõi chung — mặc định cần pilot

Lõi tối thiểu dưới đây là đặc tả để kiểm chứng, chưa chứng minh tương đương trên mọi ngành. General và Utils cũng phải qua audit; không mặc định Finan tương đương vì cùng tên ratio. Không thêm/bớt ratios theo kết quả returns.

Ký hiệu: NI = net income thuộc common shareholders; E = common equity; A = total assets; D = interest-bearing debt; M = tổng vốn hóa common share classes của doanh nghiệp tại cutoff. Flow là TTM; stock là cuối kỳ mới nhất. Average A/E là trung bình hai đầu khoảng TTM; không cộng dồn stock.

| Trục / ratio | Công thức | Chiều tốt | Period / đơn vị | Tag đầu vào us-gaap và fallback |
|---|---|---|---|---|
| Quality / ROA | NI / average A | cao | TTM / pure | NetIncomeLossAvailableToCommonStockholdersBasic; Assets |
| Quality / ROE | NI / average E | cao | TTM / pure | NI như trên; StockholdersEquity trừ PreferredStockValue |
| Growth / revenue | Revenue_TTM / Revenue_TTM_lag4 − 1 | cao | YoY TTM / pure | RevenueFromContractWithCustomerExcludingAssessedTax → Revenues → SalesRevenueNet |
| Growth / earnings | NI_TTM / NI_TTM_lag4 − 1 | cao | YoY TTM / pure | NI như trên |
| Financial Health / equity ratio | E / A | cao | instant / pure | E và Assets như trên |
| Financial Health / debt ratio | D / A | thấp | instant / pure | LongTermDebtCurrent + LongTermDebtNoncurrent + ShortTermBorrowings; Assets |
| Valuation / E/P | NI / M | cao | TTM + cutoff / pure | NI; common shares từng class × giá cutoff |
| Valuation / B/P | E / M | cao | instant + cutoff / pure | E; M như trên |

Tag là ứng viên mapping có thứ tự ưu tiên, không bảo đảm mọi doanh nghiệp khai báo cùng tag. Chỉ fallback khi cùng scope, unit, period và ý nghĩa. NI fallback NetIncomeLoss trừ preferred dividends khi các thành phần đã xác minh; E fallback từ total equity chỉ khi chứng minh không có preferred. Không coi thành phần thiếu bằng 0 nếu filing không xác nhận không có. Debt phải tránh cộng trùng current debt/short-term borrowing; không xác minh được thì missing. Với M, không nhân giá một class với toàn bộ shares khác class; thiếu class data thì valuation missing. Shares dùng số lưu hành instant đã công bố, không dùng weighted-average diluted shares của EPS; lưu ngày shares và giá.

Mẫu số ≤ 0 là undefined, gồm nền YoY ≤ 0; ghi cờ negative_base. Tử số âm vẫn giữ nếu có ý nghĩa (NI âm tạo ROA/ROE/E/P âm). Raw USD phải cùng currency/unit; không tự trộn IFRS hoặc foreign currency. Không thay tăng trưởng từ nền âm bằng tỷ lệ giả. Growth dùng YoY; ba trục khác dùng level. Thay đổi level và gia tốc growth là phân tích phụ, không có level/change 50/50 trong score chính.

## Score đặc thù và cổng nhóm

Các ratios dưới đây là backlog phân tích, chưa được vào score nếu chưa hoàn thiện dictionary như lõi chung (công thức/tag/fallback/period/direction/missing) và khóa version trước tính kết quả. Score đặc thù chưa đạt cổng là unavailable, không tự dùng block khác thay thế.

| Nhóm | Checklist trước kích hoạt |
|---|---|
| General | gross/operating margin, CFO/NI, FCF growth/yield, net debt/EBITDA, interest coverage, current ratio, D/E, EV/EBITDA; xác minh capex, debt, EV và earnings âm |
| Utils | ROE, operating margin, CFO/NI, revenue/EPS/dividend growth, coverage, leverage và yields; xác minh capex, regulated debt và dividend history |
| Bank (SIC 60xx) | ROE/ROA, net margin, equity/assets, loan/deposit, earnings/revenue growth, E/P/B/P/dividend yield; chốt cách đo revenue và ý nghĩa leverage |
| Insurance (63xx) | ROE, equity/assets, earnings/premium growth, yields; combined ratio chỉ áp cho nghiệp vụ phù hợp và có claims/expenses/premiums nhất quán |
| REIT/real estate (65xx, 6798) | xác minh thực sự là REIT hay real estate; FFO/assets/margin, leverage, coverage, growth, P/FFO/yields; không coi NI + toàn bộ depreciation − gains là FFO đã chuẩn hóa |
| Other Financials | SIC Finan còn lại cần phân loại nghiệp vụ và dictionary riêng; không tự ánh xạ sang bank/general |

Mỗi nhóm phải chứng minh ratios lõi có cùng ý nghĩa, raw facts truy nguyên và độ phủ trước khi vào ranking liên ngành. Thất bại thì giữ ngoài primary universe, báo rõ phạm vi bị loại. Trong Finan, checklist từng sub-block độc lập; không kích hoạt cả ngành khi chỉ một sub-block đạt. Mapping SIC dùng bảng Ken French có version; override 6798 vào REIT trước kiểm tra Other Financials.

## Missing và chuẩn hóa

- Trục hợp lệ khi ≥ 50% số ratios lõi đã khóa có giá trị; composite cần ≥ 3/4 trục. Với 2 ratios/trục, 1 ratio hợp lệ đủ cho trục. Báo cấu hình độ phủ để nhận diện selection bias.
- Structural N/A không tự bị loại khỏi mẫu số độ phủ lõi để “đạt cổng”; cần kiểm chứng lại thiết kế nhóm. Trong score đặc thù, mẫu số là bộ ratios áp dụng đã khóa cho nhóm.
- Temporal missing: dùng phiên bản mới nhất đã biết. Carry-forward tối đa 2 quý lịch kể từ cutoff đầu tiên giá trị có thể dùng, đồng thời period end không quá 270 ngày trước cutoff; quá một giới hạn thì missing. Amendment không đặt lại tuổi period end. Không carry growth sang kỳ mới với nhãn period mới.
- Trong trục lấy trung bình ratios hợp lệ; composite lấy trung bình các trục hợp lệ, reweight đều. Không impute số giả; lưu missing reason, tuổi dữ liệu và reweight flags.
- Percentile goodness = (midrank − 1)/(n − 1), đảo chiều cho ratio thấp tốt; n = 1 cho 0,5, n = 0 unavailable. Lõi chuẩn hóa trên eligible universe cùng cutoff; score đặc thù trong nhóm nghiệp vụ đã khóa. Ties midrank. Scores thuộc [0,1].
- Sensitivity: winsorize 1/99 rồi z-score bằng cross-section cùng cutoff; không thay cấu hình chính dựa final test.

## Ranking ngành và output

Median composite lõi chung trên toàn eligible universe là điểm ngành; không dùng riêng candidate pool. Rank theo median cao trước, ties midrank. Không lấy trung bình scores đã chuẩn hóa riêng từng ngành để so ngành.

Báo cáo median từng trục, IQR, số eligible, tỷ lệ ratios hợp lệ, tỷ lệ đạt 3/4 trục trên tập đã qua hard filters đầu tư, tỷ lệ score ≥ median universe (breadth), số vào top-100 và thay đổi hạng/score. Mẫu số từng tỷ lệ phải xuất kèm. Ngành không có eligible member là unavailable và không nhận tilt. Quy mô thấp vẫn hiển thị kèm cờ, không tự suy ra độ tin cậy.

Trạng thái ở [06](06-open-decisions-references.md); thời gian ở [04](04-point-in-time-data.md).
