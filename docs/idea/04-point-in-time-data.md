# Thông tin được phép dùng

## Quy định

Tại ngày đánh giá t, chỉ sử dụng dữ liệu đã công bố và có thể tiếp cận trước cutoff tín hiệu. Thị trường Mỹ; nguồn fundamentals là SEC EDGAR dạng as-filed.

- Ngày công bố là `filed` date của filing trên EDGAR; fundamental gắn với ngày công bố, không chỉ ngày kết thúc kỳ kế toán.
- Báo cáo sửa đổi chỉ dùng từ ngày công bố bản sửa đổi; không ghi đè lịch sử bằng phiên bản mới nhất.
- Giá, phân ngành (Ken French 17) và universe membership phải phản ánh thông tin tại thời điểm đó.
- Giao dịch diễn ra sau cutoff với execution và chi phí xác định trước.

Ví dụ: 10-Q quý I kết thúc 31/3, filed 25/4 không được dùng ở ranking 31/3.

## Lịch hàng quý

Cadence hàng quý. Cutoff là ngày giao dịch cuối cùng của quý lúc 16:00 ET (giờ thị trường Mỹ); execution vào mở phiên giao dịch kế tiếp. Tại cutoff, dùng báo cáo mới nhất đã có của mỗi doanh nghiệp; không giả định mọi mã đã công bố cùng kỳ. Sample v1: 2010Q1–2025Q4.

Tuổi dữ liệu và quy tắc staleness theo [02](02-universe-factors-ranking.md): carry-forward tối đa 2 quý, quá hạn coi là không có.

Phân biệt period end, `filed` date, amendment date, availability tại nguồn giá và signal date. Nếu thiếu ngày công bố ở nguồn không phải EDGAR, giả định lag phải ghi rõ và phân tích độ nhạy; lag không đảm bảo point-in-time chính xác.

## Universe

Dựng universe từ danh sách filer của EDGAR theo thời gian (survivor-free): mã đã hủy niêm yết vẫn còn trong EDGAR. Không xây lịch sử chỉ từ mã còn sống hôm nay.

## Metadata cần lưu

- CIK, identifier ổn định và ticker.
- Reporting period, period end.
- `filed` date (publication), amendment date.
- Accession number, filing/version identifier và amendments.
- Value, units, currency (USD), source.
- Industry Ken French 17 và universe membership có hiệu lực theo thời gian.
- Listing/delisting và corporate actions.

Giữ raw data và lịch sử phiên bản để tái lập snapshots.

## Kiểm tra

- Không dùng filing sau cutoff hoặc restatements tương lai.
- Không xây lịch sử chỉ từ mã còn sống hôm nay.
- Delisting: khi mã biến mất và không có giá, giả định delisting return −100%; ghi rõ và phân tích độ nhạy.
- Xử lý dividends và splits cho return/execution bằng giá điều chỉnh.
- Không chuẩn hóa/chọn features bằng dữ liệu tương lai.
- Valuation dùng giá biết được tại cutoff; execution sau signal.
- Target và backtest cùng quy ước vào/ra lệnh.

## Nguồn

Thị trường Mỹ, tiền tệ USD. Fundamentals: SEC EDGAR (as-filed XBRL, companyfacts/submissions). Giá: yfinance/Stooq. Ngành: SEC SIC/Ken French (17 ngành). Factor và benchmark: Ken French Data Library.

Hạn chế: nguồn giá miễn phí thiếu mã delisted, nên survivorship và delisting return là xấp xỉ; ghi rõ trong báo cáo. Nguồn có thể nâng cấp sau.
