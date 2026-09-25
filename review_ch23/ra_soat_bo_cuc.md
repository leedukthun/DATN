# Rà soát và bố cục lại chương 2 và chương 3

Báo cáo đồ án hệ thống phát hiện trường hợp đi xe máy không đội mũ bảo hiểm

## 1 Kết luận rà soát

Chương 2 và chương 3 hiện có đủ nhiều nội dung để xây dựng mạch trình bày hợp lý, nhưng ranh giới giữa cơ sở lý thuyết, thiết kế và triển khai chưa rõ. Chương 2 mô tả khá sâu cách hệ thống đang xử lý, trong khi chương 3 nhắc lại các bước đó ở mức khái quát. Vì vậy, cần chuyển phần lựa chọn giải pháp và quy tắc xử lý cụ thể sang chương 3, chuyển cấu hình cùng thao tác thực hiện sang chương 4, rồi rút gọn phần giới thiệu lặp lại.

Tài liệu được đối chiếu là CNTT_2022606983_LeDucThuan_BaoCao.docx. Các nhận xét dùng số mục hiện tại của bản này; các phần đề cương ghi rõ số mục mới. Phạm vi rà soát gồm toàn bộ chương 2, chương 3, các hình và bảng liên quan, đồng thời đối chiếu nội dung chương 4 để xác định nơi chuyển đến.

### 1.1 Phân vai ba chương

| Chương | Câu hỏi cần trả lời | Nội dung phù hợp |
| --- | --- | --- |
| Chương 2 | Kiến thức và nguyên lý nào làm nền tảng? | Khái niệm, nguyên lý YOLO, dữ liệu và fine-tuning, quan hệ không gian, tracking, chỉ số đánh giá, đặc điểm công nghệ. |
| Chương 3 | Đề tài vận dụng các cơ sở đó như thế nào? | Yêu cầu, lựa chọn phương án ba lớp, kiến trúc, thuật toán liên kết và xác nhận, mô hình dữ liệu, quy tắc thống kê, thiết kế giao diện. |
| Chương 4 | Đã thực hiện ra sao và kết quả thế nào? | Dữ liệu thực tế, môi trường, giá trị tham số, huấn luyện, tích hợp, ảnh chạy ứng dụng, kịch bản và kết quả kiểm thử. |

### 1.2 Điều chỉnh trọng tâm

- Tách mục 2.2 hiện tại: giữ nguyên lý tại chương 2; đưa các công thức và quy tắc đặc thù của đề tài sang một mục thiết kế thuật toán riêng ở chương 3.
- Bổ sung mục lựa chọn phương án mô hình trong chương 3, tiếp nhận phần phát triển từ hai lớp sang ba lớp đang nằm ở 2.1.5.
- Rút phần giới thiệu công nghệ ở 2.3 về chức năng và đặc điểm; đưa cách ghép các thành phần thành hệ thống về thiết kế kiến trúc.
- Rút sự lặp lại giữa bảng yêu cầu, bảng mô tả Use Case, đặc tả Use Case và mô tả giao diện trong chương 3.
- Giữ định nghĩa chỉ số ở chương 2; đưa cách tổ chức phép đánh giá và số liệu đo được sang chương 4.

Một chủ đề có thể xuất hiện ở cả ba chương nếu mỗi lần xuất hiện trả lời một câu hỏi khác nhau. Ví dụ: chương 2 giải thích nguyên lý tracking theo tâm; chương 3 xác định đối tượng nào được theo dõi và cách ghi nhận; chương 4 công bố ngưỡng đã dùng và kết quả sai số đếm.

<!-- PAGE -->
## 2 Những nội dung trùng và cần chuyển vị trí

### 2.1 Mở rộng mô hình hai lớp sang ba lớp

**Vị trí hiện tại:** 2.1.4–2.1.6; 3.1.1; 3.2.2.2; 4.1.2; 4.2.1. Nội dung bổ sung bike, kế thừa trọng số, đồng bộ mã lớp và giảm nhầm người đi bộ được nhắc nhiều lần. Riêng 2.1.5 đã nói đến notebook, đóng băng tham số và cách xử lý trọng số không tương thích.

**Cách sửa:** chương 2 chỉ giữ nguyên lý học chuyển giao và thay đổi số lớp. Chương 3 trình bày lý do chọn ba lớp, đầu vào, đầu ra và giới hạn của phương án. Chương 4 giữ nguồn checkpoint, bảng ánh xạ lớp, cấu hình freeze/resume và minh chứng huấn luyện. Các đoạn giới thiệu ở đầu mục chỉ dẫn chiếu, không giải thích lại toàn bộ động cơ.

### 2.2 Quy trình ảnh và video

**Vị trí hiện tại:** 2.2.1 và 3.2.2.1–3.2.2.5. Cả hai cùng mô tả đọc dữ liệu, nhận diện, liên kết, vẽ kết quả, lưu minh chứng. Mục 2.2.1 còn nêu VideoCapture, VideoWriter và cách ghi các khung không chạy AI.

