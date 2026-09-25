# Sơ đồ cơ sở dữ liệu mức vật lý

Nguồn: `backend/helmet_detection.db`, đọc qua kết nối SQLite `mode=ro`.

- `physical_erd.png`: ảnh 5320 × 3760 px, gắn metadata 300 DPI, dùng để chèn vào báo cáo.
- `physical_erd.svg`: bản vector, có thể phóng to mà không vỡ hình.
- `physical_erd.drawio`: bản chỉnh sửa trong diagrams.net; các bảng, từng ô dữ liệu và đường nối đều là đối tượng gốc. Mở bằng File → Open from → Device. Bấm đúp ô để sửa nội dung; đường nối được gắn vào hàng PK/FK và đi theo khi di chuyển bảng.
- `generate_drawio.py`: tạo lại tệp `.drawio` từ `schema_snapshot.json` bằng thư viện chuẩn Python.
- `schema_snapshot.json`: cấu trúc bảng, cột, khóa ngoại và chỉ mục đã đối chiếu.
- `generate_physical_erd.py`: mã tạo lại sơ đồ từ CSDL hiện tại (cần Python + Pillow và font Arial/Consolas trên Windows).

Sơ đồ giữ nguyên tên bảng và thứ tự cột trong SQLite: 6 bảng, 62 cột, 6 PK, 5 FK, 14 cột nullable.

## Khác biệt giữa SQLite hiện tại và model SQLAlchemy

1. `projects.owner_id` cho phép NULL nhưng chưa có FK hoặc chỉ mục. Đường nét đứt chỉ mô tả tham chiếu theo model, không phải FK vật lý.
2. SQLite hiện có UNIQUE trên `projects.name` toàn bảng. Model lại khai báo UNIQUE trên `(owner_id, name)`.
3. Cả 5 FK thực tế đều ON DELETE CASCADE, ON UPDATE NO ACTION. Ứng dụng bật `PRAGMA foreign_keys=ON` khi kết nối.
4. Không cột nào có DEFAULT ở tầng CSDL; các default trong model được SQLAlchemy cung cấp.
5. Kiểu dữ liệu trên sơ đồ là kiểu khai báo thực tế trong SQLite. TEXT được dùng cho các trường JSON.

## Chỉ mục thực tế

| Bảng | Chỉ mục | Cột | Duy nhất |
|---|---|---|---|
| `users` | `ix_users_username` | `username` | Có |
| `users` | `ix_users_id` | `id` | Không |
| `projects` | `ix_projects_name` | `name` | Có |
| `projects` | `ix_projects_id` | `id` | Không |
| `locations` | `ix_locations_project_id` | `project_id` | Không |
| `locations` | `ix_locations_id` | `id` | Không |
| `locations` | `ix_locations_name` | `name` | Không |
| `locations` | `sqlite_autoindex_locations_1` | `project_id, name` | Có |
| `analysis_sessions` | `ix_analysis_sessions_location_id` | `location_id` | Không |
| `analysis_sessions` | `ix_analysis_sessions_status` | `status` | Không |
| `analysis_sessions` | `ix_analysis_sessions_analysis_date` | `analysis_date` | Không |
| `analysis_sessions` | `ix_analysis_sessions_id` | `id` | Không |
| `media_files` | `ix_media_files_id` | `id` | Không |
| `media_files` | `ix_media_files_session_id` | `session_id` | Không |
| `violations` | `ix_violations_media_id` | `media_id` | Không |
| `violations` | `ix_violations_session_id` | `session_id` | Không |
| `violations` | `ix_violations_id` | `id` | Không |

## Chú thích đề xuất dưới hình trong báo cáo

Hình: Sơ đồ cơ sở dữ liệu mức vật lý của hệ thống phát hiện không đội mũ bảo hiểm, theo SQLite hiện tại. Đường nét đứt thể hiện liên kết trong model chưa được áp dụng thành ràng buộc khóa ngoại trong CSDL.
