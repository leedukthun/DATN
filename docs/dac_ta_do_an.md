# ĐẶC TẢ XÂY DỰNG HỆ THỐNG -- ĐỒ ÁN PHÁT HIỆN KHÔNG ĐỘI MŨ BẢO HIỂM

## 1. Bối cảnh và mục tiêu

Đây là tài liệu yêu cầu để Claude Code xây dựng hệ thống Web cho đồ án
tốt nghiệp.

**Lưu ý quan trọng:** - Tên đề tài đã được duyệt, KHÔNG được tự ý thay
đổi tên đề tài. - Trọng tâm của hệ thống là **phát hiện người điều khiển
xe máy không đội mũ bảo hiểm bằng thị giác máy tính**. - Phần thống kê
chỉ là chức năng hỗ trợ, chiếm tỷ trọng nhỏ. Mục đích của thống kê là
tổng hợp các kết quả vi phạm theo vị trí và thời gian, qua đó thể hiện
hệ thống được dùng để hỗ trợ giám sát/ghi nhận vi phạm. - Không biến hệ
thống thành một phần mềm phân tích giao thông tổng quát. - Hệ thống được
phép sử dụng model AI có sẵn. Không yêu cầu phải tự huấn luyện model. -
Model AI phải được thiết kế theo kiểu có thể thay thế dễ dàng. Ban đầu
có thể dùng model hiện có hoặc model pretrained được lựa chọn sau. - Ưu
tiên kiến trúc rõ ràng, dễ chạy bằng VS Code trên Windows, dễ demo và dễ
mở rộng.

------------------------------------------------------------------------

# 2. Mục tiêu chính của hệ thống

Hệ thống cho phép người dùng:

1.  Tạo và quản lý các **Dự án**.
2.  Trong mỗi dự án tạo/quản lý nhiều **Địa điểm**.
3.  Upload một hoặc nhiều **ảnh/video giao thông**.
4.  Gắn dữ liệu upload với:
    -   Dự án
    -   Địa điểm
    -   Ngày dữ liệu
    -   Khung giờ dữ liệu
5.  Chạy model AI để phát hiện:
    -   Xe máy
    -   Người/đầu người hoặc đối tượng liên quan
    -   Trạng thái đội mũ / không đội mũ tùy theo model được sử dụng
6.  Xác định trường hợp **vi phạm không đội mũ bảo hiểm**.
7.  Lưu ảnh bằng chứng của trường hợp vi phạm.
8.  Lưu kết quả phân tích và thông tin metadata vào database.
9.  Cho phép xem lại dữ liệu đã phân tích.
10. Cho phép tải dữ liệu kết quả về máy.
11. Có thống kê cơ bản:
    -   Tổng số phương tiện
    -   Tổng số phương tiện vi phạm
    -   Tỷ lệ vi phạm
    -   Số vi phạm theo khung giờ
    -   Khung giờ có nhiều vi phạm nhất
    -   Có thể xem theo từng địa điểm.

------------------------------------------------------------------------

# 3. Tư duy nghiệp vụ chính

Cấu trúc dữ liệu:

``` text
DỰ ÁN
  │
  ├── ĐỊA ĐIỂM A
  │      ├── Phiên phân tích 1
  │      ├── Phiên phân tích 2
  │      └── ...
  │
  └── ĐỊA ĐIỂM B
         ├── Phiên phân tích 1
         ├── Phiên phân tích 2
         └── ...
```

Một phiên phân tích gồm:

``` text
Dự án
+
Địa điểm
+
Ngày
+
Khung giờ
+
Một hoặc nhiều ảnh/video
        ↓
      AI xử lý
        ↓
Kết quả phát hiện
        ↓
Các trường hợp vi phạm
        ↓
Ảnh bằng chứng
        ↓
Thống kê phiên
```

------------------------------------------------------------------------

# 4. Luồng người dùng

## 4.1. Tạo dự án

Người dùng chọn:

**Dự án → Tạo dự án**

Thông tin: - Tên dự án - Mô tả (không bắt buộc)

Ví dụ:

``` text
Dự án: Theo dõi vi phạm khu vực Nguyễn Trãi
```

Sau khi tạo, dự án có thể có nhiều địa điểm.

------------------------------------------------------------------------

## 4.2. Quản lý địa điểm

Trong một dự án:

