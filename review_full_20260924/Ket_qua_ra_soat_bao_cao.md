# Kết quả rà soát báo cáo đồ án của Lê Đức Thuận

Tài liệu: `E:\Downloads\CNTT_2022606983_LeDucThuan_BaoCao.docx`.

Đã đọc toàn bộ phần mở đầu, bốn chương, kết luận và tài liệu tham khảo; kiểm tra bảng, công thức, sơ đồ và bố cục bản xuất từ Microsoft Word gồm 79 trang. Đối chiếu chọn lọc phần mô tả triển khai với mã nguồn và tệp trọng số đang có trong thư mục dự án. Không chỉnh sửa báo cáo gốc và không chạy lại huấn luyện hay thực nghiệm.

**Quy ước vị trí:** “trang” dưới đây là số trang in trong báo cáo. Phần nội dung từ Mở đầu trở đi có số trang vật lý cao hơn 10; ví dụ trang 58 tương ứng trang thứ 68 của tệp. Danh mục bảng nằm ở trang vii, tức trang thứ 10.

**Nhận định:** Báo cáo có cấu trúc tương đối đầy đủ và đã công khai nhiều giới hạn của hệ thống. Tuy nhiên, cần xử lý mâu thuẫn về nguồn gốc mô hình, hoàn thiện bằng chứng đánh giá cấp hệ thống và sửa các lỗi dẫn chiếu trước khi chốt bản nộp. Một số sai khác với mã nguồn/trọng số hiện tại cần xác nhận phiên bản thực nghiệm, không được tự động coi là số liệu trong báo cáo sai.

## 1. Những vấn đề cần ưu tiên

### 1.1. Mô tả quá trình phát triển mô hình chưa nhất quán

**Vị trí:** mục 2.1 trang 13; mục 4.2 trang 57; mục 4.2.2 trang 58; mục 4.2.5 trang 60; nhận xét trang 66 và kết luận trang 68.

- Trang 58: “Đề tài sử dụng trọng số YOLOv8n đã được huấn luyện cho hai lớp có mũ và không mũ làm điểm khởi tạo.”
- Trang 60: “So sánh mô hình YOLOv8n hai lớp và YOLO11n ba lớp...”
- Trang 68 tiếp tục khẳng định đã tinh chỉnh từ trọng số hai lớp sang bộ dữ liệu ba lớp.

Hai mô tả chưa giải thích được mô hình cuối là YOLOv8n hay YOLO11n và đã kế thừa trọng số nào. Thay đổi số lớp và thay đổi họ kiến trúc là hai việc cần trình bày riêng. Chỉ ghi `resume: false` không chứng minh đã kế thừa checkpoint hai lớp.

**Đối chiếu bổ sung:** metadata của `backend/models/best.pt` hiện tại ghi `yolov8n.pt`; `backend/models/best_3class.pt` ghi `yolo11n.pt`, cấu trúc YOLO11 và tên lượt chạy `train_lan_1_datasetdefault_doc_lap`. Điều này củng cố nhu cầu kiểm tra lại nguồn checkpoint, nhưng chưa chứng minh các tệp hiện tại chính là tệp dùng tạo mọi bảng trong báo cáo.

**Cách sửa:** xác định lượt chạy cuối cùng bằng notebook/lệnh huấn luyện, cấu hình, log và checkpoint. Nếu huấn luyện YOLO11n từ trọng số YOLO11 có sẵn, phải mô tả đúng việc đó; không giữ câu “tinh chỉnh trực tiếp từ YOLOv8n hai lớp” khi không có bằng chứng chuyển trọng số. Nếu thực sự có bước chuyển trọng số giữa kiến trúc, cần nêu rõ cách chuyển và các tầng được kế thừa. Cập nhật đồng bộ mục tiêu, lý thuyết áp dụng, Chương 4, kết luận và nguồn tài liệu cho YOLO11.

### 1.2. Thông số huấn luyện và Bảng 4.5 chưa khớp checkpoint hiện có

**Vị trí:** Bảng 4.4 trang 58 và Bảng 4.5 trang 59. **Loại:** cần xác minh phiên bản/lượt chạy.

