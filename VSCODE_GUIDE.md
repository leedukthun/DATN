# HƯỚNG DẪN CHẠY BẰNG VISUAL STUDIO CODE TRÊN WINDOWS

## 1. Phần mềm cần có

- Visual Studio Code.
- Python 3.11 x64; khi cài nên chọn **Add Python to PATH**.
- Node.js LTS, kèm theo `npm`.

Có thể kiểm tra trong Command Prompt:

```bat
py -3.11 --version
node --version
npm --version
code --version
```

## 2. Mở đúng workspace

Cách nhanh nhất:

```text
Nhấp đúp open_vscode.bat
```

Hoặc mở VS Code rồi chọn:

```text
File → Open Workspace from File... → helmet-detection.code-workspace
```

Khi VS Code hỏi **Do you trust the authors of the files in this folder?**, chỉ chọn Trust khi đây là bộ mã nguồn bạn đã kiểm tra và tin cậy. Tasks và debugger cần workspace được tin cậy để chạy script.

## 3. Cài extension được đề xuất

Khi mở workspace lần đầu, VS Code sẽ đề xuất các extension trong `.vscode/extensions.json`:

- Python
- Pylance
- Python Debugger
- Prettier
- DotENV

Chọn **Install All**.

## 4. Chạy toàn bộ hệ thống bằng F5

1. Mở mục **Run and Debug** bằng `Ctrl+Shift+D`.
2. Chọn cấu hình:

```text
Toàn hệ thống: Backend + Frontend
```

3. Nhấn `F5`.

Lần chạy đầu, VS Code tự động:

- Tạo `backend/.venv`.
- Tạo `backend/.env` và `frontend/.env` nếu chưa có.
- Cài thư viện Python.
- Chạy `npm install` cho frontend.
- Kiểm tra model `backend/models/best.pt`.
- Khởi động FastAPI tại cổng 8000.
- Khởi động React/Vite tại cổng 5173.
- Mở giao diện trên trình duyệt.

Địa chỉ sử dụng:

```text
Giao diện : http://localhost:5173
API docs : http://localhost:8000/docs
API health: http://localhost:8000/api/health
```

Dừng cả backend và frontend bằng `Shift+F5` hoặc nút **Stop** trong thanh Debug.

## 5. Đặt breakpoint và debug backend

- Đặt breakpoint trong các file thuộc `backend/app/`.
- Chạy cấu hình **Toàn hệ thống: Backend + Frontend**.
- Thao tác trên giao diện hoặc gọi API.
- VS Code sẽ dừng tại breakpoint trong FastAPI service/route đang được gọi.

Model AI được nạp từ:

```text
backend/models/best.pt
```

Cấu hình nằm trong:

```text
backend/.env
```

## 6. Các task có sẵn

Mở Command Palette bằng `Ctrl+Shift+P`, chọn **Tasks: Run Task**, sau đó chọn:

```text
VS Code: Cài đặt / cập nhật môi trường
VS Code: Cài đặt lại toàn bộ thư viện
Backend: Kiểm tra model và cấu hình
Backend: Chạy kiểm thử
Frontend: Build
Mở API docs
```

Phím tắt:

- `Ctrl+Shift+B`: build frontend.
- `Ctrl+Shift+P` → **Tasks: Run Test Task**: chạy pytest backend.

## 7. Chạy riêng từng phần

Sau khi đã chạy task cài đặt ít nhất một lần:

### Chỉ backend

Trong **Run and Debug**, chọn:

```text
Backend: FastAPI (Debug)
```

### Chỉ frontend

Trong **Run and Debug**, chọn:

```text
Frontend: React + Vite
```

## 8. Lỗi thường gặp

### Không tìm thấy `py.exe`

Cài Python 3.11 x64, bật lựa chọn thêm Python vào PATH, sau đó đóng và mở lại VS Code.

### Không tìm thấy `npm.cmd`

Cài Node.js LTS, sau đó đóng và mở lại VS Code.

### PowerShell chặn script

Các task đã gọi PowerShell với `-ExecutionPolicy Bypass`. Có thể chạy trực tiếp:

```bat
setup_vscode.bat
```

### Cổng 8000 hoặc 5173 đang được sử dụng

Dừng tiến trình cũ trong terminal VS Code. Có thể kiểm tra bằng:

```bat
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```

Sau đó dừng PID tương ứng:

```bat
taskkill /PID <PID> /F
```

### VS Code không nhận đúng Python interpreter

Nhấn `Ctrl+Shift+P`, chọn **Python: Select Interpreter**, rồi chọn:

```text
backend\.venv\Scripts\python.exe
```

### Model chạy chậm

Trong `backend/.env`, tăng:

```env
VIDEO_FRAME_STRIDE=2
```

hoặc `3` khi chạy CPU. Nếu máy có NVIDIA GPU và đã cài đúng PyTorch CUDA, đặt:

```env
DEVICE=0
```