**Cách sửa:** chương 2 giữ khái niệm khung hình, FPS, lấy mẫu và quan hệ thời gian. Chương 3 có một quy trình tổng thể rồi tách hai nhánh ảnh/video. Tên API thư viện, cách tổ chức vòng lặp và hành vi ghi video thực tế đưa sang 4.3.1.

### 2.3 Liên kết vùng đầu với xe máy

**Vị trí hiện tại:** 2.2.2 và 3.2.2.2. Mục 2.2.2 đã mô tả vùng mở rộng, chọn xe theo khoảng cách, quan hệ một đầu–tối đa một xe và ưu tiên NO_HELMET. Mục 3.2.2.2 lại diễn giải các quy tắc đó.

**Cách sửa:** ở chương 2 giữ cơ sở dùng vị trí tương đối và giới hạn của liên kết hình học. Chuyển công thức vùng liên kết, điểm khoảng cách, quy tắc gán trạng thái sang mục thiết kế thuật toán ở chương 3. Giá trị α = 0,2; β = 0,8; γ = 0,7 thuộc bảng cấu hình chương 4; không trình bày chúng như hằng số lý thuyết.

### 2.4 Tracking và xác nhận qua nhiều khung hình

**Vị trí hiện tại:** 2.2.3–2.2.4 và 3.2.2.4. Chương 2 đang chứa cả chi phí 0,85D, ngưỡng ghép theo kích thước khung hình, bộ đếm liên tiếp, trạng thái đã xác nhận và tập mã đã ghi nhận.

**Cách sửa:** giữ khái niệm tâm, khoảng cách Euclid, ghép đối tượng và khó khăn mất dấu tại chương 2. Đưa thuật toán ghép, đặt lại bộ đếm, điều kiện xác nhận, thời điểm lưu minh chứng và đếm một lần sang chương 3. Giá trị ngưỡng thực dùng và phép kiểm thử độ nhạy thuộc chương 4. Bảng 2.2 nên chuyển cùng phần thiết kế xác nhận để tránh minh họa lại hai lần.

### 2.5 Công nghệ và kiến trúc ứng dụng

**Vị trí hiện tại:** 2.3.3; 3.2.1; 3.3; 4.1.1.2. Backend, frontend, cơ sở dữ liệu và kho tệp đều được kể lại với cùng vai trò. Mục 2.3.3 đã mô tả tác vụ nền, truy vấn tiến độ định kỳ và tổ chức tài nguyên của đề tài.

**Cách sửa:** chương 2 giới thiệu công nghệ; chương 3 giải thích lựa chọn, cách giao tiếp và phân công trách nhiệm; chương 4 ghi phiên bản, môi trường và cách tích hợp đã thực hiện. Cấu trúc dữ liệu cụ thể chỉ trình bày đầy đủ ở phần thiết kế dữ liệu.

<!-- PAGE -->
## 3 Những điểm chưa ổn về nội dung và tính nhất quán

### 3.1 Quy tắc thiếu xe chưa thống nhất với cách mô tả mục tiêu

Mục 2.1.5 viết rằng vùng no-helmet chỉ thành ứng viên khi có quan hệ phù hợp với xe máy. Tuy nhiên, 3.2.2.2 nêu rõ khi không phát hiện xe, chương trình xử lý vùng đầu độc lập. Cần mô tả đầy đủ hai nhánh và điều kiện chuyển nhánh trong thiết kế; không kết luận mọi bản ghi đều đã được xác nhận có ngữ cảnh xe máy. Giữ đúng hành vi đang mô tả và đánh giá nhánh dự phòng ở chương 4. Nếu thay đổi hành vi, phải sửa cả hệ thống và kiểm thử, không chỉ sửa lời văn.

### 3.2 Đơn vị ghi nhận và tên đối tượng cần được chốt

Mục 2.2.2.4, 2.2.4, 3.1.1 và UC05 đã thừa nhận chưa phân biệt người lái với người ngồi sau. Trong nhánh liên kết theo xe, nhiều vùng đầu có thể tạo một trạng thái cho xe; trong nhánh không có xe, đối tượng lại là vùng đầu. Vì vậy, số bản ghi, số mã theo dõi, số xe và số người không đồng nghĩa. Chương 3 cần có quy ước riêng về đơn vị đếm, cách xử lý UNKNOWN và mẫu số của tỷ lệ. Các nhãn giao diện như “Tổng phương tiện”, “Tổng vi phạm” phải phù hợp với quy ước đó.

### 3.3 Thiết kế thuật toán bị đặt ở chương cơ sở

Phần chi tiết nhất của liên kết, ghép tracking và xác nhận hiện ở 2.2; chương 3 chủ yếu tóm tắt. Nên hình thành một mục thiết kế thuật toán liên tục, có đầu vào, đầu ra, các bước và nhánh ngoại lệ. Mục 2.2.3.3 mang tên quản lý đối tượng xuất hiện và mất dấu nhưng chủ yếu nêu hạn chế; phần thiết kế cần làm rõ vòng đời track, điều kiện tạo/xóa và dữ liệu lưu cho mỗi mã.

