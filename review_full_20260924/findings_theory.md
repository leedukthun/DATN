# Rà soát mở đầu, Chương 1 và Chương 2

Phạm vi đã đọc: toàn bộ blocks 0–429, bao gồm các bảng, công thức OMML trong `word/document.xml` và hình 2.1 (`media/image1.png`). Đối chiếu thêm các đoạn liên quan ở Chương 3–4 và danh mục tài liệu tham khảo để kiểm tra liên kết nội dung. Không sửa tài liệu nguồn.

## Các vấn đề chắc chắn hoặc nhìn thấy trực tiếp

### T1. Phạm vi “người điều khiển” chưa khớp đối tượng hệ thống thực sự xác định — quan trọng

- Vị trí: tên đề tài blocks 9/37; mục tiêu block 133; phạm vi block 152; mục 1.2.3.2 block 220; đối chiếu blocks 540/550/568/600.
- Trích dẫn block 152: “Tập trung phát hiện người điều khiển xe máy không đội mũ; chưa phân biệt chắc chắn người lái và người ngồi sau”.
- Trích dẫn block 220: “việc xác định vùng đầu có liên quan đến xe chưa đủ để phân biệt chắc chắn người lái với người ngồi sau”.
- Nhận xét: Báo cáo có công khai hạn chế, vì vậy không phải che giấu hay tự mâu thuẫn hoàn toàn. Tuy nhiên, đối tượng được cam kết trong tên đề tài và mục tiêu là người lái, trong khi đầu ra thực tế là xe có ít nhất một người không đội mũ. Ví dụ lái xe có mũ, người ngồi sau không mũ vẫn là NO_HELMET; không thể dùng số đó để kết luận số người điều khiển không mũ.
- Cách sửa: Nếu tên đề tài đã được duyệt, giữ tên nhưng xác định rõ mục tiêu thực nghiệm đã thu hẹp là phát hiện trường hợp trên xe có người không đội mũ, nêu đây là hạn chế mức độ đáp ứng đề tài. Nếu được phép đổi tên, thống nhất thành “người đi xe máy” hoặc “trường hợp đi xe máy không đội mũ”. Không nên chỉ thêm một dòng giới hạn rồi vẫn gọi đầu ra là người điều khiển ở nơi khác.

### T2. Thiếu nguồn cho công trình Aboah — chắc chắn

