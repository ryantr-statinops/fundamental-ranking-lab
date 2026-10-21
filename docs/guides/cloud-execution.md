# Hướng dẫn thực thi trên Cloud (Google Colab)

Tài liệu này hướng dẫn cách chạy bóc tách dữ liệu và tính toán chỉ số tài chính (Point-in-Time Features) trên môi trường điện toán đám mây Google Colab nhằm tối ưu hóa tài nguyên phần cứng (RAM/Disk) cho máy tính cá nhân.

## 1. Đóng gói dữ liệu thô từ máy Local

Thư mục `data/raw/sec/` chứa toàn bộ hồ sơ nộp báo cáo của 40 doanh nghiệp. Để tránh việc đồng bộ hàng chục nghìn file lẻ lên Google Drive và loại bỏ các file `.txt` submission toàn văn nặng nề, sử dụng script:

```bash
uv run python scripts/pack_raw.py
```

Script sẽ:
- Lọc bỏ các file `<SEC-DOCUMENT> .txt` (tiết kiệm ~66 GB dung lượng).
- Giữ lại toàn bộ file XML/XBRL gốc, metadata JSON và file `.records_cache.json`.
- Tạo ra file nén `pilot_raw_bundle.zip` (dung lượng gọn nhẹ chỉ khoảng 2.5 - 3.5 GB).

## 2. Chuẩn bị trên Google Drive

1. Đăng nhập vào Google Drive của bạn.
2. Tạo thư mục mới tại đường dẫn gốc:  
   `FundamentalRankingLab/`
3. Kéo thả file `pilot_raw_bundle.zip` vừa tạo vào thư mục trên:  
   `Google Drive/FundamentalRankingLab/pilot_raw_bundle.zip`

## 3. Mở Notebook trên Google Colab

1. Truy cập [Google Colaboratory](https://colab.research.google.com/).
2. Chọn tab **GitHub**.
3. Dán đường link repo:  
   `https://github.com/ryantr-statinops/fundamental-ranking-lab`
4. Chọn notebook:  
   `notebooks/01_colab_pilot_runner.ipynb`

## 4. Cấu hình bảo mật (Colab Secrets)

Để giữ an toàn cho thông tin cá nhân và tuân thủ chính sách SEC:
1. Nhìn sang thanh công cụ bên trái màn hình Colab, bấm vào biểu tượng **Chìa khóa (🔑 - Secrets)**.
2. Bấm **Add new secret**:
   - **Name:** `FRL_SEC_USER_AGENT`
   - **Value:** `Họ_Tên email_của_bạn@domain.com`
   - Gạt công tắc **Notebook access** sang màu xanh.

## 5. Thực thi và nhận kết quả

Nhấn **Runtime -> Run all** (hoặc Ctrl+F9):
1. Notebook sẽ tự động mount Google Drive.
2. Giải nén `pilot_raw_bundle.zip` vào ổ đĩa ảo Colab SSD cực nhanh (< 30 giây).
3. Cài đặt môi trường `uv` và chạy pipeline `uv run frl pilot --config configs/pilot.toml`.
4. Sau khi hoàn thành, toàn bộ các file kết quả Parquet (`facts.parquet`, `ratios.parquet`), ma trận coverage và báo cáo `feasibility.md` sẽ được tự động sao lưu an toàn về:  
   `Google Drive/FundamentalRankingLab/results/<run_id>/`