``` text
Dự án Nguyễn Trãi
├── Địa điểm A
├── Địa điểm B
└── + Thêm địa điểm
```

Thông tin địa điểm: - Tên địa điểm - Mô tả - Có thể bổ sung tọa độ nếu
cần, nhưng không bắt buộc ở phiên bản đầu.

Không được hard-code "Địa điểm A", "Địa điểm B". Đây chỉ là ví dụ. Người
dùng phải có thể thêm địa điểm động.

------------------------------------------------------------------------

## 4.3. Upload ảnh/video

Người dùng chọn:

``` text
Dự án
↓
Địa điểm
↓
Ngày dữ liệu
↓
Khung giờ dữ liệu
↓
Upload một hoặc nhiều ảnh/video
↓
Bắt đầu phân tích
```

Giao diện upload cần hỗ trợ: - Kéo thả file - Chọn nhiều file - Hiển thị
danh sách file đã chọn - Xóa file khỏi danh sách trước khi xử lý - Hiển
thị trạng thái xử lý

Thông tin phiên phân tích:

``` text
Dự án:       Dự án A
Địa điểm:    Địa điểm A
Ngày:        12/08/2026
Khung giờ:   17:00 - 18:00
Files:       image01.jpg, video01.mp4, ...
```

**Không yêu cầu người dùng nhập tên dự án mỗi lần upload.** Người dùng
phải chọn một dự án đã tồn tại hoặc tạo dự án trước.

------------------------------------------------------------------------

# 5. Xử lý AI

## 5.1. Kiến trúc AI

AI là một module độc lập:

``` text
Input image/video
       ↓
AI Detector
       ↓
Detection Results
       ↓
Violation Logic
       ↓
Evidence + Statistics
```

Không viết logic AI trực tiếp trong API route.

Nên có module kiểu:

``` text
backend/
  app/
    services/
      ai/
        detector.py
        violation.py
        tracker.py
```

Model phải được thiết kế để có thể thay thế.

Ví dụ:

``` python
class Detector:
    def predict_image(...):
        ...

    def predict_video(...):
        ...
```

Sau này có thể thay model mà không phải viết lại toàn bộ hệ thống.

------------------------------------------------------------------------

# 6. Xác định vi phạm

Nếu model sử dụng các class:

``` text
motorcycle
helmet
no_helmet
```

thì cần có lớp xử lý kết quả:

``` text
motorcycle
    +
no_helmet
    ↓
VI PHẠM
```

Không chỉ dựa vào việc có một bounding box `no_helmet` trong ảnh.

Cần có logic liên kết đối tượng để giảm false positive, ví dụ dựa
trên: - Vị trí tương đối - Khoảng cách giữa tâm bounding box - Vùng phía
trên xe - Kích thước bounding box - IoU khi phù hợp

Logic này phải nằm riêng trong `violation.py` hoặc module tương đương để
dễ điều chỉnh.

------------------------------------------------------------------------

# 7. Xử lý video

Video phải được xử lý theo frame.

Luồng:

``` text
Video
 ↓
OpenCV đọc frame
 ↓
AI Detection
 ↓
Violation Logic
 ↓
Tracking (nếu cần)
 ↓
Vẽ kết quả
 ↓
Xuất video kết quả
 ↓
Lưu ảnh bằng chứng
```

## Tránh đếm trùng

Một phương tiện xuất hiện trong nhiều frame không được tính thành nhiều
phương tiện.

Nên hỗ trợ object tracking, ưu tiên: - ByteTrack - BoT-SORT - Hoặc
tracking có sẵn của Ultralytics nếu phù hợp.

Ví dụ:

``` text
Frame 1 → Vehicle ID 001
Frame 2 → Vehicle ID 001
Frame 3 → Vehicle ID 001
...
```

Kết quả thống kê chỉ tính phương tiện theo ID thay vì đếm từng bounding
box/frame.

Nếu phiên bản đầu chưa triển khai tracking hoàn chỉnh, code phải được
thiết kế để có thể bổ sung sau.

------------------------------------------------------------------------

# 8. Ảnh bằng chứng vi phạm

Khi phát hiện vi phạm, hệ thống cần lưu ảnh bằng chứng.

Ví dụ:

``` text
storage/
  violations/
    2026-08-12/
      project_001/
        location_001/
          violation_001.jpg
          violation_002.jpg
          violation_003.jpg
```

