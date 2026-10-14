# Thông tin được phép dùng

## Quy định

Tại ngày đánh giá t, chỉ sử dụng dữ liệu đã công bố và có thể tiếp cận trước cutoff tín hiệu. Fundamental gắn với ngày công bố, không chỉ ngày kết thúc kỳ kế toán. Báo cáo sửa đổi chỉ dùng từ ngày công bố bản sửa đổi; không ghi đè lịch sử bằng phiên bản mới nhất. Giá, phân ngành và universe membership phải phản ánh thông tin tại thời điểm đó. Giao dịch diễn ra sau cutoff với execution và chi phí xác định trước.

Ví dụ: báo cáo quý I kết thúc 31/3, công bố 25/4 không được dùng ở ranking 31/3.

## Lịch hàng quý

Chốt ngày rebalance, cutoff timestamp và timezone. Tại cutoff, dùng báo cáo mới nhất đã có của mỗi doanh nghiệp; không giả định mọi mã đã công bố cùng kỳ. Ghi nhận tuổi dữ liệu và quy tắc staleness.

Phân biệt period end, publication date, amendment date, availability tại vendor và signal date. Nếu thiếu ngày công bố, giả định lag phải ghi rõ và phân tích độ nhạy; lag không đảm bảo point-in-time chính xác.

## Metadata cần lưu

- Identifier ổn định và ticker.
- Reporting period, period end.
- Publication/availability timestamp.
- Filing/version identifier và amendments.
- Value, units, currency, source.
- Industry và universe membership có hiệu lực theo thời gian.
- Listing/delisting và corporate actions.

Giữ raw data và lịch sử phiên bản để tái lập snapshots.

## Kiểm tra

- Không dùng publication sau cutoff hoặc restatements tương lai.
- Không xây lịch sử chỉ từ mã còn sống hôm nay.
- Xử lý delisting, dividends và splits cho return/execution.
- Không chuẩn hóa/chọn features bằng dữ liệu tương lai.
- Valuation dùng giá biết được tại cutoff; execution sau signal.
- Target và backtest cùng quy ước vào/ra lệnh.

Nguồn dữ liệu và mức hỗ trợ point-in-time chưa chốt.
