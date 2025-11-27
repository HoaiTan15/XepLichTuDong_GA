# 🧬 Hệ Thống Xếp Lịch Tự Động Sử Dụng Thuật Toán Di Truyền

## 📋 Mô tả dự án

Đây là một hệ thống xếp lịch học tự động sử dụng **Thuật toán di truyền (Genetic Algorithm)** để tối ưu hóa việc sắp xếp thời khóa biểu cho các lớp học. Hệ thống giúp giải quyết bài toán phức tạp về việc phân bổ giảng viên, phòng học và thời gian một cách hiệu quả, tối thiểu hóa các xung đột trong lịch học.

## ✨ Tính năng chính

- 🎯 **Tối ưu hóa thời khóa biểu**: Sử dụng thuật toán di truyền để tìm lịch học tối ưu
- 🌐 **Giao diện web**: Interface thân thiện với Flask
- 📊 **Xử lý dữ liệu**: Đọc dữ liệu từ file Excel và xuất kết quả
- 📈 **Theo dõi tiến trình**: Hiển thị tiến độ thực thi thuật toán real-time
- 🔧 **Tùy chỉnh tham số**: Có thể điều chỉnh các tham số của thuật toán
- 📋 **Báo cáo kết quả**: Xuất lịch học chi tiết và thống kê xung đột

## 🛠️ Công nghệ sử dụng

- **Python 3.x**: Ngôn ngữ lập trình chính
- **Flask**: Web framework cho giao diện web
- **Pandas**: Xử lý và phân tích dữ liệu
- **Matplotlib**: Vẽ biểu đồ và visualization
- **OpenPyXL**: Đọc/ghi file Excel
- **HTML/CSS**: Frontend cho web interface

## 📁 Cấu trúc dự án

```
XepLichTuDong_GA/
├── code/
│   ├── app.py                 # Ứng dụng web Flask
│   ├── genetic_algorithm.py   # Lớp chính của thuật toán di truyền
│   ├── fitness.py            # Hàm đánh giá fitness
│   ├── crossover.py          # Toán tử lai ghép
│   ├── mutation.py           # Toán tử đột biến
│   ├── main.py               # Chương trình chính (console)
│   ├── fix_dataset.py        # Script sửa dữ liệu
│   └── templates/            # Templates HTML cho web
│       ├── base.html
│       ├── index.html
│       ├── configure.html
│       ├── data_preview.html
│       ├── running.html
│       └── results.html
├── data/
│   ├── dataset.xlsx          # Dữ liệu gốc
│   ├── dataset_50_classes.xlsx  # Dataset 50 lớp
│   └── datasetHP.xlsx        # Dataset HP
└── README.md
```

## 🚀 Cài đặt và chạy

### Yêu cầu hệ thống
- Python 3.7+
- pip

### 1. Clone repository
```bash
git clone https://github.com/HoaiTan15/XepLichTuDong_GA.git
cd XepLichTuDong_GA
```

### 2. Cài đặt dependencies
```bash
pip install flask pandas matplotlib openpyxl
```

### 3. Chạy ứng dụng

#### Chạy web interface:
```bash
cd code
python app.py
```
Sau đó truy cập: `http://localhost:5000`

#### Chạy console version:
```bash
cd code
python main.py
```

## 🔧 Cấu hình thuật toán

Bạn có thể tùy chỉnh các tham số trong file `genetic_algorithm.py`:

- **Population Size**: Kích thước quần thể (mặc định: 60)
- **Generations**: Số thế hệ (mặc định: 150)
- **Crossover Rate**: Tỷ lệ lai ghép
- **Mutation Rate**: Tỷ lệ đột biến

## 📊 Dữ liệu đầu vào

Dữ liệu đầu vào là file Excel với cấu trúc:
- **course_id**: Mã khóa học
- **course_name**: Tên môn học  
- **subject_code**: Mã môn học
- **section**: Lớp/nhóm
- **teacher**: Giảng viên
- **room**: Phòng học

## 🎯 Thuật toán

### Genetic Algorithm Flow:
1. **Khởi tạo quần thể**: Tạo ngẫu nhiên các lịch học ban đầu
2. **Đánh giá fitness**: Tính điểm cho mỗi lịch dựa trên xung đột
3. **Chọn lọc**: Chọn các cá thể tốt nhất
4. **Lai ghép (Crossover)**: Kết hợp các lịch tốt
5. **Đột biến (Mutation)**: Thay đổi ngẫu nhiên một số gene
6. **Lặp lại**: Cho đến khi đạt được kết quả mong muốn

### Hàm Fitness:
Điểm fitness được tính dựa trên:
- Xung đột về phòng học (cùng thời gian)
- Xung đột về giảng viên (cùng thời gian)
- Tối ưu hóa phân bổ thời gian

## 📈 Kết quả

Hệ thống xuất ra:
- **File Excel**: Lịch học được sắp xếp chi tiết
- **Báo cáo**: Số lượng xung đột và tỷ lệ thành công
- **Visualization**: Biểu đồ tiến trình thuật toán

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng:
1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📧 Liên hệ

- **Tác giả**: HoaiTan15
- **Email**: [Thêm email của bạn]
- **GitHub**: [@HoaiTan15](https://github.com/HoaiTan15)

## 📄 License

Dự án này được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.

---

⭐ Nếu dự án này hữu ích cho bạn, hãy cho một star nhé!