Ảnh bằng chứng nên: - Có bounding box - Có trạng thái `NO HELMET` - Có
confidence nếu phù hợp - Có thể chứa timestamp/frame number đối với
video

Không cần lưu tất cả frame của video. Chỉ lưu các frame/ảnh đại diện cho
vi phạm.

------------------------------------------------------------------------

# 9. Kết quả sau khi phân tích

Sau khi xử lý một phiên:

``` text
Tổng phương tiện:       125
Có đội mũ:               102
Không đội mũ:             23
Tỷ lệ vi phạm:          18.4%
```

Đối với ảnh:

``` text
Ảnh gốc
↓
Ảnh kết quả có bounding box
↓
Ảnh bằng chứng vi phạm
```

Đối với video:

``` text
Video gốc
↓
Video kết quả có bounding box/tracking
↓
Ảnh bằng chứng vi phạm
```

------------------------------------------------------------------------

# 10. Cấu trúc giao diện

## 10.1. Trang chính

Tên hiển thị:

``` text
PHÁT HIỆN KHÔNG ĐỘI MŨ
```

Bố cục theo ý tưởng UI hiện tại:

``` text
┌─────────────────────────────────────────────────────────┐
│                 PHÁT HIỆN KHÔNG ĐỘI MŨ                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ [ Upload Ảnh/Video ]                                   │
│                                                         │
│ ┌──────────────────────┐                                │
│ │                      │                                │
│ │  Kéo thả ảnh/video   │                                │
│ │                      │                                │
│ └──────────────────────┘                                │
│                                                         │
│                         ┌──────────────────────────────┐ │
│                         │           DỰ ÁN              │ │
│                         ├──────────────────────────────┤ │
│                         │ Địa điểm A                   │ │
│                         │ Địa điểm B                   │ │
│                         │ + Thêm địa điểm              │ │
│                         │                              │ │
│                         │ [Tải dữ liệu về máy]         │ │
│                         └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

------------------------------------------------------------------------

# 11. Trang upload

Popup/form:

``` text
┌────────────────────────────────┐
│      THÔNG TIN DỮ LIỆU         │
├────────────────────────────────┤
│ Dự án                          │
│ [ Dự án A ▼ ]                  │
│                                │
│ Vị trí                         │
│ [ Địa điểm A ▼ ]               │
│                                │
│ Ngày dữ liệu                   │
│ [ 12/08/2026 ]                 │
│                                │
│ Khung giờ                      │
│ [ 17:00 ] - [ 18:00 ]          │
│                                │
│ ┌────────────────────────────┐ │
│ │ Kéo thả ảnh/video          │ │
│ │ hoặc click để chọn file    │ │
│ └────────────────────────────┘ │
│                                │
│       [ BẮT ĐẦU PHÂN TÍCH ]   │
└────────────────────────────────┘
```

------------------------------------------------------------------------

# 12. Trang chi tiết địa điểm

Khi click vào:

``` text
Địa điểm A
```

hiển thị:

``` text
DỰ ÁN: ABC
ĐỊA ĐIỂM: A

Tổng dữ liệu:              25
Tổng phương tiện:        1250
Tổng vi phạm:              187
Tỷ lệ vi phạm:            14.96%

DỮ LIỆU ĐÃ PHÂN TÍCH

