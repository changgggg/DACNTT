============================
DỰ ÁN: Khai thác các tập phổ biến một phần trong cơ sở dữ liệu dạng cột theo thời gian
============================

📌 Mô tả:
Dự án hiện thực hóa và cải tiến thuật toán 3P-ECLAT để khai phá các mẫu tuần hoàn một phần (Partial Periodic Patterns - 3Ps) trong cơ sở dữ liệu thời gian dạng cột.

Hệ thống so sánh 2 thuật toán:
- 3P-ECLAT
- 3P-ECLAT Pruning (cải tiến thêm cắt tỉa và giảm bộ nhớ)

----------------------------
📁 Cấu trúc thư mục:
----------------------------

📦 project-root/
 ┣ 📜 main.py                         # Tập tin chính để chạy thử nghiệm
 ┣ 📜 ThreeP_Eclat.py                 # Phiên bản 3P-ECLAT
 ┣ 📜 ThreeP_Eclat_Pruning.py         # Phiên bản cải tiến có pruning
 ┣ 📂 database/                       # Thư mục chứa dữ liệu đầu vào (.csv)
 ┃ ┣ Temporal_T10I4D100K.csv
 ┃ ┣ Temporal_T20I6D100K.csv
 ┃ ┣ Transactional_connect.csv
 ┃ ┗ Transactional_retail.csv
 ┣ 📂 output/                      # Biểu đồ thống kê tổng quan
 ┣ 📂 output1/                     # Biểu đồ mẫu Pruning
 ┣ 📂 output_T10I4D100K_minPS_fixed/     # Kết quả theo từng chế độ chạy
 ┣ 📂 output_T10I4D100K_period_fixed/  
 ┣ 📂 output_T20I6D100K_minPS_fixed/
 ┣ 📂 output_T20I6D100K_period_fixed/
 ┣ 📂 output_Transactional_connect_minPS_fixed/
 ┣ 📂 output_Transactional_connect_period_fixed/
 ┣ 📂 output_Transactional_retail_minPS_fixed/
 ┣ 📂 output_Transactional_retail_period_fixed/
 ┣ 📜 requirements.txt               # Danh sách thư viện cần cài
 ┗ 📜 README.txt                     # Tập tin hướng dẫn

(*) Các thư mục `output_*` sẽ được tạo tự động sau khi chạy chương trình.


----------------------------
▶️ Cách chạy chương trình:
----------------------------

1. **Cài thư viện cần thiết (nếu chưa có):**
pip install pandas matplotlib psutil validators

2. **Chạy chương trình:**
python main.py

3. **Lựa chọn khi chạy:**
- Chế độ 1: Giữ `minPS` cố định, thay đổi `per`
- Chế độ 2: Giữ `per` cố định, thay đổi `minPS`

4. **Chọn 1 trong 4 bộ dữ liệu có sẵn:**
- Temporal_T10I4D100K.csv
- Temporal_T20I6D100K.csv
- Transactional_connect.csv
- Transactional_retail.csv

5. **Kết quả:**
- In ra màn hình: số mẫu, thời gian thực thi, bộ nhớ.
- Tạo các file:
  - `*_stats.txt`: thống kê tập dữ liệu
  - `*_patterns.txt`: mẫu tuần hoàn khai thác được
  - `*.png`: biểu đồ runtime, memory, số mẫu
  - `.csv`: bảng kết quả tổng hợp


----------------------------
📌 Tùy chỉnh:
----------------------------
Bạn có thể điều chỉnh các tham số trong `main.py`, như:
- Tập giá trị `minPS` hoặc `period`
- Thêm dữ liệu mới vào thư mục `database/`


----------------------------
👨‍💻 Thành viên thực hiện:
----------------------------
- Thái Gia Bảo – 52000014
- Nguyễn Gia Nguyễn – 52000851