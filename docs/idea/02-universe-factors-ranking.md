# Universe, factors và ranking

## Universe và 100 mã

Tách universe đủ điều kiện nghiên cứu khỏi candidate pool khoảng 100 mã. Hard filters có thể gồm dữ liệu đầy đủ, lịch sử tối thiểu, thanh khoản, trạng thái niêm yết và điều kiện đầu tư; ngưỡng chưa chốt.

Pass/fail theo ngưỡng tạo số mã thay đổi. Muốn đúng 100 mã cần top-100 và quy tắc ties, thiếu ứng viên. Fundamental score nên tách khỏi hard filters.

Nếu lọc fundamentals tốt rồi mới ranking ngành, kết luận chỉ đại diện các mã vượt bộ lọc. Đề xuất đánh giá ngành trên universe đủ điều kiện, trình bày riêng tập ứng viên; nếu chỉ dùng 100 mã thì gọi rõ là sức hấp dẫn của tập ứng viên trong ngành.

## Bốn trục

| Trục | Câu hỏi | Chỉ số minh họa chưa chốt |
|---|---|---|
| Quality | Lợi nhuận/dòng tiền có chất lượng không? | ROIC/ROE, margins, cash flow so với earnings |
| Growth | Kinh doanh có cải thiện không? | Revenue/earnings growth, thay đổi margin |
| Financial Health | Bảng cân đối có vững không? | Leverage, interest coverage, liquidity |
| Valuation | Giá hấp dẫn so với fundamentals không? | Earnings yield, FCF yield, bội số phù hợp ngành |

Doanh nghiệp tốt chưa chắc là khoản đầu tư hấp dẫn tại mọi mức giá. Giữ chung bốn trục nhưng ratios phù hợp từng ngành, đặc biệt với ngân hàng.

## Thiết kế score đề xuất

1. Chốt định nghĩa và chiều tốt/xấu của chỉ số.
2. Xử lý missing, outliers, mẫu số âm/zero và staleness.
3. Chuẩn hóa bằng dữ liệu biết được tại thời điểm đánh giá.
4. Tổng hợp thành điểm từng trục.
5. Kết hợp điểm tổng hợp; equal-weight là baseline đề xuất, chưa chốt.

Phân biệt mức hiện tại và thay đổi theo thời gian; định nghĩa TTM, YoY, windows và seasonality.

## Ranking ngành

Báo cáo median scores, tỷ lệ mã vượt ngưỡng, dispersion và số mã; chốt aggregation/weighting để tránh vài mã chi phối.

Không chuẩn hóa tất cả scores trong từng ngành rồi lấy trung bình so ngành: có thể xóa khác biệt giữa ngành. Score so ngành và score chọn mã trong ngành cần thiết kế riêng. Khi ratios khác nhau giữa ngành, phải làm rõ tính tương đương của điểm.

Ranking bằng score; p-value không phải điểm hấp dẫn. Ngành chất lượng cao, cải thiện nhanh, định giá thấp và nhiều doanh nghiệp tốt là các khía cạnh riêng, nên giữ điểm từng trục trước khi gộp.
