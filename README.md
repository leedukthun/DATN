# Hệ thống phát hiện không đội mũ bảo hiểm

Ứng dụng phân tích ảnh và video để phát hiện người đi xe máy không đội mũ bảo hiểm. Hỗ trợ quản lý dự án, địa điểm, xem kết quả nhận diện, thống kê vi phạm và tải kết quả.

Backend sử dụng FastAPI, SQLAlchemy, Ultralytics YOLO và OpenCV. Frontend sử dụng React, TypeScript và Vite. Dữ liệu được lưu bằng SQLite và các tệp trong `backend/storage/`.

## Cài đặt và chạy trên Windows

Yêu cầu Python 3.11 và Node.js có sẵn trong PATH.

1. Tải mã nguồn:

   ```powershell
   git clone https://github.com/leedukthun/DATN.git
   cd DATN
   ```

2. Cài thư viện và tạo cấu hình:

   ```powershell
   .\install_windows.bat
   ```

3. Khởi động chương trình:

   ```powershell
   .\run_windows.bat
   ```

Giao diện mở tại `http://localhost:5173`. Tài liệu API tại `http://localhost:8000/docs`. Đóng hai cửa sổ terminal để dừng chương trình.

## Cấu hình

Trình cài đặt tạo `backend/.env` và `frontend/.env` từ các tệp `.env.example`. Các thiết lập chính trong `backend/.env`:

| Biến | Mục đích |
| --- | --- |
| `MODEL_PATH` | Model nhận diện mũ, mặc định `./models/best_3class.pt` (YOLO11n: `bike`, `helmet`, `no-helmet`) |
| `VEHICLE_MODEL_PATH` | Model phụ tìm xe máy, mặc định `./models/yolo11s.pt` (YOLO11s COCO, giấy phép AGPL-3.0). Đầu người phải nằm trên xe máy mới tính là người đi xe, nhờ đó loại người đi bộ. Để trống để tắt |
| `DEVICE` | `auto` (mặc định) chọn GPU NVIDIA, GPU Apple (`mps`) hoặc CPU; cũng có thể đặt `cpu` hay chỉ số GPU như `0` |
| `CONFIDENCE_THRESHOLD` | Ngưỡng tin cậy nhận diện, mặc định `0.25` |
| `INFERENCE_IMGSZ` | Kích thước ảnh khi nhận diện, mặc định `1280`; đầu người trong camera giám sát chỉ khoảng 15–35px |
| `INFERENCE_TILES` | Chia khung hình thành lưới NxN để bắt người ở xa, mặc định `2`. Chậm hơn khoảng 5 lần; máy chỉ có CPU chậm nên đặt `1` |
| `DATABASE_URL` | Kết nối cơ sở dữ liệu |
| `JWT_SECRET` | Khóa ký phiên đăng nhập; thay giá trị mẫu bằng khóa riêng |

Các thiết lập theo dõi và xác nhận vi phạm khác (`VIOLATION_*`, `TRACK_*`, `IGNORE_ZONES`) được giải thích trong `backend/.env.example`. Nếu `backend/.env` được tạo từ bản cũ, hãy cập nhật theo `.env.example` vì bản cũ vẫn trỏ tới `best.pt`.

Database, ảnh/video tải lên và kết quả xử lý được tạo khi sử dụng, không nằm trong repository.

## Build giao diện

Sau khi cài đặt, có thể build frontend để backend phục vụ giao diện trên cùng cổng:

```powershell
cd frontend
npm run build
cd ..\backend
.\.venv\Scripts\python.exe run.py
```

Truy cập `http://localhost:8000`.