### 3.4 Chương 3 đang lặp mô tả nghiệp vụ nhiều tầng

Bảng 3.1, Bảng 3.3, tám bảng đặc tả UC01–UC08 và mục 3.4 cùng mô tả thao tác tải dữ liệu, xem kết quả và thống kê. Không cần bỏ hết: bảng yêu cầu giữ mục tiêu và mã CN; danh mục Use Case chỉ giữ mã UC, tên và CN liên quan; đặc tả giữ luồng cùng ngoại lệ; thiết kế giao diện tập trung vào thành phần và trạng thái hiển thị. Có thể chuyển đặc tả thao tác tài khoản, quản lý, tra cứu và tải tệp sang phụ lục, giữ chi tiết UC03, UC04, UC05, UC07 trong chương chính nếu cần rút gọn.

### 3.5 Hình và nội dung thiết kế cần ăn khớp

Hình 3.2 ghi “Mô hình YOLO – Nhận diện & theo dõi”, trong khi văn bản mô tả theo dõi bằng Centroid Tracking riêng. Nên sửa nhãn YOLO thành “Phát hiện đối tượng”, thể hiện liên kết và tracking trong mô-đun xử lý. Hình ERD sáu bảng đã có và nên giữ; bổ sung từ điển dữ liệu, ràng buộc và quy tắc nhất quán giữa session_id và media_id của minh chứng. Các hình “Hình dung màn hình” là bản phác thảo phù hợp chương 3; ảnh ứng dụng chạy thực tế dùng ở chương 4.

### 3.6 Thiết kế thống kê cần được trình bày tập trung

UC07 và 3.2.2.6 đã có các quy tắc quan trọng nhưng phân tán: dùng tệp thành công, thời điểm xác nhận video, giờ bắt đầu phiên và loại ảnh tĩnh khỏi thống kê thời gian chi tiết. Cần gom vào một mục. Phải nêu rõ giới hạn khi nhiều video dùng chung giờ bắt đầu, khi thời điểm vượt khoảng khai báo và khi cộng nhiều tệp có đối tượng lặp. Không diễn giải số liệu gộp thành số người hay phương tiện duy nhất trên nhiều video.

<!-- PAGE -->
## 4 Bố cục mới của chương 2

**Tên chương đề xuất: CHƯƠNG 2 CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ SỬ DỤNG**

### 2.1 Cơ sở phát hiện đối tượng bằng YOLO

**2.1.1 Bài toán phát hiện đối tượng và biểu diễn kết quả.** Giữ phân loại, định vị, hộp giới hạn, nhãn và độ tin cậy từ 2.1.1 cũ; không lặp bối cảnh chương 1.

**2.1.2 Nguyên lý và cấu trúc tổng quát của YOLO.** Giữ nguyên lý một lần truyền tiến, backbone, neck, detection head và hình minh họa; thống nhất phiên bản với mô hình sử dụng.

**2.1.3 Lọc dự đoán và loại bỏ hộp trùng.** Giải thích ngưỡng độ tin cậy và NMS; dẫn định nghĩa IoU ở 2.4.1 mới. Giá trị ngưỡng thực dùng thuộc chương 4.

### 2.2 Cơ sở dữ liệu gán nhãn và huấn luyện tinh chỉnh

**2.2.1 Định dạng nhãn và chất lượng dữ liệu.** Giữ định dạng YOLO, quy tắc và tính nhất quán của nhãn; nêu rõ tọa độ, chiều rộng, chiều cao được chuẩn hóa theo kích thước ảnh.

**2.2.2 Phân chia dữ liệu huấn luyện, xác thực và kiểm thử.** Giữ vai trò từng tập, nguy cơ rò rỉ dữ liệu giữa khung hình gần nhau. Quy mô và nguồn dữ liệu thuộc chương 4.

**2.2.3 Học chuyển giao và huấn luyện tinh chỉnh.** Giữ nguyên lý kế thừa trọng số, cập nhật tham số và thay đổi số lớp. Phương án ba lớp của đề tài chuyển sang 3.2 mới.

**2.2.4 Tham số huấn luyện và nguyên tắc chọn checkpoint.** Giữ ý nghĩa epochs, batch, imgsz, tốc độ học, dừng sớm và best/last. Cấu hình cụ thể thuộc chương 4.

### 2.3 Cơ sở xử lý ảnh và video

**2.3.1 Biểu diễn khung hình và lấy mẫu video.** Giữ hệ tọa độ, độ phân giải, FPS, bước lấy mẫu và quan hệ thời gian. Phân biệt thời gian trong video với thời gian máy xử lý.

**2.3.2 Liên kết đối tượng theo quan hệ không gian.** Giữ cơ sở vị trí tương đối, khoảng cách và giới hạn hình học; công thức vùng liên kết của đề tài đặt ở chương 3.

**2.3.3 Nguyên lý Centroid Tracking.** Giữ tâm hộp, khoảng cách, ý tưởng ghép qua các khung và hạn chế đổi mã; chưa mô tả các hệ số cài đặt.

