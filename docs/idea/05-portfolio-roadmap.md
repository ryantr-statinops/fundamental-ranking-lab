# Portfolio và lộ trình nghiên cứu

## Candidate pool và holdings

Candidate pool khoảng 100 mã đến từ universe đủ điều kiện (top-100 theo score so ngành, xem [02](02-universe-factors-ranking.md)). Holdings là tập nhỏ hơn lấy từ candidate pool, phân bổ theo quy tắc construction. Danh mục không bắt buộc nắm toàn bộ candidate pool.

v1 thử số holdings ở các mức **30, 50 và 100** để so độ tập trung và ảnh hưởng tới hiệu quả sau chi phí.

## Ảnh hưởng của ranking ngành

Ranking ngành thay đổi tỷ trọng holdings: weight của mỗi mã nhân với hệ số theo hạng ngành (có biên và tham số λ), rồi chuẩn hóa lại. Áp trần tỷ trọng ngành để tránh tập trung. Tham số λ để mở và thử ở giai đoạn validation.

Ranking tốt vẫn có thể gây tập trung ngành; trần tỷ trọng và tilt cần được kiểm tra cùng nhau.

## Quy tắc construction

- Weight scheme: **score-weight** là mặc định cho kết quả chính; **cap-weight** là biến thể đối chiếu. Có thể thêm equal-weight làm tham chiếu.
- Trần tỷ trọng mỗi mã: 10%.
- Trần tỷ trọng mỗi ngành: 25%.
- Thanh khoản: ràng buộc qua hard filter của universe ([02](02-universe-factors-ranking.md)).
- Nguồn mã: chỉ lấy từ candidate pool.

## Turnover và chi phí

- **No-trade band**: chỉ giao dịch khi tỷ trọng lệch khỏi target quá 1%, nhằm giảm turnover.
- **Chi phí theo component model**: commission + spread + market impact. Tham số cụ thể để mở, gắn với thị trường ở [06](06-open-decisions-references.md).
- Báo cáo turnover mỗi kỳ và tổng chi phí.

## Mốc đề xuất

1. **Research specification:** đã xong; thị trường và data cụ thể còn lại ở [06](06-open-decisions-references.md).
2. **Data + factor baseline:** snapshots point-in-time, hard filters, scores, ranking ngành/mã; xuất lịch sử 100 ứng viên và lý do chọn/loại.
3. **Portfolio + validation:** weights, execution, costs, backtest, attribution ngành/mã, metrics và inference ngoài mẫu.
4. **ML ranking:** học từ features theo target tương lai. Ngày rebalance là ranking group. Có thể dùng LightGBM LambdaRank với labels nguyên không âm; so regression-then-sort và factor baseline.
5. **ML reranking:** sắp lại candidate pool; so ranker toàn universe với candidate-then-rerank để đánh giá tổn thất do lọc. Model score không mặc định là probability/expected return.

Đây là lộ trình đề xuất; v1 gồm mốc 1-3, ML ở mốc 4-5 để giai đoạn sau.

## Repo dự kiến

```text
configs/
src/data/
src/features/
src/universe/
src/ranking/
src/models/
src/evaluation/
src/backtest/
tests/
notebooks/
reports/
docs/idea/
```

Tests triển khai tập trung vào leakage, versioning, ranking groups và portfolio accounting.

## Definition of done

Pipeline tái lập từ dữ liệu đến ranking và báo cáo ngoài mẫu; trả lời phương pháp có cải thiện baseline sau chi phí không, với độ bất định bao nhiêu. Kết quả không bắt buộc dương để nghiên cứu hoàn thành.
