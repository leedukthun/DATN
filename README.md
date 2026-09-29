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
| `MODEL_PATH` | Đường dẫn model, mặc định `./models/best.pt` |
| `DEVICE` | `cpu` hoặc chỉ số GPU, ví dụ `0` khi PyTorch hỗ trợ CUDA |
| `CONFIDENCE_THRESHOLD` | Ngưỡng tin cậy nhận diện |
| `DATABASE_URL` | Kết nối cơ sở dữ liệu |
| `JWT_SECRET` | Khóa ký phiên đăng nhập; thay giá trị mẫu bằng khóa riêng |

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