**2.3.4 Xác nhận theo thời gian và hạn chế đếm trùng.** Giải thích nhu cầu nhiều quan sát và duy trì mã. Quy tắc bộ đếm, chốt trạng thái, lưu một lần chuyển sang chương 3.

### 2.4 Cơ sở đánh giá mô hình và hệ thống

**2.4.1 IoU và các trường hợp TP, FP, FN.** Giữ định nghĩa, công thức và quy tắc ghép một đối một.

**2.4.2 Precision, Recall, F1 và mAP.** Giữ công thức, cách hiểu và sự khác nhau giữa mAP@50 với mAP@50–95.

**2.4.3 Ma trận nhầm lẫn và các đường cong đánh giá.** Giữ cách đọc và ý nghĩa; quy ước đầu ra thư viện được nêu theo công cụ thực dùng khi báo cáo thực nghiệm.

**2.4.4 Sai số đếm và hiệu năng xử lý.** Giữ sai số tuyệt đối, MAE, FPS và thời gian toàn trình; phân biệt đánh giá mô hình với đánh giá sự kiện của hệ thống.

### 2.5 Công nghệ và công cụ sử dụng

**2.5.1 Python, Ultralytics và OpenCV.** Chức năng và đặc điểm phục vụ tính toán, phát hiện và xử lý dữ liệu ảnh/video.

**2.5.2 FastAPI và công nghệ giao diện web.** Giới thiệu API HTTP, FastAPI, React, TypeScript và Vite ở mức cần thiết.

**2.5.3 SQLAlchemy, SQLite và lưu trữ tệp.** Giới thiệu truy cập dữ liệu, lưu trữ quan hệ và sự khác biệt giữa dữ liệu mô tả với nội dung tệp.

**2.5.4 Google Colab và Google Drive.** Trình bày ngắn vai trò môi trường huấn luyện và lưu kết quả; không kể quy trình chạy notebook.

### 2.6 Kết luận chương

Tóm tắt các cơ sở sẽ được vận dụng ở chương 3, không khẳng định đã giảm báo nhầm hay đã tăng độ chính xác.

<!-- PAGE -->
## 5 Bố cục mới của chương 3

**Tên chương đề xuất: CHƯƠNG 3 PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG**

### 3.1 Phân tích yêu cầu hệ thống

**3.1.1 Đối tượng sử dụng, phạm vi và quy ước nghiệp vụ.** Giữ nhóm người dùng chung, xử lý tệp tải lên và phân cấp dự án–địa điểm–phiên–tệp. Chốt cách hiểu “đối tượng”, “trường hợp ghi nhận” và giới hạn chưa phân biệt người lái/người ngồi sau. Phần công thức thống kê dẫn tới 3.6 mới.

**3.1.2 Yêu cầu chức năng.** Giữ CN01–CN09, viết dưới dạng yêu cầu đầu vào, xử lý, đầu ra và điều kiện chấp nhận có thể kiểm tra; không mô tả lại từng bước giao diện.

**3.1.3 Yêu cầu phi chức năng.** Giữ khả năng sử dụng, nhất quán, hiệu năng, xử lý lỗi, xác thực và bảo trì. Làm rõ cách kiểm tra yêu cầu; không tự đặt chỉ tiêu tốc độ hoặc độ chính xác khi chưa có căn cứ.

**3.1.4 Mô hình Use Case và đặc tả nghiệp vụ chính.** Giữ hình tổng quát; dùng danh mục UC gắn với mã CN. Dưới mục này, dùng tên UC01, UC02… làm tiêu đề ngắn, tránh dãy số năm cấp. Đặc tả tập trung vào luồng chính, luồng lỗi và điều kiện trước/sau; các chi tiết thuật toán chỉ dẫn chiếu tới 3.4.

### 3.2 Lựa chọn phương án nhận diện cho đề tài

**3.2.1 Yêu cầu đối với mô hình và phương án ba lớp.** Từ hạn chế của hai lớp, giải thích vì sao bổ sung bike; phân biệt đầu ra phát hiện vùng đầu với kết luận ở cấp hệ thống. Phần này tiếp nhận nội dung thiết kế từ 2.1.5 cũ, không lặp bối cảnh chương 1.

**3.2.2 Phương án kế thừa và tinh chỉnh mô hình.** Mô tả luồng thiết kế: checkpoint hai lớp → dữ liệu ba lớp → tinh chỉnh → chọn mô hình trên tập xác thực → tích hợp. Nêu yêu cầu đồng bộ tên lớp, mã lớp và trọng số tương thích. Cấu hình, nguồn dữ liệu và kết quả thực hiện đưa vào chương 4.

**3.2.3 Đầu vào, đầu ra và giả định của mô-đun nhận diện.** Định nghĩa dữ liệu đưa vào, hộp giới hạn, nhãn, điểm tin cậy và cách chuyển đầu ra thành dữ liệu cho mô-đun liên kết. Nêu riêng giới hạn đối tượng nhỏ, che khuất và thiếu xe; không khẳng định riêng việc tăng số lớp đã giải quyết nhầm người đi bộ.

### 3.3 Thiết kế kiến trúc và luồng xử lý tổng thể

