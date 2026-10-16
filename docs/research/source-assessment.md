# Đánh giá nguồn dữ liệu — Stage 01

Trạng thái tại 2026-10-16: desk review kỹ thuật và fixture checks đã thực hiện; **chưa ingestion nguồn thật**, vì vậy độ phủ lịch sử, tính đầy đủ của listing/delisting, độ đúng corporate actions và khả năng đối chiếu chưa được đo.

| Nguồn | Vai trò | Đã kiểm tra | Chưa xác minh |
|---|---|---|---|
| SEC submissions | Khám phá filing, accession, form, ngày nộp và lịch sử bổ sung | Đường dẫn API và parser fixtures | Contact chưa cấu hình; chưa tải submissions/history hay đo coverage cho roster |
| SEC companyfacts | Khám phá facts chuẩn theo entity | Mã yêu cầu JSON và cách lưu | Endpoint chưa gọi; API tổng hợp không thay thế mọi custom fact/context |
| SEC filing archive | Filing gốc và context XBRL | Parser fixture tổng hợp cho XML/inline XBRL, accession và date-only cutoff | Chưa tải/đối chiếu filing gốc của doanh nghiệp thật |
| yfinance | Daily OHLCV/actions để kiểm tra thanh khoản và định giá | Adapter truyền rõ điều chỉnh, actions, repair và timeout | Chưa gọi provider; chưa xác minh lịch sử, split convention, currency hoặc nhiều share classes |
| SEC entity/listing history và SIC | Membership, identifier, share class và ngành theo thời điểm | Roster chỉ có candidate URLs để bắt đầu điều tra | Chưa đủ historical evidence; không được coi universe là survivor-free |

Collector giới hạn SEC ở 2 requests/giây, timeout 30 giây, tối đa 5 attempts, tôn trọng `Retry-After`, dừng khi gặp 403 và ghi nhận 404. SEC công bố giới hạn truy cập cùng [developer resources](https://www.sec.gov/about/developer-resources); adapter kiểm tra [EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces). Adapter giá dùng tùy chọn của [yfinance `history`](https://ranaroussi.github.io/yfinance/reference/api/yfinance.Ticker.history.html), nhưng convention cần được đối chiếu trước khi dùng kết quả.

Kết luận hiện tại: interfaces và offline replay có thể kiểm tra; chưa có căn cứ kết luận bất kỳ nguồn/nhóm nào khả thi. Cập nhật bảng này sau ingestion và đối chiếu thật, kèm run ID, checksum, denominator và giới hạn.
