# Đối chiếu đặc tả và phần đã triển khai

## Hoàn thành trong MVP

| Yêu cầu | Thành phần triển khai |
|---|---|
| Dự án có nhiều địa điểm động | `projects`, `locations`, Project Explorer UI |
| Upload nhiều ảnh/video | `POST /api/analyses`, `UploadModal`, drag & drop |
| Ngày + khung giờ | `analysis_date`, `start_time`, `end_time` |
| AI tách khỏi API | `services/ai/detector.py`, `image_processor.py`, `video_processor.py` |
| Model thay thế qua config | `MODEL_PATH` và mapping class trong `.env` |
| Xác định vi phạm | `services/ai/violation.py` |
| Video theo frame | OpenCV trong `video_processor.py` |
| Tránh đếm trùng | `CentroidTracker` trong `services/ai/tracker.py` |
| Lưu bằng chứng | `evidence_service.py`, bảng `violations` |
| Kết quả ảnh/video | `storage/results` và trang Analysis Detail |
| Polling trạng thái | Frontend gọi lại `GET /api/analyses/{id}` |
| Thống kê cơ bản | `statistics_service.py`, tab thống kê |
| Tải dữ liệu | ZIP theo phiên/địa điểm/dự án |
| PostgreSQL/Supabase-ready | `DATABASE_URL`, SQLAlchemy, psycopg |
| Responsive UI | CSS desktop/tablet/mobile |

## Chủ ý thiết kế

- SQLite là mặc định để đồ án chạy ngay trên Windows; không khóa hệ thống vào SQLite.
- Model do người dùng cung cấp nằm ở `backend/models/best.pt`.
- Logic class name có thể chỉnh trong `.env`.
- Binary không lưu vào database.
- API request upload trả về nhanh; xử lý chạy sau response bằng BackgroundTasks.
- Giao diện thống kê chỉ hỗ trợ mục tiêu phát hiện vi phạm, không biến thành hệ thống phân tích giao thông tổng quát.

## Nâng cấp tiếp theo phù hợp cho bản bảo vệ/triển khai thật

1. Thay centroid tracker bằng ByteTrack hoặc BoT-SORT.
2. Dùng Redis + Celery/RQ cho hàng đợi video.
3. Dùng PostgreSQL/Supabase và object storage.
4. Thêm migration bằng Alembic.
5. Thêm đăng nhập đơn giản nếu hội đồng yêu cầu.
6. Hiệu chỉnh threshold bằng bộ dữ liệu test thực tế.
7. Thêm test integration với các ảnh/video mẫu được phép sử dụng.

## UI scroll fix
- Upload modal now has a guaranteed scrollable body on short laptop screens.
- The overlay supports vertical scrolling and mobile touch scrolling.
- Large upload modal uses a viewport-bounded height (`dvh`) so the action buttons remain reachable.
- Body scroll locking now restores the previous value when the modal closes.