**3.3.1 Kiến trúc và trách nhiệm các thành phần.** Tiếp nhận 3.2.1 cũ cùng phần kiến trúc từ 2.3.3. Thể hiện frontend, API, dịch vụ xử lý, YOLO, liên kết/tracking, cơ sở dữ liệu và kho tệp. Giữ notebook huấn luyện ở luồng riêng cung cấp checkpoint.

**3.3.2 Giao tiếp và điều phối tác vụ.** Mô tả dữ liệu gửi/nhận, xác thực, tiếp nhận tệp, tác vụ nền và truy vấn tiến độ. Có thể bổ sung sơ đồ trình tự tải dữ liệu → trả mã phiên → xử lý → cập nhật trạng thái. Bảng giao tiếp chỉ cần đầu vào, đầu ra và lỗi chính; danh sách API chi tiết có thể để phụ lục.

**3.3.3 Quy trình tổng thể và quản lý trạng thái.** Tái sử dụng lưu đồ hiện có; phân biệt trạng thái phiên với trạng thái tệp, giải thích PENDING, PROCESSING, COMPLETED, FAILED và hoàn thành một phần. Mỗi bước chỉ dẫn tới mục thiết kế chi tiết, không kể lại toàn bộ thuật toán.

<!-- PAGE -->
## 5 Bố cục mới của chương 3 tiếp theo

### 3.4 Thiết kế thuật toán nhận diện và ghi nhận trường hợp

**3.4.1 Quy trình xử lý ảnh và video.** Xác định đầu vào, đầu ra, các bước dùng chung và các bước riêng. Ảnh xử lý tại một thời điểm; video thêm lấy mẫu, tracking và xác nhận. Quy tắc xử lý/lưu khung bỏ qua phải được nêu đúng với phương án đã chọn.

**3.4.2 Thiết kế liên kết vùng đầu với xe máy.** Chuyển công thức vùng mở rộng, điều kiện ứng viên và chọn xe từ 2.2.2 cũ. Nêu quan hệ một đầu–tối đa một xe, một xe–nhiều đầu và ba trạng thái HELMET, NO_HELMET, UNKNOWN. Giữ hệ số dưới dạng tham số; dẫn tới bảng giá trị thực dùng ở chương 4.

**3.4.3 Thiết kế theo dõi đối tượng.** Nêu đối tượng được theo dõi ở từng nhánh, dữ liệu của track, chi phí ghép, cách chọn cặp, tạo mã mới và mất dấu. Đưa quy tắc ưu tiên cùng trạng thái từ 2.2.3 cũ vào đây; trình bày hệ số như lựa chọn thiết kế có giá trị cấu hình tại chương 4.

**3.4.4 Xác nhận trạng thái và lưu minh chứng một lần.** Chuyển công thức bộ đếm, đặt lại chuỗi, ngưỡng K và trạng thái đã xác nhận từ 2.2.4 cũ. Giữ bảng minh họa hiện có tại đây; ghi rõ liên tiếp trên các lượt chạy AI, thời điểm minh chứng là lúc xác nhận và trạng thái xác nhận không tự bị xóa bởi quan sát sau đó.

**3.4.5 Các nhánh ngoại lệ và giới hạn của thiết kế.** Tập trung trường hợp không phát hiện xe, xe chưa có vùng đầu, một xe nhiều đầu, người đi bộ gần xe, đổi mã và che khuất. Đây là mô tả hành vi và giả định cần kiểm thử, chưa phải kết quả chứng minh hiệu quả.

### 3.5 Thiết kế cơ sở dữ liệu và lưu trữ

**3.5.1 Mô hình thực thể và quan hệ.** Giữ ERD và sáu bảng users, projects, locations, analysis_sessions, media_files, violations; làm rõ quan hệ sở hữu và liên kết kết quả về nguồn.

**3.5.2 Cấu trúc dữ liệu và ràng buộc.** Bổ sung kiểu dữ liệu, khóa, trường bắt buộc, trường không áp dụng cho ảnh tĩnh, trạng thái và quy tắc xóa/nhất quán. Làm rõ mã theo dõi thuộc phạm vi tệp video, không phải định danh xe trên toàn hệ thống.

**3.5.3 Tổ chức kho tệp và liên kết minh chứng.** Giữ các nhóm uploads, results, violations, exports ở mức cấu trúc logic; nêu quy tắc đặt tên và đường dẫn tương đối. Đường dẫn cài đặt, mã tạo thư mục và ví dụ gói ZIP thực tế thuộc chương 4.

### 3.6 Thiết kế thống kê và xuất kết quả

**3.6.1 Đơn vị đếm và các chỉ số tổng hợp.** Nêu nguồn số liệu, phạm vi tổng hợp, cách tính tỷ lệ, xử lý UNKNOWN và mẫu số bằng 0. Phân biệt đếm theo ảnh, theo mã trong video và phép cộng giữa nhiều tệp.