Bảng 4.4 ghi tốc độ học ban đầu khai báo là `0,001`, trong khi metadata của `best_3class.pt` hiện tại ghi `lr0 = 0.01`. Báo cáo nói Bảng 4.5 lấy kết quả tại vòng 88; lịch sử huấn luyện lưu trong checkpoint hiện tại có các giá trị sau:

| Chỉ số tại vòng 88 | Bảng 4.5 | Lịch sử trong checkpoint hiện có |
|---|---:|---:|
| Precision | 88,322% | 90,095% |
| Recall | 85,794% | 87,116% |
| mAP@50 | 92,499% | 93,317% |
| mAP@50–95 | 66,512% | 69,668% |

**Cách sửa:** đối chiếu `args.yaml`, `results.csv`, log và checkpoint cùng một lượt chạy. Ghi rõ tên mô hình, tên lượt chạy và nguồn từng bảng. Không thay các số trong báo cáo bằng cột phải nếu chưa xác định đúng tệp. Với `optimizer=auto`, cũng cần phân biệt tham số tốc độ học khai báo với tốc độ học thực tế được bộ tối ưu sử dụng.

### 1.3. Kết quả thực nghiệm chưa chứng minh đủ các mục tiêu chính

**Vị trí:** mục tiêu và phạm vi đánh giá trang 2–3; mục 2.4.3 trang 24; mục 4.2.5 trang 60; mục 4.4 trang 63–65.

Phần mở đầu đặt mục tiêu giảm báo nhầm người đi bộ, đánh giá bỏ sót, sai số đếm và tốc độ xử lý. Chương 2 đã định nghĩa MAE và FPS. Tuy nhiên, phần kết quả chưa trình bày:

- Số/tỷ lệ người đi bộ bị ghi nhầm sau bước liên kết vùng đầu với xe.
- Bảng đối chiếu số đếm thủ công và số đếm hệ thống trên từng video thực tế; MAE hoặc sai số tương ứng.
- Số trường hợp đếm trùng hoặc mất đối tượng trên video thực tế.
- Thời gian/FPS của toàn bộ quy trình, gồm đọc video, nhận diện, liên kết, theo dõi và lưu kết quả.

Bảng 4.8 là đánh giá mô hình trên ảnh; Bảng 4.12 kiểm tra logic tracker bằng đối tượng giả lập. Hai loại kết quả này có giá trị nhưng chưa thay thế phép đánh giá toàn hệ thống. Báo cáo đã thừa nhận giới hạn ở trang 63, 64 và 67; đó là điểm đúng cần giữ.

**Cách sửa:** bổ sung một tập ảnh có người đi bộ và một nhóm video được kiểm đếm thủ công, ghi rõ tiêu chí đúng/sai và báo cáo kết quả trước/sau liên kết, theo dõi. Nếu chưa thực hiện được, nêu rõ những mục tiêu nào mới được triển khai hoặc kiểm thử logic, chưa được xác nhận hiệu quả bằng dữ liệu thực tế.

### 1.4. Chưa thể quy toàn bộ mức cải thiện cho việc thêm lớp bike

**Vị trí:** Bảng 4.8–4.9 trang 60; nhận xét trang 61, 66–68.

So sánh YOLOv8n hai lớp với YOLO11n ba lớp đồng thời thay đổi ít nhất kiến trúc và số lớp; quá trình huấn luyện/dữ liệu có thể cũng khác. Kết quả cho phép kết luận hai cấu hình có chất lượng khác nhau trên tập đối chứng, nhưng chưa tách riêng tác dụng của lớp bike hay bước liên kết.

**Cách sửa:** giữ kết luận trong phạm vi “cấu hình ba lớp được đánh giá tốt hơn cấu hình hai lớp trên tập đối chứng”. Muốn khẳng định riêng tác dụng của lớp bike hoặc thuật toán liên kết, cần thí nghiệm đối chứng giữ các yếu tố khác tương đương và bật/tắt thành phần cần đánh giá. Đây là giới hạn thiết kế thực nghiệm, không phủ nhận các số đo đã có.

### 1.5. Đối tượng trong tên đề tài chưa trùng hoàn toàn đơn vị đầu ra

**Vị trí:** tên đề tài; phạm vi trang 3, 8; thiết kế trang 44–46, 50.

