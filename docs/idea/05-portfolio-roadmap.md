# Portfolio và lộ trình nghiên cứu

## Candidate pool và trọng số

Danh mục chính long-only, không leverage, mục tiêu nắm top-100 score lõi chung, gồm mọi ties tại ranh giới; dưới 100 thì lấy hết. Không có tầng chọn 30/50 holdings. Score đặc thù không quyết định selection hoặc weights.

Gọi s_i là composite lõi chung trong [0,1]. Với K ngành có eligible member, percentile ngành p_g = (midrank tăng dần của median ngành − 1)/(K − 1); K = 1 cho 0,5. Ngành tốt nhất có p cao nhất. Trọng số thô:

    a_i = s_i × [1 + λ × (2p_g − 1)], λ = 0,5

λ khóa cho primary; không tinh chỉnh bằng final test. a_i = 0 không nhận vốn; nếu mọi a_i = 0 thì toàn tiền mặt, không tự chuyển equal-weight. Báo score, tilt multiplier và target trước/sau caps.

## Caps và phân bổ tiền mặt

Trần mỗi **doanh nghiệp 5% NAV**, mỗi **ngành 20% NAV**, áp tại rebalance. Vì chỉ một share class/doanh nghiệp, trần mã đồng thời là trần doanh nghiệp. Drift giữa kỳ không tự kích hoạt giao dịch; báo vi phạm do drift, sửa ở rebalance kế tiếp. Corporate actions bắt buộc xử lý theo [04](04-point-in-time-data.md).

Thuật toán water-filling xác định:

1. Bắt đầu w_i = 0, phần còn lại R = 1 (trên NAV có thể đầu tư sau phí).
2. Tập active gồm mã a_i > 0 còn room doanh nghiệp và ngành chưa đầy.
3. Tăng weights theo hướng a_i / tổng a_active. Chọn bước nhỏ nhất giữa R, thời điểm một mã chạm 5% và một ngành chạm 20%.
4. Khóa mã/ngành đã đầy, trừ phần vừa phân bổ khỏi R và lặp; dừng khi R = 0 hoặc không còn active. Tolerance 1e−10, không làm tròn trong tính toán.
5. Phần R giữ tiền mặt, lợi suất mặc định 0%; không chuẩn hóa cổ phiếu lên 100% sau caps. Không bổ sung ngoài candidate pool.

Ví dụ minh họa, không phải cấu hình khác: 4 ngành, mỗi ngành 25 mã có a_i bằng nhau. Mỗi ngành nhận 20%, mỗi mã 0,8%; tổng cổ phiếu 80% + tiền mặt 20% = 100%. Với 5 ngành tương tự mỗi ngành nhận 20%, tiền mặt 0%. Không nhân lại weights cổ phiếu của ví dụ 4 ngành với 1/0,8 vì sẽ phá trần ngành.

Nếu chỉ có 3 mã thuộc 3 ngành thì mỗi mã tối đa 5%, còn 85% tiền mặt. Không đánh đồng “top-100” với luôn có 100 holdings dương.

## Execution, turnover và chi phí

Giao dịch đầy đủ đến target mỗi quý, bao gồm thoát mã rời candidate pool/mất eligibility. Hoãn no-trade band; ngưỡng 1 điểm phần trăm cũ không dùng trong primary. Không khớp được lệnh phải báo trạng thái unresolved, không giả vờ đã đạt target.

Chưa gắn quy mô vốn. Chi phí một chiều mặc định **10 bps × tổng giá trị mua và bán**; sensitivity 0/25/50 bps. Không cộng thêm commission/spread/impact lên cùng chi phí này. Báo buys/NAV, sells/NAV và half-turnover = 0,5 × tổng |thay đổi notional| / NAV trước giao dịch; initial entry và exit cuối sample cũng tính phí.

Accounting tự tài trợ: gọi V− là NAV trước phí, t_i là tỷ trọng target gồm caps, H_i− là notional trước giao dịch và c là chi phí một chiều. Giải V+ = V− − c × Σ|t_i V+ − H_i−|; notional sau = t_i V+, cash sau = (1 − Σt_i)V+. Báo weights trên NAV sau phí, bảo đảm cash không âm. Cùng quy ước cho baseline; cuối sample thanh lý và tính phí exit. Return quý đánh dấu trước rebalance tiếp theo, phí entry nằm trong kỳ bắt đầu; phí terminal exit nằm ở kỳ cuối, không trừ hai lần.

Báo NAV, cash, gross/net return, phí, số mã, top-10 weight, largest issuer/industry, số mã hiệu dụng 1/Σq_i² (q chuẩn hóa riêng phần cổ phiếu, unavailable nếu toàn cash), tần suất caps binding và exposure do drift. Chưa kết luận market impact/capacity; component cost và quy mô vốn hoãn.