**3.6.2 Tổng hợp theo địa điểm và thời gian.** Gom quy tắc ở UC07 và 3.2.2.6 cũ: phiên/tệp thành công, giờ khai báo, thời điểm xác nhận, ảnh tĩnh và giới hạn nhiều video dùng chung mốc bắt đầu. Giá trị khoảng thời gian có thể cấu hình được dẫn sang chương 4.

**3.6.3 Xuất dữ liệu và kiểm tra nguồn kết quả.** Thiết kế phạm vi phiên/địa điểm/dự án, nội dung JSON/CSV, tệp và minh chứng trong ZIP; quy định cách phản ánh tệp thiếu hoặc phiên chưa hoàn thành.

### 3.7 Thiết kế giao diện và tương tác

**3.7.1 Cấu trúc màn hình và điều hướng.** Tài khoản, dự án, địa điểm, tải dữ liệu, chi tiết phiên và thống kê.

**3.7.2 Giao diện nhập dữ liệu và theo dõi tiến độ.** Giữ bản phác thảo, trường nhập, trạng thái rỗng, lỗi, chờ và hoàn thành một phần; dẫn chiếu Use Case thay vì viết lại toàn bộ luồng.

**3.7.3 Giao diện kết quả, minh chứng và thống kê.** Nêu bố trí thông tin và cách người dùng đối chiếu. Điều chỉnh tên chỉ số theo đơn vị đã chốt ở 3.6. Ảnh chụp ứng dụng đã xây dựng chuyển sang chương 4.

### 3.8 Kết luận chương

Tóm tắt các quyết định thiết kế và mối liên hệ với cơ sở chương 2, dẫn sang thực hiện và kiểm thử chương 4.

<!-- PAGE -->
## 6 Nội dung dành cho chương 4

**Tên chương đề xuất: CHƯƠNG 4 TRIỂN KHAI VÀ KIỂM THỬ HỆ THỐNG**

### 4.1 Môi trường thực hiện và chuẩn bị dữ liệu

Giữ phần cứng, phiên bản công cụ, nguồn checkpoint, nguồn dữ liệu, mã lớp, quy mô các tập và thao tác kiểm tra nhãn. Định dạng nhãn chỉ dẫn lại chương 2, kèm ví dụ thực tế nếu cần. Đối chiếu số liệu với nhật ký và tệp cấu hình của lần chạy.

### 4.2 Thực hiện huấn luyện tinh chỉnh và lựa chọn mô hình

Giữ bảng cấu hình epochs, imgsz, batch, optimizer, lr0, seed, resume, freeze; quy trình chạy notebook; lịch sử huấn luyện; checkpoint được chọn và kiểm tra đầu ra. Dẫn lại phương án ở 3.2 mới để tránh giải thích lại động cơ bổ sung bike. Các số liệu 100 epoch, khoảng 174 phút, epoch 88 và mAP hiện có chỉ là thông tin bản thảo đang ghi, cần đi kèm minh chứng tương ứng khi hoàn thiện.

### 4.3 Xây dựng và tích hợp hệ thống

**4.3.1 Tích hợp mô hình và cấu hình xử lý ảnh/video.** Bổ sung bảng tham số thực dùng: ngưỡng tin cậy, tham số liên kết, bước lấy mẫu, khoảng cách ghép, ngưỡng mất dấu và số lượt xác nhận. Chuyển các hệ số cụ thể ở 2.2 cũ vào đây; dẫn thuật toán về 3.4 mới.

**4.3.2 Xây dựng API, cơ sở dữ liệu và lưu trữ.** Nêu mô-đun đã xây dựng, cách cấu hình và minh chứng hoạt động, tránh sao chép ERD hoặc toàn bộ đặc tả chương 3.

**4.3.3 Xây dựng giao diện và các chức năng nghiệp vụ.** Dùng ảnh chụp ứng dụng chạy thực tế; nêu chức năng đã hoàn thành và cách chúng đáp ứng thiết kế.

**4.3.4 Tích hợp thống kê và xuất kết quả.** Đưa ví dụ dữ liệu, gói ZIP và đối chiếu số liệu; dẫn công thức/quy tắc về 3.6 mới.

### 4.4 Kiểm thử và đánh giá

**4.4.1 Dữ liệu, điều kiện và phương pháp kiểm thử.** Nêu dữ liệu đối chứng, đơn vị đếm, ngưỡng, phần cứng và cách đo. Đặt kịch bản người đi bộ, người gần xe, thiếu xe, nhiều đầu, che khuất và đổi mã tại đây.

**4.4.2 Kết quả đánh giá mô hình.** Dùng chỉ số đã định nghĩa ở chương 2. So sánh hai mô hình trên hai lớp chung với cùng dữ liệu và ánh xạ đúng lớp; báo cáo bike riêng, không dùng trung bình hai lớp so trực tiếp trung bình ba lớp để kết luận cải tiến.

**4.4.3 Kết quả ghi nhận và sai số đếm.** Báo cáo đúng, nhầm, bỏ sót, đếm trùng và ảnh hưởng nhánh không phát hiện xe. Phân biệt kết quả mô hình với kết quả sau liên kết/tracking.