Tên đề tài nhấn mạnh **người điều khiển xe máy**, nhưng báo cáo thừa nhận chưa phân biệt chắc chắn người lái với người ngồi sau. Quy tắc lại gán cả xe là NO_HELMET khi có ít nhất một vùng đầu không mũ. Vì vậy, xe có người lái đội mũ nhưng người ngồi sau không mũ vẫn được tính.

**Cách sửa:** thống nhất rằng chỉ số đầu ra là “số xe có ít nhất một người không đội mũ” trong phạm vi dữ liệu, không diễn giải thành số người lái không đội mũ. Nếu tên đề tài đã được duyệt, cần giữ tên theo yêu cầu của trường và nêu rõ giới hạn mức độ đáp ứng; nếu được phép điều chỉnh, cân nhắc cụm “người đi xe máy”. Không tự đổi tên đề tài đã duyệt.

### 1.6. Quy tắc bỏ vùng đầu không có xe khác với mã nguồn hiện tại

**Vị trí:** mục 3.3.1.4 trang 46 và mục 3.3.4.3 trang 50. **Loại:** sai khác chắc chắn với workspace hiện tại; cần xác nhận bản triển khai được báo cáo.

Báo cáo khẳng định vùng đầu không liên kết được với xe không được tính độc lập. Nhưng `build_subjects()` trong `backend/app/services/ai/violation.py` có nhánh `if not vehicles:` tạo một đối tượng cho từng vùng đầu có/không mũ. Nhánh này xét việc không phát hiện được xe trong khung hình, không giới hạn ở mô hình hai lớp.

**Ý nghĩa:** ảnh chỉ có người đi bộ hoặc khung hình bỏ sót toàn bộ xe vẫn có thể phát sinh số đếm. Điều này ảnh hưởng trực tiếp lập luận về đơn vị đếm và giảm báo nhầm người đi bộ.

**Cách sửa:** chốt phiên bản mã nguồn dùng đánh giá. Nếu cơ chế dự phòng này là chủ ý, phải mô tả và đo ảnh hưởng của nó. Nếu thiết kế yêu cầu chỉ ghi nhận đầu gắn với xe, cần đồng bộ triển khai rồi kiểm thử lại trước khi giữ kết luận. Chỉnh lời văn đơn thuần không giải quyết được sai khác thực nghiệm.

### 1.7. Quy tắc tổng hợp HELMET và UNKNOWN trên video chưa đầy đủ

**Vị trí:** mục 3.3.4.3 trang 50.

Câu “Những mã chưa đủ thông tin hoặc chưa đạt điều kiện xác nhận được giữ ở nhóm chưa xác định...” chưa giải thích trường hợp track đã từng thấy có mũ. Trong code hiện tại, tracker tổng hợp:

- NO_HELMET nếu đã từng đủ điều kiện xác nhận không mũ.
- HELMET nếu đã từng thấy có mũ và chưa từng xác nhận không mũ.
- UNKNOWN trong các trường hợp còn lại.

Ví dụ, với K=3, track từng thấy có mũ rồi có hai lần không mũ vẫn được code tổng hợp vào HELMET. Bảng 3.4 chỉ mô tả trạng thái tại một lần quan sát, chưa thay cho quy tắc tổng hợp toàn video.

**Cách sửa:** bổ sung đủ ba quy tắc theo lịch sử track, đối chiếu đúng phiên bản triển khai và nêu quan hệ `UNKNOWN = tổng track − HELMET − NO_HELMET`.

## 2. Thiếu thông tin để kiểm chứng và tái lập

### 2.1. Nguồn dữ liệu và cách chia tập còn thiếu

**Vị trí:** mục 4.2.1 trang 57–58 và mục 4.2.5 trang 60.

Báo cáo nêu 6.988 ảnh và 31.033 đối tượng, nhưng chưa chỉ rõ tên/nguồn/bản phát hành bộ dữ liệu, nguồn dữ liệu của mô hình hai lớp, phần nào được tự gán bổ sung và quy ước lớp bike. Chưa có danh sách hoặc mô tả đủ cụ thể cách loại 332 ảnh có “mã nguồn trùng”. Cụm “mã nguồn” dễ bị hiểu thành source code; nên giải thích đó là mã ảnh gốc hoặc định danh ảnh.

