# Idea: Fundamental Ranking Lab

Khởi tạo 2026-10-14; cập nhật thiết kế 2026-10-15.

**Trạng thái:** thiết kế nghiên cứu đã xác định; triển khai theo cổng kiểm chứng dữ liệu. Chưa thực hiện pilot, audit universe, pipeline hoặc backtest. Không coi các nguồn miễn phí là bảo đảm dữ liệu lịch sử hoàn chỉnh.

## Mục tiêu và nội dung

Mỗi quý dùng fundamentals đã công bố để rank cổ phiếu/ngành, tạo danh mục khoảng 100 mã và kiểm chứng Q1–Q3 ngoài mẫu.

- [Concept và output](01-concept.md)
- [Universe, factor dictionary và ranking](02-universe-factors-ranking.md)
- [Hypothesis testing và đánh giá](03-hypothesis-validation.md)
- [Thông tin được phép dùng](04-point-in-time-data.md)
- [Portfolio, pilot và cổng triển khai](05-portfolio-roadmap.md)
- [Trạng thái quyết định và nguồn](06-open-decisions-references.md)
- [Bảng tham số tổng hợp](07-spec-parameters.md)

## Quyết định chính

- Mỹ, USD, dữ liệu miễn phí; SEC EDGAR as-filed, giá yfinance/Stooq cần audit; SIC lịch sử ánh xạ Ken French 17.
- Lõi chung cho so ngành/top-100/weights; ratios đặc thù cho ranking trong nhóm. Chưa đạt dictionary/cổng thì unavailable.
- Quality, Financial Health, Valuation dùng level; Growth dùng YoY. Percentile và equal-weight; không level/change 50/50 áp đồng loạt.
- Top-100 lấy hết ties; dưới 100 lấy hết. Score-weight + tilt λ=0,5; caps ngành 20%, doanh nghiệp 5%; dư tiền mặt lợi suất 0%, tính vào NAV.
- Rebalance đầy đủ mỗi quý; chi phí 10 bps một chiều, sensitivity 0/25/50. Chưa gắn vốn hoặc kết luận capacity.
- Cutoff cuối quý 16:00 America/New_York, next-open execution. Date-only filing chỉ nhận từ ngày trước cutoff.
- Tín hiệu mục tiêu 2010Q1–2025Q4, outcome tới open quý II/2026; split research/validation/test theo 03, chờ audit khả thi.
- Primary Q1 Fama–MacBeth slope, Q2 spread ngành, Q3 net excess; BH cho 3 primary tests; phân tích phụ đăng ký riêng. Không tuning final test.

## Bước tiếp theo và giới hạn

Đặc tả pilot 40 doanh nghiệp × 4 cutoff lịch sử, manual reconciliation ≥ 10 doanh nghiệp; từng nhóm có cổng riêng. Sau đó audit toàn universe trước primary backtest. Bank/insurance/REIT/Other Financials không tự vào kết quả chính khi thiếu dữ liệu hoặc chưa chứng minh lõi tương đương.

Spec tách đã chốt, mặc định nghiên cứu, chờ kiểm chứng và hoãn. Caps 20%/5% là lựa chọn kiểm soát tập trung, chưa chứng minh tối ưu. Giá/event unresolved chặn primary performance; không mặc định −100% cho giá thiếu. Nghiên cứu có thể kết luận âm hoặc chưa đủ bằng chứng; ML và quyết định dùng vốn thực để sau.