**4.4.4 Kiểm thử chức năng và thời gian xử lý.** Liên kết ca kiểm thử với CN/UC ở chương 3; ghi kết quả mong đợi, thực tế và đạt/chưa đạt. Phân biệt tốc độ suy luận với thời gian xử lý toàn trình.

**4.4.5 Nhận xét và hạn chế.** Kết luận theo kết quả đo, xác định trường hợp hoạt động tốt và trường hợp còn sai.

### 4.5 Kết luận chương

Tổng hợp mức độ hoàn thành và kết quả kiểm thử. Trong bản hiện tại, 4.3 và 4.4 mới chủ yếu là đề mục; không nên dùng lời khẳng định ở chương 2 hoặc chương 3 để thay cho phần kết quả còn thiếu.

<!-- PAGE -->
## 7 Bảng chuyển nội dung từ bố cục cũ sang bố cục mới

Số ở cột đầu là mục hiện tại của bản báo cáo; các cột còn lại dùng số mục mới trong đề cương này. Khi một mục được tách sang nhiều chương, cần biên tập lại câu văn theo chức năng của từng chương.

| Nội dung hiện tại | Giữ tại chương 2 mới | Đưa sang chương 3 mới | Đưa sang chương 4 mới |
| --- | --- | --- | --- |
| 2.1.1–2.1.2 Phát hiện và YOLO | 2.1 Khái niệm, nguyên lý, đầu ra, lọc dự đoán | 3.2.3 Đầu ra sử dụng trong hệ thống | 4.3.1 Cách nạp và tích hợp |
| 2.1.3 Nhãn và chia dữ liệu | 2.2.1–2.2.2 Nguyên tắc | 3.2.2 Yêu cầu đồng bộ lớp | 4.1 Nguồn, quy mô, kiểm tra thực tế |
| 2.1.4–2.1.5 Fine-tuning và ba lớp | 2.2.3 Cơ sở học chuyển giao | 3.2.1–3.2.2 Phương án của đề tài | 4.2 Cấu hình và thực hiện |
| 2.1.6 Tham số và checkpoint | 2.2.4 Ý nghĩa và nguyên tắc | 3.2.2 Luồng lựa chọn mô hình | 4.2 Giá trị, nhật ký, checkpoint |
| 2.2.1 Ảnh và video | 2.3.1 Khung hình và lấy mẫu | 3.4.1 Hai nhánh xử lý | 4.3.1 API thư viện và vòng xử lý |
| 2.2.2 Liên kết đầu và xe | 2.3.2 Quan hệ không gian | 3.4.2 Vùng ghép, khoảng cách, trạng thái | 4.3.1 Hệ số thực dùng |
| 2.2.3 Tracking | 2.3.3 Nguyên lý theo tâm | 3.4.3 Ghép và vòng đời mã | 4.3.1 Ngưỡng thực dùng |
| 2.2.4 Xác nhận và đếm | 2.3.4 Cơ sở xác nhận theo thời gian | 3.4.4 Bộ đếm, chốt trạng thái; 3.6.1 đơn vị | 4.3.1 Cấu hình; 4.4.3 kết quả |
| 2.3 Công nghệ | 2.5 Đặc điểm và chức năng công cụ | 3.3 Cách kết hợp thành kiến trúc | 4.1 Môi trường; 4.3 tích hợp |
| 2.4 Chỉ số đánh giá | 2.4 Định nghĩa, công thức, cách hiểu | 3.1 Tiêu chí yêu cầu; 3.6 quy tắc đếm | 4.4 Quy trình đánh giá và kết quả |
| 3.1 Yêu cầu và Use Case | Không chuyển | 3.1 Rút lặp và liên kết CN–UC | 4.4.4 Đối chiếu ca kiểm thử |
| 3.2.1 Kiến trúc | Không chuyển | 3.3.1 Trách nhiệm thành phần | 4.3 Minh chứng đã tích hợp |
| 3.2.2 Quy trình | Không chuyển | 3.3.3 Luồng chung; 3.4 thuật toán; 3.6 thống kê | 4.3 Chi tiết cài đặt cần thiết |
| 3.3 Dữ liệu và lưu trữ | Không chuyển | 3.5 Mô hình và ràng buộc | 4.3.2 Cài đặt và ví dụ thực tế |
| 3.4 Giao diện | Không chuyển | 3.7 Bản phác thảo và tương tác | 4.3.3 Ảnh ứng dụng chạy thực tế |

### Cách xử lý hình và công thức

Giữ hình nguyên lý YOLO trong chương 2. Giữ Use Case, kiến trúc, lưu đồ, ERD và bản phác thảo giao diện trong chương 3, đồng thời cập nhật nhãn và số thứ tự. Chuyển công thức (2.5), (2.6), (2.8), (2.9) cùng Bảng 2.2 sang mục 3.4 thích hợp rồi đánh số lại. Công thức khoảng cách Euclid giữ ở phần nguyên lý tracking; phần thiết kế dẫn chiếu khi dùng để xây dựng chi phí ghép. Công thức chỉ số đánh giá tiếp tục nằm trong chương 2.

