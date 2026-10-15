# Universe, factors và ranking

## Universe và 100 mã

Universe xác định tại từng thời điểm; lọc bằng hard filters để tạo universe đủ điều kiện, tách khỏi candidate pool. Hard filters là pass/fail và tách khỏi fundamental score.

Loại hard filter thuộc v1; ngưỡng cụ thể để mở ở [06](06-open-decisions-references.md):

- Dữ liệu đầy đủ cho các ratio bắt buộc.
- Lịch sử tối thiểu.
- Thanh khoản.
- Trạng thái niêm yết.
- Khả năng đầu tư.

Candidate pool khoảng 100 mã lấy top-100 theo **score so ngành** (chuẩn hóa trên toàn universe đủ điều kiện). Lấy hết các mã bằng điểm ở vị trí thứ 100, nên số lượng có thể vượt 100. Nếu universe đủ điều kiện ít hơn 100 mã, lấy hết và chấp nhận số lượng biến động.

Đánh giá ngành (Q2) tính trên universe đủ điều kiện, tách khỏi tập ứng viên. Nếu chỉ dùng 100 mã để so ngành thì phải gọi rõ là sức hấp dẫn của tập ứng viên trong ngành.

## Bốn trục

Doanh nghiệp tốt chưa chắc là khoản đầu tư hấp dẫn tại mọi mức giá. Giữ chung bốn trục; ratios phù hợp từng ngành.

### General (15 ngành còn lại)

| Trục | Ratios (level, TTM) | Chiều tốt |
|---|---|---|
| Quality | Gross margin, Operating margin, ROE, CFO/NetIncome | cao |
| Growth | Revenue growth, NetIncome growth, FCF growth, Δoperating margin | cao |
| Financial Health | Net debt/EBITDA, Interest coverage, Current ratio, Debt/Equity | EBITDA và D/E thấp; coverage và current ratio cao |
| Valuation | Earnings yield (E/P), FCF yield, EV/EBITDA, B/P | yield cao; EV/EBITDA thấp |

### Finan (Banks, Insurance, Other Financials) — tách sub-block bằng SIC

| Sub-block | Quality | Financial Health | Valuation |
|---|---|---|---|
| Ngân hàng (SIC 60xx) | ROE, ROA, net margin | equity/assets, loan/deposit | E/P, B/P, dividend yield |
| Bảo hiểm (SIC 63xx) | ROE, combined ratio | equity/assets | E/P, B/P, dividend yield |
| REIT/real estate (SIC 65xx, 6798) | FFO/assets, FFO margin | Net debt/EBITDA, interest coverage | P/FFO, dividend yield, EV/EBITDA |

Net debt/EBITDA và interest coverage không áp dụng cho ngân hàng và bảo hiểm.

### Utils

| Trục | Ratios |
|---|---|
| Quality | ROE, Operating margin, CFO/NetIncome |
| Growth | Revenue growth, EPS growth, dividend growth |
| Financial Health | Net debt/EBITDA, interest coverage |
| Valuation | E/P, EV/EBITDA, dividend yield, B/P |

### Cấu trúc và xử lý

Mỗi trục gồm hai nhóm: level (TTM, 4 quý) và change (YoY, so cùng quý năm trước). Trong mỗi nhóm, các chỉ số equal-weight nội bộ; điểm trục là trung bình hai nhóm theo tỷ lệ 50/50. Change tính trên chỉ số gốc rồi mới chuẩn hóa. TTM và YoY giúp tránh seasonality.

Ratios tự tính từ EDGAR XBRL. REIT xấp xỉ FFO = Net Income + depreciation − gains; bỏ nếu thiếu. Ratio thiếu áp dụng missing policy ở phần "Thiết kế score".

## Thiết kế score

1. Chốt định nghĩa và chiều tốt/xấu của chỉ số.
2. Xử lý missing, outliers, mẫu số âm/zero và staleness.
3. Chuẩn hóa bằng dữ liệu biết được tại thời điểm đánh giá.
4. Tổng hợp thành điểm từng trục (level/change 50/50).
5. Kết hợp điểm tổng hợp; equal-weight cả trong trục và giữa bốn trục.

Chuẩn hóa: percentile rank là chính trên cross-section tại cutoff. Đối chiếu độ bền bằng winsorize 1/99 rồi z-score.

Hai score tách biệt:

- **Score so ngành:** chuẩn hóa trên toàn universe đủ điều kiện; dùng để rank ngành và chọn top-100.
- **Score trong ngành:** chuẩn hóa riêng trong từng ngành; dùng để rank mã trong ngành.

### Xử lý missing

Phân biệt hai loại thiếu:

- **Structural** (không áp dụng theo ngành): dùng lõi chung áp dụng mọi ngành cộng block riêng theo ngành; ratio không áp dụng bị loại khỏi trục và reweight phần còn lại.
- **Temporal** (thiếu theo thời gian): carry-forward giá trị đã công bố mới nhất trong tối đa 2 quý; nếu vẫn thiếu thì bỏ ratio đó và reweight; không impute giá trị giả. Mẫu số âm/zero coi là không xác định.

Ngưỡng độ phủ: trục có điểm nếu còn ít nhất 50% số ratio áp dụng có giá trị; score tổng hợp cần ít nhất 3/4 trục, dưới ngưỡng thì loại mã. Missing và N/A phân biệt rõ trong dữ liệu. Báo cáo độ phủ từng mã/ngành và đánh dấu mã dùng carry-forward hoặc reweight.

## Ranking ngành

Xếp hạng bằng score; p-value không phải điểm hấp dẫn. Median equal-weight là đại lượng chính; giữ điểm từng trục trước khi gộp.

Báo cáo:

- Sức mạnh: median composite score.
- Chi tiết: median bốn trục riêng.
- Đồng thuận: dispersion (IQR hoặc std của member scores).
- Breadth: tỷ lệ mã trên median universe và tỷ lệ mã đạt ngưỡng chất lượng (theo phân vị, chốt con số sau).
- Độ phủ: tỷ lệ ratio hợp lệ; tỷ lệ mã đủ 3/4 trục.
- Quy mô: số mã eligible và số mã lọt top-100.
- Động lượng: thay đổi hạng và median score so quý trước.
- Ổn định: rank stability qua các quý (tùy chọn).

Không chuẩn hóa tất cả scores trong từng ngành rồi lấy trung bình so ngành: có thể xóa khác biệt giữa ngành. Score so ngành và score trong ngành thiết kế riêng. Khi ratios khác nhau giữa ngành, phải làm rõ tính tương đương của điểm.

Ngành chất lượng cao, cải thiện nhanh, định giá thấp và nhiều doanh nghiệp tốt là các khía cạnh riêng.

## Điểm mở

Ngưỡng hard filters, hệ thống và cấp ngành, bộ ratio cụ thể, và con số ngưỡng chất lượng để mở ở [06](06-open-decisions-references.md).