**Cách sửa:** thêm nguồn dữ liệu, phiên bản, ánh xạ mã lớp, quy tắc gán nhãn, phương pháp chia và loại trùng. Với khung hình từ video, cần giải thích cách tránh đưa các khung gần nhau hoặc biến thể của cùng ảnh vào cả train và test. Chưa đủ căn cứ để kết luận có rò rỉ dữ liệu; thiếu sót hiện tại là chưa chứng minh rõ tính độc lập của các tập.

### 2.2. Cấu hình đo hiệu năng chưa đủ cụ thể

**Vị trí:** mục 4.1 trang 56–57; Bảng 4.8 trang 60.

Hai kết quả 86,74 và 93,23 ms/ảnh chưa kèm mẫu CPU, RAM, phiên bản thư viện, số luồng, số lần chạy, khởi động làm nóng mô hình và phạm vi đo. “Máy tính cá nhân, chạy CPU” chưa đủ để tái lập hoặc so sánh tốc độ.

**Cách sửa:** ghi cấu hình máy và môi trường; xác định thời gian chỉ suy luận hay gồm tiền/hậu xử lý, số ảnh, cách lấy trung bình và số lần lặp. Không suy ra FPS toàn hệ thống từ thời gian suy luận ảnh đơn.

### 2.3. Nhắc ma trận nhầm lẫn và đường cong nhưng chưa đưa hình chứng minh

**Vị trí:** mục 4.2.4 trang 60 và mục 4.5.2 trang 66.

Văn bản phân tích ma trận nhầm lẫn với các số 691, 31, 74 và nhắc đường cong Precision–Recall, nhưng không có hình ma trận/đường cong tương ứng trong báo cáo. Ngưỡng cụ thể dùng lập ma trận cũng chưa được nêu; chỉ nói điều kiện có thể khác bảng tổng hợp.

**Cách sửa:** thêm hai hình từ đúng lượt đánh giá, chú thích lớp, trục, tập dữ liệu và ngưỡng; liên hệ rõ với bảng chỉ số. Nếu đặt ở phụ lục, phải dẫn đến phụ lục đó. Không coi việc 691/796 khác Recall 82,161% là lỗi số học khi các ngưỡng đánh giá có thể khác nhau.

Ở mục 4.2.5, cần nói rõ IoU 0,50 là ngưỡng ghép dự đoán với nhãn thật hay ngưỡng NMS; phân biệt confidence dùng cho Precision/Recall/F1 với quy trình tính đường cong AP. Đây là thông tin còn thiếu để kiểm chứng, chưa có căn cứ kết luận AP đã được tính sai.

### 2.4. Hình 4.8 chưa được giải thích đủ để minh họa cải thiện

**Vị trí:** trang 66.

Ảnh trước/sau hiển thị tổng đối tượng và số có mũ giảm từ **6 xuống 5**, số không mũ đều bằng **0**. Chưa có nhãn đối chứng để biết giảm một đối tượng là loại được báo nhầm, gộp đúng đối tượng hay bỏ sót.

**Cách sửa:** chú thích số đối tượng đúng theo kiểm tra thủ công, chỉ rõ đối tượng nào thay đổi và lý do. Nếu muốn minh họa giảm ghi nhầm người đi bộ, dùng tình huống có người đi bộ được đánh dấu rõ. Hình hiện tại không đủ để tự kết luận thuật toán tốt hơn hoặc kém hơn.

### 2.5. Kết luận “các chỉ số đều ổn định” chưa có bằng chứng phù hợp

**Vị trí:** trang 68, câu “Kết quả đánh giá trên tập kiểm thử các chỉ số đều ổn định”.

Câu thiếu cấu trúc rõ và dấu chấm. “Ổn định” thường cần kết quả qua nhiều lần chạy, nhiều tập hoặc điều kiện khác nhau; báo cáo hiện trình bày một tập kết quả tổng hợp.

**Cách sửa:** thay bằng nhận xét gắn với số liệu đã xác minh, chẳng hạn: “Trên tập kiểm thử đã sử dụng, mô hình đạt ...; lớp no-helmet vẫn có Recall thấp hơn các lớp còn lại.” Chỉ chèn số sau khi giải quyết mục 1.1–1.2.