Ngày        Khung giờ       File        Vi phạm
12/08       07:00-08:00     data01      15
12/08       08:00-09:00     data02      21
12/08       17:00-18:00     data03      63
```

Có nút:

``` text
[Xem chi tiết]
```

------------------------------------------------------------------------

# 13. Trang dữ liệu vi phạm

Hiển thị danh sách ảnh bằng chứng:

``` text
┌──────────┬──────────┬──────────┐
│ Ảnh 01   │ Ảnh 02   │ Ảnh 03   │
│ 17:32:10 │ 17:33:15 │ 17:35:21 │
├──────────┼──────────┼──────────┤
│ Ảnh 04   │ Ảnh 05   │ Ảnh 06   │
└──────────┴──────────┴──────────┘
```

Click vào ảnh:

``` text
Thời gian: 17:32:10
Địa điểm: Địa điểm A
Confidence: 0.91
Trạng thái: Không đội mũ
```

------------------------------------------------------------------------

# 14. Thống kê

Thống kê là chức năng phụ, không phải trung tâm hệ thống.

Chỉ cần các nội dung:

## Tổng quan

``` text
Tổng phương tiện:       1250
Tổng vi phạm:             187
Tỷ lệ vi phạm:           14.96%
```

## Theo khung giờ

Ví dụ:

``` text
07:00 - 08:00      15
08:00 - 09:00      23
09:00 - 10:00      12
...
17:00 - 18:00      51
18:00 - 19:00      63
19:00 - 20:00      42
```

Kết luận:

``` text
Khung giờ có nhiều vi phạm nhất:
18:00 - 19:00
```

## Theo địa điểm

``` text
Địa điểm A: 187
Địa điểm B: 124
```

Không cần xây dựng các thuật toán thống kê phức tạp.

------------------------------------------------------------------------

# 15. Tải dữ liệu về máy

Chức năng:

``` text
TẢI DỮ LIỆU VỀ MÁY
```

Có thể cho phép: - Tải ảnh kết quả - Tải video kết quả - Tải ảnh bằng
chứng vi phạm - Có thể bổ sung xuất CSV/Excel/PDF ở giai đoạn sau

Ưu tiên hoàn thành tải ảnh/video trước.

------------------------------------------------------------------------

# 16. Database

Đề xuất sử dụng:

**PostgreSQL**, có thể triển khai thông qua **Supabase**.

## Bảng `projects`

``` text
id
name
description
created_at
updated_at
```

## Bảng `locations`

``` text
id
project_id
name
description
latitude       (nullable)
longitude      (nullable)
created_at
updated_at
```

Quan hệ:

``` text
projects 1 ---- N locations
```

## Bảng `analysis_sessions`

Mỗi lần người dùng upload một nhóm dữ liệu sẽ tạo một session.

``` text
id
location_id
analysis_date
start_time
end_time
total_files
total_vehicles
helmet_count
no_helmet_count
violation_count
violation_rate
status
created_at
completed_at
```

Quan hệ:

``` text
locations 1 ---- N analysis_sessions
```

## Bảng `media_files`

``` text
id
session_id
original_filename
file_type
original_file_url
result_file_url
status
created_at
```

Quan hệ:

``` text
analysis_sessions 1 ---- N media_files
```

## Bảng `violations`

``` text
id
session_id
media_id
vehicle_id
frame_number
timestamp
confidence
status
evidence_image_url
created_at
```

Quan hệ:

``` text
analysis_sessions 1 ---- N violations
media_files 1 ---- N violations
```

`vehicle_id`, `frame_number` có thể nullable đối với ảnh nếu không cần.

------------------------------------------------------------------------

# 17. Backend

Ưu tiên:

``` text
Python
FastAPI
Ultralytics
OpenCV
PostgreSQL / Supabase
```

Cấu trúc đề xuất:

``` text
backend/
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── projects.py
│   │   ├── locations.py
│   │   ├── uploads.py
│   │   ├── analyses.py
│   │   ├── violations.py
│   │   └── statistics.py
│   │
│   ├── services/
│   │   ├── ai/
│   │   │   ├── detector.py
│   │   │   ├── violation.py
│   │   │   └── tracker.py
│   │   ├── image_processor.py
│   │   ├── video_processor.py
│   │   ├── evidence_service.py
│   │   └── statistics_service.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   └── core/
│
├── models/
│   └── model.pt
│
├── storage/
│   ├── uploads/
│   ├── results/
│   └── violations/
│
├── requirements.txt
└── .env.example
```

------------------------------------------------------------------------

# 18. Frontend

Có thể dùng:

``` text
React + Vite
```

Ưu tiên giao diện: - Gọn - Hiện đại - Dễ demo - Responsive - Không quá
nhiều animation - Tập trung vào luồng upload → xử lý → kết quả → lưu
trữ.

Cấu trúc:

``` text
frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard
│   │   ├── Upload
│   │   ├── ProjectDetail
│   │   ├── LocationDetail
│   │   ├── AnalysisDetail
│   │   └── Violations
│   │
│   ├── components/
│   ├── services/
│   ├── hooks/
│   └── types/
└── ...
```

------------------------------------------------------------------------

# 19. API dự kiến

## Projects

``` http
GET    /api/projects
POST   /api/projects
GET    /api/projects/{id}
PUT    /api/projects/{id}
DELETE /api/projects/{id}
```

## Locations

``` http
GET    /api/projects/{project_id}/locations
POST   /api/projects/{project_id}/locations
GET    /api/locations/{id}
PUT    /api/locations/{id}
DELETE /api/locations/{id}
```

## Upload / Analysis

``` http
POST /api/analyses
GET  /api/analyses/{id}
GET  /api/analyses/{id}/status
GET  /api/analyses/{id}/results
```

Upload request phải chứa: - project_id - location_id - analysis_date -
start_time - end_time - files\[\]

## Violations

``` http
GET /api/locations/{id}/violations
GET /api/analyses/{id}/violations
GET /api/violations/{id}
```

## Statistics

``` http
GET /api/locations/{id}/statistics
GET /api/projects/{id}/statistics
```

------------------------------------------------------------------------

# 20. Trạng thái xử lý

Do video có thể mất thời gian xử lý, không nên để frontend chờ HTTP
request quá lâu.

Session nên có status:

``` text
PENDING
PROCESSING
COMPLETED
FAILED
```

Frontend có thể polling:

``` text
GET /api/analyses/{id}/status
```

Ví dụ:

``` text
PROCESSING 45%
```

Sau khi hoàn thành:

``` text
COMPLETED
```

------------------------------------------------------------------------

# 21. Lưu trữ file

Trong môi trường local:

``` text
storage/
├── uploads/
├── results/
└── violations/
```

Nếu dùng Supabase Storage thì có thể chuyển sang:

``` text
uploads/
results/
violations/
```

Database chỉ lưu URL/path của file, không lưu binary trực tiếp trong
PostgreSQL.

------------------------------------------------------------------------

# 22. Yêu cầu quan trọng về model

Không hard-code model cụ thể vào toàn bộ hệ thống.

Model phải có thể cấu hình qua `.env`:

``` env
MODEL_PATH=./models/model.pt
CONFIDENCE_THRESHOLD=0.4
IOU_THRESHOLD=0.5
```

Nếu sau này đổi model:

``` text
model.pt
```

chỉ cần thay file/config.

Hệ thống phải hỗ trợ model có sẵn và không phụ thuộc vào việc model được
train trong project này.

------------------------------------------------------------------------

# 23. Xử lý confidence và IoU

Các giá trị mặc định chỉ là giá trị ban đầu:

``` text
confidence = 0.4
IoU = 0.5
```

Phải cho phép điều chỉnh qua `.env` hoặc config.

Không được coi các giá trị này là tối ưu tuyệt đối.

Sau khi chọn model thực tế, cần test và điều chỉnh.

------------------------------------------------------------------------

# 24. Yêu cầu về trải nghiệm

Khi upload:

``` text
Đã chọn 5 file
```

Hiển thị:

``` text
image01.jpg     ✓
image02.jpg     ✓
video01.mp4     ✓
...
```

Khi xử lý:

``` text
Đang xử lý...
image01.jpg      100%
image02.jpg      100%
video01.mp4       63%
```

Khi hoàn thành:

``` text
Phân tích hoàn tất