## Cơ sở chọn giới hạn

20%/5% là mặc định nghiên cứu kiểm soát tập trung, chưa chứng minh tối ưu. [S&P Quality methodology](https://www.spglobal.com/spdji/en/documents/methodologies/methodology-sp-quality-indices.pdf) (09/2025, trang 8, 11) mô tả S&P 500 Quality chọn 100 mã, trần security tối đa 5% kèm giới hạn tương đối vốn hóa, GICS sector 40%. Đây là tiền lệ cho cap security, không phải chứng minh 20% ngành Ken French.

[MSCI Quality Advanced Select methodology](https://www.msci.com/indexes/documents/methodology/4_MSCI_Quality_Advanced_Select_Indexes_Methodology_20230801.pdf) (02/2025) dùng kiểm soát sector tương đối parent index. Không đồng nhất GICS sectors với 17 ngành Ken French. Sensitivity ngành 15%/25% giữ issuer 5%; không chọn cap bằng final test.

## Cổng triển khai

1. **Đặc tả:** đồng bộ các tài liệu và version tham số; nội dung còn phụ thuộc dữ liệu phải mang trạng thái rõ.
2. **Pilot facts:** 40 doanh nghiệp × 4 cutoff ngày giao dịch cuối năm 2012/2018/2022/2025; chọn roster trước khi xem returns. Dùng 20 General, 4 Utils, 4 Bank, 4 Insurance, 4 REIT/real estate, 4 Other Financials. Trong roster có ít nhất 4 doanh nghiệp lỗ, 2 đổi ticker/share class và 2 merger/delisting, có thể trùng các nhóm trên. Mã chưa tồn tại/đã delisted tại một cutoff vẫn có record not_member và bằng chứng, không bịa snapshot; phải có ít nhất một snapshot thực dùng được cho mỗi doanh nghiệp.
3. **Cổng nhóm:** xuất ma trận ratio/trục/cutoff, trace accession/timestamp và reasons; mỗi nhóm có ít nhất 3 doanh nghiệp với snapshot thực và ≥ 50% snapshot member đạt 3/4 trục. Mọi mismatch trọng yếu hoặc structural incompatibility phải giải quyết trước kích hoạt. Đây là ngưỡng feasibility, không chứng minh tính đại diện hoặc alpha.
4. **Audit universe:** kiểm tra độc lập membership/listing, identity, SIC, prices và events từng cutoff trên toàn sample. Mọi lỗ hổng chưa rõ phải được lượng hóa; không chứng nhận survivor-free nếu chưa có bằng chứng. Thiếu giá/event unresolved chặn primary performance sample liên quan. Giới hạn sample/scope chỉ theo audit trước xem returns, ghi manifest; nếu không đủ bằng chứng thì dừng tại feasibility.
5. **Baseline + validation:** dựng ranking, portfolio và đối chiếu; khóa cấu hình trước final test. ML ranking/reranking là giai đoạn sau, không thuộc v1.

Pilot phải đối chiếu filing gốc ít nhất 10 doanh nghiệp, mỗi doanh nghiệp một cutoff thực, phủ cả 6 nhóm trên. Kiểm tra toàn bộ raw inputs/ratios lõi ở các snapshot này; khớp sau quy đổi unit và tolerance bằng nửa đơn vị làm tròn của nguồn, không tự đặt dung sai phần trăm để che lỗi. TTM dẫn tới từng quarterly fact; tag/fallback/custom context cần bằng chứng. Score đặc thù chỉ bật sau dictionary và cùng cổng kiểm tra, không bắt buộc bật để chạy primary lõi chung.

## Acceptance scenarios và definition of done

- Filing sau cutoff/date-only cùng ngày bị loại; amendment tương lai không đổi snapshot cũ.
- YTD → quý riêng và TTM không double count; nền growth âm là missing; dưới 3/4 trục bị loại trước rank.
- Ties ở top-100 lấy hết; dưới 100 lấy hết; empty/all-zero scores giữ cash.
- Caps đầy dừng phân bổ, stocks + cash = 100%; doanh nghiệp ≤ 5%, ngành ≤ 20% sau phí; drift báo riêng.
- Missing giá/event unresolved chặn primary performance; splits/dividends không tạo return giả; phí không gây cash âm.
- Pipeline tái lập từ raw đến báo cáo Q1–Q3, công bố độ bất định và phạm vi dữ liệu. Kết quả âm hoặc chưa đủ bằng chứng vẫn là kết quả hợp lệ, không mặc định cho phép dùng vốn thực.

Repo dự kiến: configs/, src/data/, src/features/, src/universe/, src/ranking/, src/evaluation/, src/backtest/, tests/, notebooks/, reports/. Chưa tạo các thư mục/code trong đợt sửa tài liệu này.
