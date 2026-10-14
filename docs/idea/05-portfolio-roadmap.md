# Portfolio và lộ trình nghiên cứu

## 100 mã

100 mã được chọn từ universe, phục vụ ranking và portfolio. Chưa chốt nắm giữ toàn bộ hay chọn danh mục nhỏ hơn. Portfolio cần số holdings, weights, giới hạn mã/ngành, liquidity, sell rules và costs. Ranking tốt vẫn có thể gây tập trung ngành.

## Mốc đề xuất

1. **Research specification:** chốt thị trường, data, universe, ngành, factors, benchmark, horizon, quarterly schedule, hypotheses và output.
2. **Data + factor baseline:** snapshots point-in-time, hard filters, scores, ranking ngành/mã; xuất lịch sử 100 ứng viên và lý do chọn/loại.
3. **Portfolio + validation:** weights, execution, costs, backtest, attribution ngành/mã, metrics và inference ngoài mẫu.
4. **ML ranking:** học từ features theo target tương lai. Ngày rebalance là ranking group. Có thể dùng LightGBM LambdaRank với labels nguyên không âm; so regression-then-sort và factor baseline.
5. **ML reranking:** sắp lại candidate pool; so ranker toàn universe với candidate-then-rerank để đánh giá tổn thất do lọc. Model score không mặc định là probability/expected return.

Đây là lộ trình đề xuất, chưa triển khai code.

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