<!-- PAGE -->
## 8 Các lỗi biên tập cần sửa và mẫu nối mạch nội dung

### 8.1 Lỗi đánh số và trình bày đang có

- **2.1.3:** tiểu mục đầu dùng “a)” nhưng phần sau dùng 2.1.3.2 và 2.1.3.3. Chọn thống nhất một cách chia.
- **2.2.4:** tiêu đề 2.2.4.1 và 2.2.4.2 cùng là “Xác nhận bằng chuỗi phát hiện liên tiếp”; mục sau thực chất là ví dụ. Số 2.2.4.3 được dùng hai lần.
- **2.4.2:** Recall và F1-score cùng được đánh số 2.4.2.2.
- **3.1.1:** “Đối tượng sử dụng” và “Phạm vi hoạt động” cùng mang số 3.1.1.1.
- **3.1.4:** số 3.1.4.2 dùng cho cả biểu đồ tổng quát và đặc tả; các đặc tả kéo xuống năm cấp. Dùng mã UC để rút cấp mục.
- **Hình và bảng chương 3:** còn “Hình 3..”, “Hình 3.”, “Bảng 3.”; Bảng 3.6–3.11 thiếu tên sau số bảng. Cần ghi tên đầy đủ và cập nhật danh mục.
- **Kiểu tiêu đề Word:** 3.1.4 và nhiều tiểu mục đang dùng Normal; cần gán Heading đúng cấp để mục lục và điều hướng phản ánh đủ cấu trúc.
- **Lỗi chữ:** bỏ ký tự “ư” cuối dòng Detection Head ở 2.1.2, dấu chấm đôi ở 2.3.1, đoạn chỉ có dấu chấm sau kết luận chương 2; sửa “dư liệu” thành “dữ liệu”.
- **Chương 4:** tiêu đề 4.3 bị lặp; còn ghi chú chèn hình và đề mục chưa triển khai. Khi hoàn thiện cần thay bằng nội dung và minh chứng thực tế.

### 8.2 Mẫu cách viết để phân biệt ba chương

**Đoạn cơ sở phù hợp chương 2:**

“Theo dõi đối tượng bằng tâm hộp giới hạn sử dụng vị trí của đối tượng ở các khung hình để thiết lập quan hệ giữa các lần phát hiện. Khoảng cách giữa các tâm là một căn cứ ghép đối tượng. Phương pháp có cách tính đơn giản nhưng có thể đổi mã khi đối tượng giao cắt hoặc bị che khuất. Vì vậy, kết quả theo dõi cần được xem xét cùng sai số đếm trong ứng dụng.”

**Đoạn thiết kế phù hợp chương 3:**

“Vận dụng cơ sở theo dõi theo tâm ở mục 2.3.3, hệ thống duy trì mã và trạng thái cho từng đối tượng qua các lượt phân tích video. Nhánh liên kết theo xe sử dụng tâm hộp xe; nhánh xử lý vùng đầu độc lập sử dụng tâm hộp vùng đầu. Bộ đếm xác nhận được cập nhật trên các khung chạy nhận diện. Khi một mã lần đầu đạt điều kiện xác nhận, hệ thống tạo bản ghi và lưu minh chứng; các lần cập nhật tiếp theo của cùng mã không tạo bản ghi mới.”

**Nội dung tương ứng ở chương 4:**

Trình bày mô-đun cài đặt thuật toán trên, bảng giá trị tham số thực dùng, cấu hình máy và dữ liệu kiểm thử; đưa kết quả báo nhầm, bỏ sót, đổi mã hoặc đếm trùng kèm minh chứng. Không lặp lại định nghĩa Centroid Tracking hoặc tự suy diễn hiệu quả từ tên thuật toán.

### 8.3 Đoạn dẫn mở chương có thể sử dụng

**Mở chương 2:** “Chương này trình bày các cơ sở về phát hiện đối tượng, huấn luyện tinh chỉnh, xử lý ảnh và video, liên kết không gian và theo dõi đối tượng. Các chỉ số đánh giá và công nghệ liên quan được giới thiệu nhằm làm nền tảng cho những lựa chọn thiết kế ở chương tiếp theo.”

**Mở chương 3:** “Trên cơ sở lý thuyết và công nghệ đã trình bày ở Chương 2, chương này phân tích yêu cầu và đề xuất thiết kế hệ thống. Nội dung tập trung vào phương án nhận diện ba lớp, kiến trúc xử lý, thuật toán liên kết và ghi nhận trường hợp, tổ chức dữ liệu, thống kê và giao diện. Cấu hình thực hiện cùng kết quả kiểm thử được trình bày ở Chương 4.”

Sau khi áp dụng bố cục mới, cần cập nhật kết luận từng chương, phần bố cục báo cáo ở mở đầu, mục lục, danh mục hình/bảng và mọi dẫn chiếu số mục. Nội dung về giảm nhầm người đi bộ và giảm đếm trùng phải được diễn đạt là mục tiêu thiết kế ở chương 3, rồi kết luận mức độ đạt được bằng thực nghiệm ở chương 4.
