# PHÁT HIỆN KHÔNG ĐỘI MŨ

Ứng dụng web phát hiện người điều khiển xe máy không đội mũ bảo hiểm từ ảnh/video.

## Chức năng đã có

- Tạo, sửa, xóa **Dự án**.
- Tạo, sửa, xóa nhiều **Địa điểm** động trong từng dự án.
- Upload kéo-thả nhiều ảnh/video.
- Gắn dữ liệu với dự án, địa điểm, ngày và khung giờ.
- Xử lý AI bằng model `backend/models/best.pt` qua một lớp `Detector` độc lập.
- Nhận diện trạng thái đội mũ/không đội mũ theo class của model.
- Xử lý video theo frame và dùng centroid tracking để hạn chế đếm trùng.
- Lưu ảnh/video kết quả có bounding box.
- Lưu ảnh bằng chứng cho trường hợp không đội mũ.
- Lưu lịch sử vào database.
- Theo dõi trạng thái `PENDING → PROCESSING → COMPLETED/FAILED` và phần trăm xử lý.
- Xem dữ liệu theo dự án, địa điểm và phiên phân tích.
- Thống kê tổng phương tiện, tổng vi phạm, tỷ lệ và vi phạm theo khung giờ.
- Tải dữ liệu của phiên/địa điểm/dự án thành file ZIP.
- Giao diện responsive, giữ bố cục chính giống bản vẽ: upload ở bên trái, cây dự án/địa điểm ở bên phải.

## Công nghệ

- **Frontend:** React + Vite + TypeScript.
- **Backend:** Python + FastAPI + SQLAlchemy.
- **AI:** Ultralytics YOLO + OpenCV.
- **Database:** SQLite mặc định để demo ngay; có thể đổi `DATABASE_URL` sang PostgreSQL/Supabase.
- **Storage:** local `backend/storage/`; database chỉ lưu đường dẫn file.

## Cấu trúc

```text
he_thong_phat_hien_khong_doi_mu/
├── backend/
│   ├── app/
│   │   ├── api/                 # REST routes
│   │   ├── core/                # config + database
│   │   ├── models/              # SQLAlchemy entities
│   │   ├── repositories/        # truy cập database
│   │   ├── schemas/             # request/response models
│   │   ├── services/
│   │   │   ├── ai/
│   │   │   │   ├── detector.py
│   │   │   │   ├── violation.py
│   │   │   │   └── tracker.py
│   │   │   ├── image_processor.py
│   │   │   ├── video_processor.py
│   │   │   ├── evidence_service.py
│   │   │   ├── analysis_service.py
│   │   │   ├── statistics_service.py
│   │   │   └── download_service.py
│   │   └── main.py
│   ├── models/best.pt
│   ├── storage/
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   └── package.json
├── install_windows.bat
├── run_windows.bat
└── README.md
```

## Chạy bằng Visual Studio Code — cách khuyến nghị

Bộ mã nguồn đã có sẵn cấu hình workspace trong `.vscode/` và file `helmet-detection.code-workspace`.

### Chạy lần đầu

1. Cài **Python 3.11 x64**, **Node.js LTS** và **Visual Studio Code**.
2. Nhấp đúp `open_vscode.bat`, hoặc mở `helmet-detection.code-workspace` từ VS Code.
3. Chọn **Install All** khi VS Code đề xuất extension.
4. Mở **Run and Debug** (`Ctrl+Shift+D`).
5. Chọn **Toàn hệ thống: Backend + Frontend** và nhấn `F5`.

Task trước khi debug sẽ tự tạo virtual environment, cài/cập nhật thư viện, tạo `.env`, kiểm tra model rồi khởi động cả backend và frontend. Trình duyệt sẽ mở tại `http://localhost:5173`.

Các file cấu hình chính:

```text
.vscode/settings.json       # Python interpreter, pytest, TypeScript
.vscode/launch.json         # F5 chạy FastAPI + React/Vite
.vscode/tasks.json          # setup, test, build, kiểm tra model
.vscode/extensions.json     # extension được khuyến nghị
scripts/vscode_setup.ps1    # tự động chuẩn bị môi trường
VSCODE_GUIDE.md             # hướng dẫn chi tiết và xử lý lỗi
```

Dừng toàn bộ bằng `Shift+F5`. Xem hướng dẫn đầy đủ tại [VSCODE_GUIDE.md](VSCODE_GUIDE.md).

## Chạy nhanh trên Windows

### 1. Cài môi trường

Cần có Python và Node.js trên máy. Khuyến nghị dùng Python 3.10–3.12 để tương thích thuận lợi với PyTorch/Ultralytics.

Chạy:

```bat
install_windows.bat
```

Script sẽ:

1. Tạo `backend\.venv`.
2. Cài các thư viện Python trong `backend\requirements.txt`.
3. Tạo `backend\.env` từ `.env.example` nếu chưa có.
4. Chạy `npm install` cho frontend.
5. Tạo `frontend\.env` từ `.env.example` nếu chưa có.

### 2. Khởi động

```bat
run_windows.bat
```

Sau đó mở:

- Giao diện: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`
- API health: `http://localhost:8000/api/health`

## Chạy thủ công trong VS Code

### Backend

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
python run.py
```

### Frontend

Mở terminal thứ hai:

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

## Build frontend để FastAPI phục vụ cùng một cổng

```powershell
cd frontend
npm run build
cd ..\backend
python run.py
```

Khi thư mục `frontend/dist` tồn tại, FastAPI sẽ tự phục vụ giao diện tại `http://localhost:8000`.