- Vị trí: mục 1.3.2, block 228; danh mục blocks 777–789.
- Trích dẫn: “Aboah và cộng sự sử dụng YOLOv8 cho bài toán phát hiện vi phạm đội mũ, chú trọng lựa chọn mẫu khi dữ liệu gán nhãn còn hạn chế.”
- Vấn đề: Câu không có số tham chiếu; danh mục 13 tài liệu không có công trình Aboah. Người đọc không truy lại được nguồn.
- Sửa: Thêm tham chiếu và tài liệu: A. Aboah, B. Wang, U. Bagci, Y. Adu-Gyamfi, “Real-Time Multi-Class Helmet Violation Detection Using Few-Shot Data Sampling Technique and YOLOv8,” CVPR Workshops, 2023, pp. 5350–5358; đánh lại số dẫn nếu cần.
- Đã xác minh nguồn chính: [CVF Open Access](https://openaccess.thecvf.com/content/CVPR2023W/AICity/html/Aboah_Real-Time_Multi-Class_Helmet_Violation_Detection_Using_Few-Shot_Data_Sampling_Technique_CVPRW_2023_paper.html). Mô tả kỹ thuật trong báo cáo phù hợp tóm tắt paper; lỗi là thiếu dẫn nguồn.

### T3. Tham chiếu [11] gắn vào Vite nhưng tài liệu là React — chắc chắn

- Vị trí: mục 2.3.2, block 357; tài liệu [11] ở block 787.
- Trích dẫn: “Phần giao diện được xây dựng bằng React, TypeScript và Vite[11].”
- Tài liệu [11]: “React, ‘Quick Start,’ React Documentation”.
- Sửa: Đặt `[11]` ngay sau React hoặc sau câu mô tả React; thêm nguồn riêng cho TypeScript và Vite nếu muốn dẫn cho hai công nghệ đó. Thêm khoảng trắng trước dấu ngoặc tham chiếu, tương tự `FastAPI[10]` (356), `SQLAlchemy[12]` (358).
- Nguồn chính: [React Quick Start](https://react.dev/learn), [Vite Getting Started](https://vite.dev/guide/).

### T4. Lỗi gõ hai dấu hai chấm — chắc chắn

- Vị trí: mục 2.1.4, phần giải thích công thức (2.1), block 306.
- Nguyên văn: “xᵢ: : ảnh huấn luyện thứ i;”.
- Sửa thành: “xᵢ: ảnh huấn luyện thứ i;”.

### T5. Cách ghi cấu trúc dòng nhãn YOLO không chuẩn và dễ gây hiểu nhầm — cần sửa nhỏ

- Vị trí: mục 2.1.3.1, block 283.
- Nguyên văn: “mỗi đối tượng được biểu diễn trên một dòng với năm thành phần: class_id, x_center y_center, width height”.
- Vấn đề: Dấu phẩy và khoảng trắng bị dùng lẫn lộn; nếu coi phần sau dấu hai chấm là mẫu dòng nhãn thì sai cú pháp. Năm trường trong file nhãn được phân tách bằng khoảng trắng.
- Sửa bằng dòng mã rõ ràng: `class_id x_center y_center width height`; thêm “các trường phân tách bằng khoảng trắng”. Nội dung chuẩn hóa tọa độ ở block 288 đang đúng.
- Nguồn chính: [Ultralytics – Object Detection Datasets](https://docs.ultralytics.com/datasets/detect/).

### T6. Đối tượng sử dụng thay đổi giữa các chương — cần thống nhất mô tả

- Vị trí: mục 1.2.1 block 196; mục 1.2.2.2 block 211; đối chiếu mục 3.1.1.1 block 434.
- Block 196: “Đối tượng sử dụng hệ thống là cán bộ Phòng Cảnh sát giao thông...”.
- Block 434: “Đối tượng sử dụng là người có nhu cầu quản lý, phân tích dữ liệu ảnh và video giao thông, chẳng hạn người thực hiện khảo sát hoặc người phụ trách tổng hợp số liệu...”.
- Hai mô tả không loại trừ nhau nhưng một nơi quy định đối tượng cụ thể, nơi khác mở rộng không giải thích. Sửa thống nhất thành đối tượng sử dụng chung, với cán bộ CSGT là ví dụ/nhóm dự kiến, hoặc dùng đúng nhóm CSGT xuyên suốt. Không nên khiến người đọc hiểu đã khảo sát yêu cầu chính thức từ cơ quan này khi chưa có dữ liệu khảo sát.

### T7. Một số thiếu sót trình bày nhỏ

- Block 75: danh mục từ viết tắt thiếu những chỉ số dùng nhiều trong nội dung: IoU, AP, mAP, TP, FP, FN, MAE. Đây là gợi ý hoàn thiện, không phải lỗi công thức.
- Blocks 368–369: giải thích `B_p ∩ B_g` và `B_p ∪ B_g` là “diện tích”, trong khi công thức (2.6) dùng `|B_p ∩ B_g|`, `|B_p ∪ B_g|`. Nên giữ cả dấu giá trị/độ đo trong dòng giải thích, hoặc nói “vùng giao”, “vùng hợp” rồi định nghĩa dấu `|.|` là diện tích.
- Block 361: đoạn kết ở `[13]` chưa có dấu chấm.
- Thống nhất “khung giới hạn” (260/261/276) với “hộp giới hạn” (234); “tỷ lệ” với “tỉ lệ” (270); “tracking” (251) với “theo dõi đối tượng”. Đây là biên tập thuật ngữ, không phải khác biệt kỹ thuật.

## Các vấn đề cần đối chiếu thực nghiệm/triển khai trước khi kết luận

### V1. Mục tiêu quan trọng chưa chắc có phép đánh giá tương ứng

- Block 142: “So sánh hệ thống sử dụng mô hình hai lớp với hệ thống sử dụng mô hình ba lớp kết hợp liên kết đối tượng, chú trọng khả năng giảm báo nhầm đối với người đi bộ, mức độ bỏ sót và tốc độ xử lý.”
- Blocks 154/164 hứa đánh giá “báo nhầm người đi bộ, bỏ sót, sai số đếm và tốc độ xử lý”; mục 2.4.3 đã định nghĩa MAE và FPS.
- Cần Chương 4 có số đo cấp hệ thống sau liên kết/theo dõi trên dữ liệu đối chứng phù hợp: người đi bộ bị ghi nhầm, người đi xe bị bỏ sót, sai số đếm mỗi video, thời gian toàn hệ thống. AP/Precision/Recall của detector trên nhãn helmet/no-helmet không thay thế được những phép đo này.
- Nếu chưa đo, nên bổ sung thực nghiệm hoặc ghi thẳng đây là mục tiêu chưa hoàn thành, thay vì giữ toàn bộ cam kết và kết luận đã đạt.

### V2. Cần xác minh quá trình “từ checkpoint hai lớp thành ba lớp”

- Chương 2 block 256 mô tả “huấn luyện tinh chỉnh từ checkpoint hai lớp sang mô hình ba lớp”; block 300 mô tả cách kế thừa tham số tương thích, về lý thuyết là hợp lý.
- Nhưng block 679 nói điểm khởi tạo là YOLOv8n hai lớp; block 702 so sánh “YOLOv8n hai lớp và YOLO11n ba lớp”. Hai họ kiến trúc khác nhau cần được giải thích bằng lệnh huấn luyện/cấu hình/checkpoint thực tế. Không thể mặc nhiên gọi đây chỉ là tăng số lớp trên cùng mô hình.
- Cần agent rà soát thực nghiệm xác định checkpoint mới thực chất là YOLOv8n hay YOLO11n, nguồn checkpoint ban đầu, tỷ lệ/tầng trọng số kế thừa; sau đó sửa mô tả thống nhất.

### V3. Hình 2.1 có minh họa đầu ra không giống đơn vị gán nhãn mô tả

- Hình 2.1 ở block 267/268 (`media/image1.png`) vẽ ba khung `bike`, `helmet`, `no-helmet` bao gần trọn người/xe tương ứng. Trong văn bản (199/237) hai lớp helmet/no-helmet là vùng đầu, còn bike là phương tiện riêng.
- Đây có thể chỉ là hình minh họa, chưa đủ kết luận dữ liệu huấn luyện sai. Nên thay phần đầu ra bằng ảnh dự đoán thật có khung đầu và xe đúng quy ước, hoặc ghi rõ minh họa và chỉnh các khung cho đúng đối tượng.

## Phần kiểm tra không phát hiện lỗi kỹ thuật đáng kể

- Các công thức (2.1)–(2.13) đúng ở mức đang trình bày: empirical detection loss, bước lấy mẫu video, điều kiện tâm trong hình chữ nhật, tọa độ tâm, khoảng cách Euclid, IoU, Precision, Recall, F1, mAP, sai số tuyệt đối, MAE, FPS suy luận.
- Hai ký hiệu ở blocks 412/413 KHÔNG trùng nhau trong tài liệu gốc: 412 là n có dấu mũ, 413 không có dấu mũ. Bản trích xuất văn bản làm mất accent; không báo lỗi này.
- Các bảng công thức nhìn như trống trong `report_all.txt` do trích xuất `cell.text` không lấy OMML, không phải tài liệu bị mất công thức.
- Cách phân biệt lỗi detector với lỗi suy luận nghiệp vụ ở block 235 đúng và hữu ích; các giới hạn đầu ra/tracking được nêu khá rõ.
- Mô tả nghiên cứu Siebert–Lin và Choi–Greer đúng với abstract paper. Tài liệu tham khảo của chúng chưa đủ thông tin (năm, nơi xuất bản/DOI), nên agent rà soát tài liệu tham khảo bổ sung.
- Nguồn đối chiếu: [Siebert–Lin](https://arxiv.org/abs/1910.13232), [Choi–Greer](https://arxiv.org/abs/2408.02244).

## Bổ sung đối chiếu nguồn và trang

- T1: mục tiêu trang 2; phạm vi trang 3 và trang 8.
- T2: đoạn Aboah/Siebert trang 9; tài liệu tham khảo trang 69.
- T3: trang 20; tài liệu [11] trang 69.
- T4: trang 16.
- T5: trang 15.
- T6: mô tả CSGT trang 6 và 8.
- V3: Hình 2.1 trang 14.

Các mục thư mục có thể bổ sung ngay, dựa trên nguồn đã xác minh:

1. F. W. Siebert and H. Lin, “Detecting motorcycle helmet use with deep learning,” *Accident Analysis & Prevention*, vol. 134, article 105319, 2020, doi: [10.1016/j.aap.2019.105319](https://doi.org/10.1016/j.aap.2019.105319). Năm trên bản preprint là 2019, nhưng năm của số tạp chí là 2020; [bản arXiv do tác giả đăng](https://arxiv.org/abs/1910.13232) ghi rõ cả journal reference và DOI. Mô tả tại block 228 đúng; mục [2] chỉ bị thiếu thông tin thư mục.
2. A. Aboah, B. Wang, U. Bagci, and Y. Adu-Gyamfi, “Real-Time Multi-Class Helmet Violation Detection Using Few-Shot Data Sampling Technique and YOLOv8,” in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR) Workshops*, 2023, pp. 5350–5358. Có thể dùng [CVF](https://openaccess.thecvf.com/content/CVPR2023W/AICity/html/Aboah_Real-Time_Multi-Class_Helmet_Violation_Detection_Using_Few-Shot_Data_Sampling_Technique_CVPRW_2023_paper.html); DOI bản preprint đã xác minh là [10.48550/arXiv.2304.08256](https://doi.org/10.48550/arXiv.2304.08256). Không ghép DOI preprint vào mục hội nghị mà không ghi rõ loại phiên bản. Mô tả ở block 228 đúng; thiếu cả số dẫn và mục tài liệu.
3. L. Choi and R. Greer, “Evaluating Vision-Language Models for Zero-Shot Detection, Classification, and Association of Motorcycles, Passengers, and Helmets,” *arXiv preprint arXiv:2408.02244*, 2024, doi: [10.48550/arXiv.2408.02244](https://doi.org/10.48550/arXiv.2408.02244). Đây là phương án trích dẫn phiên bản tác giả đã kiểm được từ [arXiv](https://arxiv.org/abs/2408.02244). Mô tả block 229 đúng; có thể bổ sung OWLv2 kết hợp CNN để phân biệt rõ phương pháp với YOLO. Trang IEEE tương ứng bị chặn robot nên chưa dùng siêu dữ liệu từ trang IEEE để chốt citation hội nghị.
