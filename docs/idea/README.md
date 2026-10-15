# Idea: Fundamental Ranking Lab

Ngày khởi tạo: 2026-10-14. Tài liệu ghi lại concept, đề xuất nghiên cứu và các quyết định thiết kế cho dự án.

## Mục tiêu

Mỗi quý, sử dụng thông tin fundamental đã công bố để đánh giá ngành, chọn khoảng 100 cổ phiếu từ universe và xếp hạng nhằm phục vụ danh mục đầu tư. Kiểm chứng ngoài mẫu xem phương pháp có liên hệ với kết quả đầu tư tương lai hay không.

## Nội dung

- [Concept và output](01-concept.md)
- [Universe, factors và ranking](02-universe-factors-ranking.md)
- [Hypothesis testing và đánh giá](03-hypothesis-validation.md)
- [Thông tin được phép dùng](04-point-in-time-data.md)
- [Portfolio và lộ trình](05-portfolio-roadmap.md)
- [Quyết định mở và nguồn](06-open-decisions-references.md)
- [Bảng tham số tổng hợp](07-spec-parameters.md)

## Đã xác định

- Hướng quant research; chọn khoảng 100 mã từ universe.
- Thị trường Mỹ; fundamentals SEC EDGAR (as-filed), giá yfinance/Stooq, ngành SEC SIC/Ken French, factor Ken French (free).
- Nhóm theo ngành: Ken French 17 ngành; nhãn chính.
- Bốn trục: Quality, Growth, Financial Health, Valuation; bộ ratio cụ thể cho general/Finan/Utils.
- Cập nhật hàng quý; horizon một quý; cutoff ngày giao dịch cuối quý 16:00 ET, execution mở phiên kế tiếp.
- Phạm vi v1: factor ranking, ranking ngành/mã, portfolio và backtest; ML ranking/reranking để sau.
- Chọn 100 mã bằng top-100 theo score so ngành từ universe đủ điều kiện.
- Output mỗi quý gồm ranking ngành, khoảng 100 ứng viên, holdings và tỷ trọng.
- Statistical inference là lớp kiểm chứng phương pháp; một phía, α = 0.05, hiệu chỉnh Benjamini–Hochberg.
- Sample 2010Q1–2025Q4; research 2010–2019, validation 2020–2022, test 2023–2025.

Bảng trạng thái đầy đủ ở [06](06-open-decisions-references.md); tham số tổng hợp ở [07](07-spec-parameters.md). Bộ spec đã đầy đủ để triển khai.