## Cấu hình model

File model đã được đặt tại:

```text
backend/models/best.pt
```

Cấu hình trong `backend/.env`:

```env
MODEL_PATH=./models/best.pt
CONFIDENCE_THRESHOLD=0.40
IOU_THRESHOLD=0.50
DEVICE=cpu

HELMET_CLASS_NAMES=with helmet,helmet,wearing helmet
NO_HELMET_CLASS_NAMES=without helmet,no helmet,no_helmet,without_helmet
VEHICLE_CLASS_NAMES=motorcycle,motorbike,bike
```

Tên class được chuẩn hóa không phân biệt chữ hoa, khoảng trắng, dấu gạch ngang và dấu gạch dưới. Khi đổi model, chỉ cần thay file và cập nhật các biến class trong `.env`, không phải sửa API/UI.

### Dùng GPU NVIDIA

Sau khi cài đúng bản PyTorch hỗ trợ CUDA trên máy, đổi:

```env
DEVICE=0
```

Nếu chỉ demo trên laptop không có GPU, giữ:

```env
DEVICE=cpu
```

## Luồng xử lý

```text
Upload ảnh/video
      ↓
Tạo analysis_session = PENDING
      ↓
FastAPI BackgroundTask
      ↓
Detector → Violation Logic → Tracker
      ↓
Ảnh/video kết quả + ảnh bằng chứng
      ↓
Database + statistics
      ↓
Frontend polling và hiển thị kết quả
```

AI inference nằm trong `services/`, không nằm trực tiếp trong API route.

## Database

Mặc định:

```env
DATABASE_URL=sqlite:///./helmet_detection.db
```

Để dùng PostgreSQL/Supabase, thay bằng URL kết nối PostgreSQL, ví dụ:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
```

Các bảng chính:

- `projects`
- `locations`
- `analysis_sessions`
- `media_files`
- `violations`

## Điều chỉnh video

Trong `backend/.env`:

```env
VIDEO_FRAME_STRIDE=1
VIDEO_MAX_WIDTH=1280
TRACK_MAX_MISSING=18
TRACK_MAX_DISTANCE_RATIO=0.08
VIOLATION_CONFIRMATION_FRAMES=3
```

- `VIDEO_FRAME_STRIDE=1`: AI chạy mọi frame, chính xác hơn nhưng chậm hơn.
- Tăng lên `2` hoặc `3` để demo nhanh hơn trên CPU.
- `VIDEO_MAX_WIDTH` giảm độ phân giải xử lý của video dài/4K.
- `VIOLATION_CONFIRMATION_FRAMES=3`: video chỉ ghi nhận vi phạm sau 3 lần nhận diện không mũ liên tiếp trên cùng track. Mất phát hiện hoặc đổi trạng thái sẽ đặt lại chuỗi xác nhận. Đây là số frame được chạy AI; tăng stride sẽ tăng thời gian chờ xác nhận. Đối tượng xuất hiện quá ngắn có thể chưa đủ điều kiện xác nhận. Cấu hình này không áp dụng cho ảnh.
- Video dài vẫn giữ đúng `VIDEO_FRAME_STRIDE`, không tự tăng bước lấy mẫu. Thay đổi chỉ áp dụng khi phân tích lại video; kết quả cũ trong lịch sử không tự cập nhật.
- Tracker hiện tại là centroid tracker nhẹ, phù hợp MVP. Có thể thay bằng ByteTrack/BoT-SORT trong `services/ai/tracker.py` mà không đổi API.

## Lưu ý khi đánh giá kết quả

- Confidence/IoU mặc định chỉ là điểm bắt đầu; cần test bằng dữ liệu thật và hiệu chỉnh.
- Nếu model chỉ có class trạng thái đầu người (`With Helmet`, `Without Helmet`) thì mỗi bounding box trạng thái được dùng như một đối tượng người điều khiển quan sát được.
- Nếu model mới có thêm class `motorcycle`, module `violation.py` sẽ ưu tiên liên kết vùng đầu với vùng xe trước khi kết luận vi phạm.
- BackgroundTasks phù hợp demo/MVP. Khi chạy nhiều video đồng thời trong môi trường thật, nên thay bằng hàng đợi Celery/RQ và worker riêng.
- Với video dài, nên dùng GPU hoặc tăng `VIDEO_FRAME_STRIDE`.

## API chính

```text
GET/POST           /api/projects
GET/PUT/DELETE     /api/projects/{id}
GET/POST           /api/projects/{project_id}/locations
GET/PUT/DELETE     /api/locations/{id}
POST               /api/analyses
GET                /api/analyses/{id}
GET                /api/analyses/{id}/status
GET                /api/analyses/{id}/results
GET                /api/analyses/{id}/violations
GET                /api/locations/{id}/violations
GET                /api/locations/{id}/statistics
GET                /api/projects/{id}/statistics
GET                /api/downloads/analyses/{id}
GET                /api/downloads/locations/{id}
GET                /api/downloads/projects/{id}
```

## Kiểm tra trước khi demo

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python verify_setup.py
```

Kết quả cần có:

- Model tồn tại.
- Ultralytics nạp được model.
- Hiển thị đúng danh sách class.
- Storage có quyền ghi.
- Database kết nối được.
