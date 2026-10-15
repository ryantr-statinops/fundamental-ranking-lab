# Thông tin được phép dùng

## Publication, cutoff và execution

Chỉ dùng dữ liệu công bố và có thể tiếp cận trước hoặc đúng cutoff. Cutoff là 16:00 America/New_York ngày giao dịch cuối quý (DST theo timezone, không cố định UTC offset). Lưu timestamp nguồn, múi giờ gốc, bản UTC, acceptance/publication time và availability của nguồn nếu có. Kiểm chứng timestamp bằng filing header; không suy ra giờ từ filed date.

Nếu chỉ biết ngày công bố, chỉ nhận ngày trước ngày cutoff; loại filing cùng ngày cutoff. Filing 31/3 lúc 16:05 không được dùng cho cutoff 16:00; filing 30/3 chỉ có ngày được dùng. Báo cáo quý kết thúc 31/3 filed 25/4 không xuất hiện trong snapshot 31/3.

Execution mở phiên kế tiếp; giữ đến mở phiên sau cutoff quý tiếp theo. Giá đóng cửa cutoff dùng valuation/filter, giá mở cửa dùng execution/target. Lưu raw open/close, dividends và splits; accounting dùng shares và cashflows thực, không trộn raw open với adjusted close. Total-return adjusted series chỉ dùng đối chiếu, không cộng dividend lần hai. Split không tự tạo lãi/lỗ; dividend nhận vào tiền mặt, tái đầu tư khi rebalance.

Sample mục tiêu: tín hiệu 2010Q1–2025Q4; outcome cuối kết thúc phiên mở đầu quý II/2026. Warm-up trước 2010 phải đủ 8 quý đã công bố và đầu kỳ stock cần thiết. XBRL đầu sample có thể thiếu: audit quyết định sample khả dụng trước xem performance, không cam kết đủ 2010.

## As-filed facts và period

- Giữ raw filings/companyfacts/submissions, accession, version, source URL, retrieved_at và checksum; snapshot truy nguyên tới facts thực dùng. Companyfacts là facts tổng hợp, không tự là snapshot point-in-time.
- Chọn fact theo accession đã công bố tại cutoff, cùng entity scope/unit/period. Amendments chỉ có hiệu lực từ publication của bản sửa; không ghi đè snapshot trước đó. Fact comparative công bố lại không được mang về trước publication.
- Tách instant/duration; fiscal quarter không nhất thiết trùng calendar quarter. Q2 riêng = YTD6 − Q1; Q3 = YTD9 − YTD6; Q4 = FY − YTD9. Chỉ trừ facts cùng fiscal year, unit, scope và phiên bản reconciliation đã biết tại cutoff; thiếu thì missing. Ưu tiên quarterly fact trực tiếp đã xác minh; khác biệt với derivation phải giải quyết.
- TTM cộng 4 quý tài khóa liên tiếp không chồng lấn; YoY so TTM với 4 quý trước. Fiscal-year change/period bất thường cần kiểm tra hoặc loại, không nội suy quý thiếu. Stock dùng instant, không cộng 4 quý.
- Staleness/carry-forward theo [02](02-universe-factors-ranking.md); lưu period end, publication và tuổi, không coi amendment là dữ liệu kinh tế mới.

## Identity, universe và ngành lịch sử

EDGAR filer history là đầu vào tìm doanh nghiệp, chưa đủ chứng minh survivor-free universe. SEC submissions có metadata hiện tại; không coi ticker/sàn hiện tại là lịch sử listing. Audit coverage bằng danh sách chứng khoán lịch sử, bằng chứng listing/delisting và corporate events từng cutoff. Không chỉ lấy mã còn sống hôm nay.

Lưu entity_id/CIK riêng security_id/share_class; ticker và exchange có valid_from/valid_to, source và known_at. Không nối ticker trùng tên qua hai doanh nghiệp. Chọn share class theo [02](02-universe-factors-ranking.md). SIC lấy từ filing đã biết tại cutoff; ánh xạ Ken French 17 bằng bảng versioned, không backfill SIC hiện tại. Lưu nhãn chính và bằng chứng thay đổi nghiệp vụ; thiếu nhãn lịch sử thì chưa đủ điều kiện.

Metadata cần có: identifiers, fiscal year/quarter, start/end, form, filed date, publication/availability timestamp, accession/amendment, taxonomy/tag/context, value/unit/currency, source/version; membership, SIC/industry và corporate actions có hiệu lực theo thời gian. Nguồn thiếu timestamp phải mang cờ date_only.

## Giá thiếu và corporate actions

Phân loại trước tính return: đổi ticker/sàn, split, merger tiền mặt/cổ phiếu, bankruptcy/cancellation, trading halt hoặc lỗi provider. Merger dùng consideration thực. Stock nhận sau merger là vị thế bắt buộc, bán ở phiên mở khả thi đầu tiên sau khi xác minh; trước đó báo exposure ngoài candidate pool. Bankruptcy dùng recovery/cancellation có bằng chứng; không mặc định mọi bankruptcy bằng 0.

Không forward-fill giá qua event chưa giải quyết hoặc loại mã khỏi lịch sử để né lỗ. Nếu thiếu execution/exit price hoặc consideration chưa xác minh, gắn unresolved và chặn kết luận performance chính cho sample liên quan; hiển thị số lượng/ảnh hưởng, không xóa âm thầm. −100% chỉ là stress scenario cho phần chưa rõ, không thay dữ liệu thực.

## Nguồn và cổng kiểm tra

Ngân sách 0 USD: SEC EDGAR as-filed; giá yfinance, Stooq dự phòng sau kiểm tra scale/corporate actions trước nối; ngành SIC/Ken French; Ken French factors cho phân tích phụ. Không tự chuyển trả phí. Thiếu nguồn thì ghi blocker, giới hạn scope/sample theo audit và giữ kết luận chưa đủ dữ liệu.

[SEC API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) mô tả submissions/XBRL và giới hạn facts aggregate ở taxonomy chuẩn/entity scope; custom facts cần filing gốc. Không dùng frames “last filed” làm snapshot lịch sử. [SEC developer resources](https://www.sec.gov/about/developer-resources) hướng dẫn truy cập filings. Nguồn không bảo đảm universe hoàn chỉnh.

Kiểm tra bắt buộc: publication ≤ cutoff; date-only không cùng ngày; amendment không sửa quá khứ; không trùng duration khi TTM; đủ warm-up; identity/ngành có nguồn; split/dividend không double count; event unresolved chặn primary performance. Pilot và audit universe là hai cổng riêng ở [05](05-portfolio-roadmap.md).