Tổng phương tiện: 125
Vi phạm: 23

[ Xem kết quả ]
[ Xem ảnh vi phạm ]
```

------------------------------------------------------------------------

# 25. Không cần làm ở phiên bản đầu

Không cần triển khai ngay: - Đăng nhập/role phức tạp - AI tự động
retrain - Phân tích giao thông tổng quát - Nhận diện biển số - Phạt
nguội - OCR - Bản đồ GIS phức tạp - Thống kê nâng cao - Mobile app

Tập trung hoàn thành:

``` text
Project
→ Location
→ Upload
→ AI Detection
→ Violation
→ Evidence
→ Storage
→ View Result
→ Basic Statistics
→ Download
```

------------------------------------------------------------------------

# 26. Tiêu chí hoàn thành MVP

MVP được xem là hoàn thành khi có thể thực hiện đầy đủ:

``` text
1. Tạo project
       ↓
2. Tạo location
       ↓
3. Upload nhiều ảnh/video
       ↓
4. Chọn ngày + khung giờ
       ↓
5. AI xử lý
       ↓
6. Hiển thị kết quả
       ↓
7. Phát hiện trường hợp không đội mũ
       ↓
8. Lưu ảnh bằng chứng
       ↓
9. Lưu database
       ↓
10. Xem lại lịch sử
       ↓
11. Xem thống kê cơ bản
       ↓