Cùng trang, câu quy lỗi bỏ sót/nhầm lẫn “do các yếu tố dữ liệu” mạnh hơn nhận xét ở mục 4.5.2 vốn chỉ nói những yếu tố này “có thể góp phần”. Khi chưa phân tích từng nhóm lỗi, nên giữ mức diễn đạt có điều kiện thay vì khẳng định nguyên nhân.

## 3. Lỗi dẫn chiếu và tài liệu tham khảo

### 3.1. Bốn chỗ dẫn sai số bảng

| Trang | Vị trí | Đang ghi | Cần sửa |
|---:|---|---|---|
| 51 | Đoạn trước bảng các bảng dữ liệu | “bảng 3.4” | **Bảng 3.5** |
| 52 | Đoạn giới thiệu cấu trúc kho lưu trữ | “bảng 3.5” | **Bảng 3.6** |
| 64 | Mục 4.4.2, đoạn trước kết quả kiểm thử chức năng | “bảng 4.9” | **Bảng 4.11** |
| 65 | Mục 4.4.4, đoạn trước kết quả kiểm thử tracker | “bảng 4.10” | **Bảng 4.12** |

Nên dùng chức năng tham chiếu chéo của Word để giảm lệch số khi thêm/xóa bảng.

### 3.2. Danh mục bảng thiếu Bảng 4.12

**Vị trí:** danh mục bảng trang vii; Bảng 4.12 trang 65.

Danh mục hiện dừng ở Bảng 4.11. Chú thích Bảng 4.12 đang dùng style **Normal**, trong khi danh mục lấy các đoạn mang style **Bảng**.

**Cách sửa:** áp dụng đúng style/caption cho Bảng 4.12, sau đó cập nhật toàn bộ danh mục. Chỉ bấm cập nhật khi caption vẫn là Normal có thể chưa đưa được bảng này vào danh mục.

### 3.3. Công trình Aboah chưa có nguồn tham chiếu

**Vị trí:** mục 1.3.2 trang 9; danh mục tài liệu trang 69.

Báo cáo nhắc Aboah và cộng sự, YOLOv8 và lựa chọn mẫu khi dữ liệu gán nhãn hạn chế, nhưng không có số dẫn và không có mục tương ứng trong 13 tài liệu cuối báo cáo. Mô tả nghiên cứu phù hợp bài báo đã kiểm tra; lỗi là thiếu nguồn.