12. Tải kết quả về máy
```

------------------------------------------------------------------------

# 27. Thứ tự Claude Code nên triển khai

Không viết toàn bộ hệ thống một lần.

### Phase 1 -- Khởi tạo project

-   Frontend React + Vite
-   Backend FastAPI
-   Database connection
-   `.env`
-   Cấu trúc thư mục

### Phase 2 -- Database

-   projects
-   locations
-   analysis_sessions
-   media_files
-   violations
-   migration/schema

### Phase 3 -- Project/Location

-   CRUD project
-   CRUD location
-   UI quản lý project/location

### Phase 4 -- Upload

-   Upload nhiều ảnh/video
-   Chọn project/location
-   Ngày/khung giờ
-   File validation

### Phase 5 -- AI

-   Tạo detector service
-   Load model từ `MODEL_PATH`
-   Image inference
-   Video inference
-   Violation logic

### Phase 6 -- Evidence

-   Lưu ảnh vi phạm
-   Lưu result image/video
-   Lưu database

### Phase 7 -- Result

-   Trang kết quả
-   Danh sách vi phạm
-   Xem ảnh/video

### Phase 8 -- Tracking

-   Tracking video
-   Vehicle ID
-   Tránh đếm trùng

### Phase 9 -- Statistics

-   Tổng phương tiện
-   Tổng vi phạm
-   Tỷ lệ
-   Theo khung giờ
-   Khung giờ cao nhất
-   Theo địa điểm

### Phase 10 -- Download

-   Tải ảnh
-   Tải video
-   Có thể thêm CSV/Excel/PDF nếu còn thời gian

### Phase 11 -- Polish

-   Loading
-   Error handling
-   Empty states
-   Responsive
-   UI hoàn thiện
-   README
-   Hướng dẫn chạy

------------------------------------------------------------------------

# 28. Nguyên tắc khi Claude Code triển khai

1.  Không tự ý đổi tên đề tài.
2.  Không tự ý đổi nghiệp vụ chính.
3.  Không hard-code địa điểm A/B.
4.  Không hard-code project.
5.  Không đặt AI inference trực tiếp trong route.
6.  Tách AI service khỏi business logic.
7.  Tách database/repository khỏi API.
8.  Model phải có thể thay thế.
9.  Không lưu binary file trực tiếp trong database.
10. Không để video inference block API quá lâu nếu có thể tránh.
11. Có xử lý lỗi khi file không hợp lệ.
12. Có kiểm tra định dạng file.
13. Có giới hạn kích thước file phù hợp.
14. Code phải dễ đọc, dễ bảo trì.
15. Ưu tiên hoàn thành MVP trước rồi mới bổ sung tính năng.

------------------------------------------------------------------------

# 29. Kiến trúc tổng thể

``` text
                         USER
                           │
                           ▼
                  ┌─────────────────┐
                  │    FRONTEND     │
                  │ React + Vite    │
                  └────────┬────────┘
                           │ REST API
                           ▼
                  ┌─────────────────┐
                  │     FASTAPI     │
                  └────────┬────────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
          Project       Analysis       Statistics
          Service        Service         Service
                           │
                           ▼
                     ┌───────────┐
                     │ AI Module │
                     └─────┬─────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
                 Detector      Tracker
                    │             │
                    └──────┬──────┘
                           ▼
                   Violation Logic
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          Evidence       Results      Statistics
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                    PostgreSQL
                    / Supabase
                           │
                           ▼
                      File Storage
```

------------------------------------------------------------------------

# 30. Kết luận nghiệp vụ

Hệ thống này không phải một hệ thống thống kê giao thông tổng quát.

**Mục đích cốt lõi:**

> Sử dụng thị giác máy tính để hỗ trợ phát hiện người điều khiển xe máy
> không đội mũ bảo hiểm từ ảnh/video.

Các chức năng: - Quản lý dự án - Quản lý địa điểm - Upload dữ liệu -
Chọn thời gian dữ liệu - AI detection - Xác định vi phạm - Lưu ảnh bằng
chứng - Lưu trữ kết quả - Tra cứu dữ liệu - Thống kê cơ bản - Tải kết
quả

được xây dựng để hỗ trợ mục tiêu cốt lõi trên.

**Claude Code cần xây dựng hệ thống theo đúng đặc tả này, ưu tiên MVP
chạy được end-to-end trước, sau đó mới tối ưu UI và bổ sung tính năng.**