**Bổ sung đề nghị:** A. Aboah, B. Wang, U. Bagci và Y. Adu-Gyamfi, “Real-Time Multi-Class Helmet Violation Detection Using Few-Shot Data Sampling Technique and YOLOv8,” CVPR Workshops, 2023, tr. 5350–5358. [Bản công bố trên CVF](https://openaccess.thecvf.com/content/CVPR2023W/AICity/html/Aboah_Real-Time_Multi-Class_Helmet_Violation_Detection_Using_Few-Shot_Data_Sampling_Technique_CVPRW_2023_paper.html).

### 3.4. Vite đang gắn với tài liệu React

**Vị trí:** mục 2.3.2 trang 20: “React, TypeScript và Vite[11]”. Tài liệu [11] là React Quick Start.

**Cách sửa:** đặt [11] sau React hoặc sau câu nói riêng về React. Bổ sung nguồn của Vite nếu dẫn cho Vite; thêm khoảng trắng trước các tham chiếu như `FastAPI [10]`, `React [11]`, `SQLAlchemy [12]`. Nguồn tương ứng: [React Quick Start](https://react.dev/learn), [Vite Getting Started](https://vite.dev/guide/).

### 3.5. Một số mục tài liệu tham khảo chưa đủ thông tin

**Vị trí:** trang 69.

- [2] thiếu năm, tập và mã bài/DOI. Có thể hoàn thiện thành: F. W. Siebert và H. Lin, “Detecting motorcycle helmet use with deep learning,” *Accident Analysis & Prevention*, tập 134, bài 105319, 2020, DOI 10.1016/j.aap.2019.105319. [Thông tin do tác giả công bố](https://arxiv.org/abs/1910.13232).
- [3] dừng sau tên bài với dấu phẩy, thiếu năm và nơi công bố. Có thể dùng bản đã xác minh: L. Choi và R. Greer, “Evaluating Vision-Language Models for Zero-Shot Detection, Classification, and Association of Motorcycles, Passengers, and Helmets,” arXiv:2408.02244, 2024. [Bản tác giả](https://arxiv.org/abs/2408.02244).
- Các nguồn tài liệu trực tuyến như [6]–[8], [10]–[13] chưa có đường dẫn và ngày truy cập. Bổ sung theo quy cách trích dẫn trường yêu cầu, thống nhất dấu câu.
- Nguồn [5] mô tả YOLOv8; nếu mô hình cuối là YOLO11 thì cần bổ sung tài liệu đúng mô hình đó.

## 4. Thiết kế và diễn đạt cần chỉnh

| Trang | Nội dung | Nhận xét và cách sửa |
|---:|---|---|
| 39 | Hình 3.2: “Mô hình YOLO — Nhận diện & theo dõi” | Bảng 3.3 và mục 3.3.2 phân biệt YOLO với Centroid Tracking. Đổi mô tả dưới YOLO thành “Nhận diện đối tượng”; đặt phần theo dõi trong mô-đun xử lý phù hợp. |
| 31 | Use case Quản lý dự án: tiền điều kiện “thao tác với dự án hiện có” | Luồng cơ bản có tạo dự án mới. Sửa: “Người dùng đã đăng nhập. Với thao tác xem, sửa, xóa, dự án phải tồn tại và người dùng có quyền truy cập.” |
| 27, 32–33 | CN04 chỉ nêu tạo/xem địa điểm, đặc tả có cả sửa/xóa | Bổ sung sửa/xóa vào bảng yêu cầu để khớp phạm vi chức năng. |
| 6–7, 26 | Đối tượng sử dụng lúc là cán bộ Phòng CSGT, lúc là người khảo sát nói chung | Hai nhóm không loại trừ nhau, nhưng cần nói rõ nhóm chính và nhóm ví dụ; tránh thay đổi phạm vi mà không giải thích. |
| 15 | `class_id, x_center y_center, width height` | Nếu dùng làm mẫu định dạng nhãn, sửa thành `class_id x_center y_center width height`, nói rõ năm trường phân tách bằng khoảng trắng. [Định dạng chính thức](https://docs.ultralytics.com/datasets/detect/). |
| 16 | `xᵢ: : ảnh huấn luyện thứ i;` | Xóa một dấu hai chấm. |
| 60 | “dưới dây” | Sửa thành “dưới đây”. |
| 56 | “Được thể hiện qua bảng 4.2:” | Nên viết thành câu đầy đủ: “Môi trường triển khai và kiểm thử ứng dụng được trình bày trong Bảng 4.2.” |
| 36–37 | Ô yêu cầu đặc biệt của use case thống kê bắt đầu “Cách tính tỉ lệ vi phạm, phân biệt...” | Chuyển thành yêu cầu đầy đủ: “Hệ thống phải áp dụng thống nhất công thức tính tỷ lệ và phân biệt khung giờ khai báo với thời điểm xác nhận trong video.” |
| 68 | “live camera” | Có thể thống nhất thành “luồng camera trực tiếp”. |

Các chỉnh sửa nhỏ khác: thống nhất `use case`/`UseCase`, “tỷ lệ”/“tỉ lệ”, “hộp giới hạn”/“khung giới hạn”; thống nhất dấu chấm hoặc dấu hai chấm sau số chương; bổ sung dấu chấm còn thiếu cuối một số đoạn. Danh mục viết tắt nên có IoU, AP, mAP, TP, FP, FN, MAE vì xuất hiện nhiều trong nội dung. Đây là chỉnh biên tập, không phải các lỗi khoa học độc lập.

Một chi tiết có thể bổ sung để mô tả đúng triển khai: tracker hiện điều chỉnh khoảng cách ghép theo trạng thái trước khi chọn cặp, trong khi mục 3.3.2 trang 47 mới mô tả khoảng cách tâm. Nếu thuật toán này được dùng thực nghiệm, nên ghi rõ cách tính và tham số.

## 5. Lỗi bố cục đã thấy trên bản hiển thị Word

| Vị trí | Hiện tượng | Cách sửa |
|---|---|---|
| Trang 56–57, Bảng 4.2 | Caption và riêng hàng tiêu đề nằm cuối trang 56; dữ liệu bắt đầu ở trang 57 | Giữ caption và hàng tiêu đề đi cùng ít nhất hàng dữ liệu đầu; có thể chuyển cả bảng sang trang sau. |
| Trang 63–64, Bảng 4.10 | Cuối trang 63 chỉ còn caption và hàng tiêu đề; nội dung sang trang 64 | Điều chỉnh như Bảng 4.2. |
| Trang 10–11, Bảng 1.1 | Một hàng cuối bị đẩy riêng sang trang 11 | Bảng ngắn nên ưu tiên giữ nguyên trên một trang. |
| Trang 45–46, Bảng 3.4 | Bảng quy tắc ngắn bị chia qua hai trang | Chuyển hoặc cân lại khoảng cách để các trạng thái nằm cùng nhau. |
| Các bảng nhiều trang, gồm bảng use case | Trang tiếp theo không lặp hàng tên cột tương ứng, khó theo dõi | Dùng Repeat Header Rows với bảng có cấu trúc phù hợp; tránh tách một hàng thành vài dòng lẻ sang trang sau. |
| Trang 59, Bảng 4.7 | Từ “Precision” bị xuống dòng giữa từ | Tăng chiều rộng cột, giảm khoảng thừa ở cột khác hoặc điều chỉnh cỡ chữ nhất quán. |
| Trang 12 | Chỉ có vài dòng cuối kết luận Chương 1, phần còn lại gần như trống | Cân lại đoạn cuối Chương 1 để tránh trang đuôi quá ngắn; vẫn giữ Chương 2 bắt đầu trang mới nếu mẫu yêu cầu. |

Một số hình giao diện chứa nhiều chữ nhỏ; cần kiểm tra ở kích thước in. Hình 2.1 minh họa khung helmet/no-helmet bao cả người/xe, khác với phần văn bản mô tả nhãn vùng đầu; nên chỉnh riêng phần minh họa đầu ra hoặc thay bằng dự đoán thật đúng quy ước. Không từ hình minh họa này suy ra rằng bộ dữ liệu đã gán nhãn sai.

## 6. Những nội dung đã kiểm tra và không nên sửa nhầm

- Tổng số ảnh trong Bảng 4.3 đúng: 4.705 + 1.460 + 823 = 6.988.
- Tổng số đối tượng đúng: 21.142 + 6.361 + 3.530 = 31.033; ba lớp trong tập kiểm thử có 992 + 1.742 + 796 = 3.530 đối tượng.
- F1 từng lớp và F1 trung bình trong Bảng 4.6–4.7 phù hợp với cách tính trung bình theo lớp, có sai khác làm tròn rất nhỏ. Không thay F1 trung bình bằng công thức tính từ Precision/Recall trung bình rồi kết luận bảng sai.
- Trong mô tả ma trận nhầm lẫn, 691 + 31 + 74 = 796 là đúng. Recall tại ngưỡng dựng ma trận có thể khác Recall trong bảng tổng hợp; cần bổ sung cấu hình đánh giá, không tự sửa số cho trùng.
- Các công thức chính của Chương 2 không có lỗi đại số rõ ràng ở mức trình bày hiện tại. Ký hiệu số đếm dự đoán có dấu mũ và số đếm thực tế là hai ký hiệu khác nhau trong tài liệu gốc.
- Sơ đồ cơ sở dữ liệu phù hợp quan hệ giữa sáu bảng ở mức khái quát.
- Hạn chế chưa xử lý camera trực tiếp, chưa phân biệt chắc chắn lái/ngồi sau và chưa loại trùng giữa nhiều video đã được công khai. Những giới hạn đó không tự thân là lỗi; cần bảo đảm mục tiêu, số đếm và kết luận không vượt quá chúng.

**Thứ tự xử lý đề nghị:** chốt mô hình và lượt chạy → đối chiếu lại số liệu → bổ sung/thu hẹp kết luận thực nghiệm → thống nhất mô tả thuật toán với bản triển khai → sửa dẫn bảng và nguồn tài liệu → cập nhật danh mục và dàn trang lần cuối.
