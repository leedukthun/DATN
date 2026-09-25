# Rà soát Chương 4, Kết luận và Tài liệu tham khảo

Ngày rà soát: 24/09/2026. Đối tượng: bản DOCX người dùng cung cấp. Trang dưới đây là số trang in; PDF tương ứng lớn hơn 10 trang. Không sửa báo cáo hoặc mã nguồn. Checkpoint trong workspace chỉ được dùng để phát hiện điểm cần đối chiếu, không mặc định chúng chính là checkpoint tạo số liệu báo cáo. Metadata được đọc bằng `pickletools`, không thực thi pickle và không chạy mô hình.

## Những điểm cần sửa hoặc làm rõ trước tiên

### R1 — Mâu thuẫn danh tính mô hình và phương pháp tạo mô hình ba lớp

- Mức độ: nghiêm trọng; **mâu thuẫn trong báo cáo là chắc chắn**. Nguồn số liệu/checkpoint cần tác giả xác nhận.
- Vị trí: 4.2.2, trang 58, block 679; 4.2.5, trang 60, block 702; lặp trong 4.5.1, trang 66, block 752 và Kết luận, trang 68, block 769.
- Trích: “sử dụng trọng số YOLOv8n ... hai lớp ... làm điểm khởi tạo”; nhưng mục so sánh ghi “YOLOv8n hai lớp và YOLO11n ba lớp”.
- Tinh chỉnh trực tiếp checkpoint YOLOv8n trên bộ ba lớp không tự đổi kiến trúc thành YOLO11n. Notebook hiện có gọi `YOLO(OLD_WEIGHTS)` rồi `.train(...)`, không có bước chuyển sang kiến trúc YOLO11n; tiêu đề notebook tự gọi YOLO11 không chứng minh được kiến trúc.
- Đối chiếu bổ sung: `backend/models/best.pt` hiện có chứa C2f và `model=yolov8n.pt`; `best_3class.pt` chứa C3k2, `yolo11n.yaml`, `model=yolo11n.pt`, run name `train_lan_1_datasetdefault_doc_lap`. Các tệp hiện tại ủng hộ kịch bản YOLO11n ba lớp được huấn luyện từ checkpoint YOLO11n, chứ không phải trực tiếp từ YOLOv8n hai lớp.
- Cách sửa: chốt một run gốc và đường dẫn/hash checkpoint. Nếu run thực là YOLO11n từ trọng số tiền huấn luyện, sửa mô tả phương pháp xuyên suốt thành huấn luyện/tinh chỉnh YOLO11n trên ba lớp và so sánh với baseline YOLOv8n hai lớp. Nếu có run fine-tune trực tiếp YOLOv8n, cung cấp checkpoint/log đúng và dùng thống nhất số liệu run đó. Không chỉ đổi một chữ YOLO11n thành YOLOv8n để che mâu thuẫn.

### R2 — Bảng cấu hình và kết quả validation không khớp checkpoint ba lớp đang có

- Mức độ: nghiêm trọng; **sai khác đã xác minh**, chưa kết luận bảng sai nếu checkpoint báo cáo là file khác.
- Vị trí: Bảng 4.4, trang 58–59, block 684; đoạn lựa chọn epoch 88 và Bảng 4.5, trang 59, blocks 687–689.
- Bảng 4.4 ghi tốc độ học ban đầu khai báo 0,001. Metadata `best_3class.pt` hiện tại ghi `lr0=0.01`.
- Bảng 4.5 ghi P=88,322%, R=85,794%, mAP@50=92,499%, mAP@50–95=66,512%. `train_results` của checkpoint hiện tại tại epoch 88 ghi lần lượt **90,095%; 87,116%; 93,317%; 69,668%**. Epoch 88 thực sự là epoch đạt mAP@50–95 lớn nhất trong lịch sử 100 epoch của file này.
- Chứng cứ: `checkpoint_metadata_review.json`, tái tạo bằng `inspect_checkpoint_metadata.py`. Hash checkpoint ba lớp: `abfd3720fa50190d7408b7900959ee82f10c0ace8c5e86d2d57840d4362fb30c`.
- Cách sửa: truy nguyên `args.yaml`, `results.csv`, JSON đánh giá và checkpoint của **cùng một run**. Không tự thay số kiểm thử bằng số validation và không tự thay bảng bằng metadata của checkpoint khác. Gắn tên run/hash trong phụ lục để tránh trộn các lần thực nghiệm.

### R3 — Thiếu nguồn dữ liệu, nguồn trọng số và mô tả xử lý trùng lặp đủ để tái lập

- Mức độ: thiếu sót phương pháp quan trọng; **thiếu trong báo cáo là chắc chắn**, rò rỉ thực tế cần xác minh.
- Vị trí: 4.2.1, trang 57–58, blocks 672–677; 4.2.5, trang 60, block 702; danh mục tham khảo trang 69.
- Chỉ có số lượng ảnh và đối tượng. Chưa nêu tên/bản phát hành/URL bộ dữ liệu, cách tạo ba lớp, nguồn checkpoint hai lớp, quy trình chia nhóm, seed hoặc cách xác định “mã nguồn trùng”. Không có tài liệu tham khảo cho dữ liệu hay checkpoint.
- Mục so sánh nói loại 332/823 ảnh trùng nguồn train/validation của “bộ dữ liệu gốc”, còn đánh giá chính ở mục 4.2.4 vẫn dùng 823 ảnh. Chưa xác định bộ gốc là tập đã huấn luyện baseline hay tập huấn luyện mô hình cuối. Vì vậy chưa thể biết tập kiểm thử 823 ảnh có độc lập với toàn bộ dữ liệu mô hình đã học hay không. **Không được kết luận chắc chắn có rò rỉ chỉ dựa vào câu này.**
- Cách sửa: bổ sung tên và phiên bản dữ liệu, URL, lớp/ID, nguồn gán nhãn, quy tắc chia và loại trùng; ghi rõ tập gốc nào liên quan đến 332 ảnh, lập bảng đối chiếu số ảnh trước/sau lọc cho từng checkpoint. Nếu có rò rỉ với mô hình cuối, dùng tập độc lập để đánh giá lại; nếu chỉ trùng với dữ liệu huấn luyện baseline, giải thích rõ.

### R4 — Chưa chứng minh đủ các mục tiêu về đếm, báo nhầm người đi bộ và tốc độ hệ thống

- Mức độ: thiếu bằng chứng thực nghiệm quan trọng; **chắc chắn trong nội dung báo cáo**.
- Vị trí: 4.4, trang 63–65, blocks 728–748; đối chiếu mục tiêu blocks 142, 154, 164 và mô tả kiểm chứng block 599.
- Bảng 4.10 liệt kê “Đối chiếu số đếm và đo thời gian xử lý”, kiểm tra số lượng/minh chứng/tệp tải xuống. Tuy nhiên 4.4.3 chỉ có Hình 4.7 (một ảnh), 4.4.4 chỉ có các tình huống tracker giả lập. Không có bảng số đếm thủ công–hệ thống trên video, FP/FN sự kiện, đếm trùng, tỷ lệ gán ID sai, số báo nhầm người đi bộ trước/sau liên kết hoặc thời gian toàn luồng.
- 8 kiểm thử đơn vị/API chứng minh được các quy tắc đã kiểm tra, không đủ thay thế đánh giá video thực tế. Báo cáo đã tự thừa nhận thiếu kiểm thử toàn luồng ở blocks 730, 740, 762; nên giữ sự thận trọng này.
- Cách sửa: bổ sung video/ảnh đối chứng có ground truth, nêu độ dài, FPS, độ phân giải, số người/xe, điều kiện quan sát; báo cáo đếm đúng/sai/bỏ sót/trùng, thời gian xử lý và cấu hình stride. Với mục tiêu giảm báo nhầm người đi bộ, cần tập có người đi bộ và so sánh bật/tắt quy tắc liên kết. Nếu chưa thực hiện, ghi rõ mục tiêu mới đạt ở mức triển khai, chưa định lượng hiệu quả.

### R5 — Phạm vi so sánh hai mô hình và điều kiện đo chưa rõ

- Mức độ: thiếu sót cần làm rõ, không phải lỗi phép tính.
- Vị trí: 4.2.5, Bảng 4.8–4.9, trang 60; blocks 702–708.
- Đổi cả kiến trúc (YOLOv8n/YOLO11n), tập/lịch sử huấn luyện và số lớp nên kết quả chỉ hỗ trợ “checkpoint ba lớp tốt hơn checkpoint hai lớp trên tập đối chứng này”. Không tách được tác động riêng của việc thêm lớp bike hay của liên kết đầu–xe.
- “IoU 0,50” chưa nói rõ là IoU ghép prediction–ground truth hay ngưỡng NMS. AP/mAP chưa nêu có quét confidence đầy đủ hay lọc ở 0,40; nếu lọc ở 0,40 rồi tính AP sẽ làm mất đoạn PR ở confidence thấp. Đây là yêu cầu mô tả/xác minh, **chưa khẳng định AP bị tính sai**.
- Cách sửa: ghi hai ngưỡng IoU riêng (NMS và matching), cách remap lớp chung, macro/micro, confidence dùng cho AP, script tính và danh sách 491 ảnh; nếu kết luận hiệu quả của lớp xe, cần thí nghiệm cùng kiến trúc và cùng quy trình.

### R6 — Không đủ thông tin tái lập số liệu thời gian CPU

- Mức độ: thiếu phương pháp đo.
- Vị trí: Bảng 4.2, trang 56–57, block 667; Bảng 4.8, trang 60, block 704.
- Có 86,74 và 93,23 ms/ảnh nhưng chưa có CPU/RAM, phiên bản Python/PyTorch/Ultralytics, số luồng, batch, warm-up, số lần lặp, phạm vi đo (inference hay cả tiền/hậu xử lý). Bảng môi trường chỉ ghi tên công nghệ.
- Đây là tốc độ mô hình trên ảnh, không phải FPS toàn hệ thống video. Mô hình ba lớp trong bảng chậm hơn khoảng 7,48%; không nên rút kết luận cải thiện tốc độ từ bảng này.
- Cách sửa: thêm cấu hình máy và quy trình đo, trung bình/độ phân tán, tách inference và tổng thời gian xử lý.

### R7 — Điều kiện các chỉ số test và ma trận nhầm lẫn chưa được nêu đủ

- Mức độ: thiếu thuyết minh tái lập.
- Vị trí: 4.2.4, trang 59–60, blocks 691–700.
- Báo cáo có chú thích hợp lý rằng ma trận và P/R tổng hợp có thể dùng điều kiện khác. Tuy nhiên không cho biết chính xác các ngưỡng tương ứng; cũng không đính kèm ma trận/đường cong PR dù nhận xét về chúng.
- Cách sửa: thêm các hình hoặc phụ lục kết quả, confidence và IoU cho từng cách tính; nêu P/R của thư viện tại điểm tối ưu F1 nếu đúng quy trình. Không coi 691/796 khác Recall 82,161% là lỗi số học trước khi đồng nhất điều kiện đánh giá.

### R8 — Câu kết luận “các chỉ số đều ổn định” vượt quá bằng chứng

- Mức độ: diễn đạt kết luận chưa có cơ sở.
- Vị trí: Kết luận, trang 68, block 769.
- Trích: “Kết quả đánh giá trên tập kiểm thử các chỉ số đều ổn định”. Báo cáo cho một lần huấn luyện/đánh giá và một tập đối chứng, không có độ phân tán qua nhiều seed, nhiều cảnh hoặc phân nhóm điều kiện để kết luận ổn định. Câu còn thiếu dấu chấm cuối.
- Cách sửa: thay bằng kết quả cụ thể và phạm vi, ví dụ “Trên tập kiểm thử ... mô hình đạt ...; kết quả mới phản ánh bộ dữ liệu đã đánh giá”. Nếu dùng từ ổn định, cần báo cáo thí nghiệm lặp/phân tích độ biến thiên.

### R9 — Khẳng định nguyên nhân sai số ở kết luận mạnh hơn phần hạn chế

- Mức độ: cần sửa cách kết luận.
- Vị trí: Kết luận, trang 68, block 771 so với 4.5.2, trang 66, block 757.
- Kết luận ghi bỏ sót/nhầm “do các yếu tố dữ liệu”, trong khi 4.5.2 đúng hơn khi viết các yếu tố “có thể góp phần” và “cần đối chiếu từng ảnh”. Chưa có phân tích lỗi để quy nguyên nhân.
- Cách sửa: dùng “có thể liên quan đến ...; chưa phân tích đầy đủ nguyên nhân” hoặc bổ sung phân loại lỗi thực tế. Những lợi ích quản lý ở block 772 nên trình bày là tiềm năng vì chưa có đánh giá người dùng hoặc thời gian tiết kiệm.

## Lỗi chắc chắn về biên tập và tham khảo

### R10 — Hai tham chiếu bảng sai

- Trang 64, block 736: “trình bày trong bảng 4.9” phải là **Bảng 4.11** ngay sau đó.
- Trang 65, block 745: “Kết quả được nêu trong bảng 4.10” phải là **Bảng 4.12** ngay sau đó.
- Block 746: chú thích Bảng 4.12 dùng style Normal, khác các chú thích bảng khác dùng style Bảng; có thể làm danh mục bảng/định dạng không đồng nhất.

### R11 — Lỗi chính tả/câu và thuật ngữ

- Trang 60, block 702: “dưới dây” → **“dưới đây”**. Câu rất dài và “... IoU 0,50 được thể hiện...” nên tách thành hai câu.
- Trang 56, block 665: “Được thể hiện qua bảng 4.2:” là câu thiếu chủ ngữ; sửa “Môi trường triển khai và kiểm thử được tổng hợp trong Bảng 4.2.”
- Trang 68, block 773: “live camera” nên thống nhất “camera trực tiếp” hoặc “luồng video trực tiếp từ camera”.
- Bảng 4.9 ghi “nhãn NO-HELMET” trong khi tên lớp còn lại là `no-helmet`; nên giữ tên lớp đúng mapping và phân biệt tên lớp với trạng thái `NO_HELMET` trong hệ thống.

### R12 — Tài liệu tham khảo thiếu thông tin nhận dạng và chưa đồng nhất

- Trang 69, blocks 778–789.
- [2] thiếu năm, volume, mã bài/DOI; [3] thiếu năm và nơi công bố, kết thúc bằng dấu phẩy. [5]–[13] là tài liệu/phần mềm/trang web nhưng không có URL và ngày truy cập; [8], [10]–[13] còn thiếu dấu chấm cuối.
- [2] có thể hoàn thiện bằng thông tin đã đối chiếu: F. W. Siebert và H. Lin, “Detecting motorcycle helmet use with deep learning,” *Accident Analysis & Prevention*, tập 134, bài 105319, 2020, DOI 10.1016/j.aap.2019.105319. Nguồn bản tác giả: https://www.fsv.uni-jena.de/fsvmedia/98186/am-siebert-lin-2020-detecting-motorcycle-helmet-use-with-deep-learning-compressed.pdf
- [3] tối thiểu có thể dẫn đúng bản arXiv của L. Choi và R. Greer, 2024, arXiv:2408.02244, DOI 10.48550/arXiv.2408.02244, nếu đây là bản tác giả đã đọc: https://arxiv.org/abs/2408.02244. Nếu trích bản hội nghị, dùng metadata bản hội nghị thực tế thay vì trộn thông tin.
- [1] đã khớp WHO ấn bản 2, 2023: https://www.who.int/publications/i/item/9789240069824. Không có căn cứ đánh dấu nguồn này là sai.
- Cách sửa chung: áp dụng một chuẩn duy nhất của khoa; bài báo đủ tác giả/tên/nơi công bố/năm/volume/trang hoặc mã bài/DOI; website đủ tổ chức/tên trang/URL/ngày truy cập. Nếu mô hình cuối là YOLO11, bổ sung nguồn chính thức cho YOLO11 thay vì chỉ dẫn YOLOv8.

### R13 — Có công trình được nhắc đến nhưng thiếu nguồn tương ứng

- Block 228, trang phần tổng quan: câu “Aboah và cộng sự sử dụng YOLOv8...” không có số trích dẫn và không có Aboah trong [1]–[13]. Đây là thiếu dẫn nguồn chắc chắn.
- Công trình phù hợp nội dung câu: *Real-Time Multi-Class Helmet Violation Detection Using Few-Shot Data Sampling Technique and YOLOv8*, CVPR Workshops 2023; bản chính thức CVF: https://openaccess.thecvf.com/content/CVPR2023W/AICity/papers/Aboah_Real-Time_Multi-Class_Helmet_Violation_Detection_Using_Few-Shot_Data_Sampling_Technique_CVPRW_2023_paper.pdf
- Cách sửa: xác nhận đây là bài tác giả thực sự sử dụng, thêm vào danh mục và gắn số ngay câu tổng quan. Không gán [2] của Siebert/Lin cho câu Aboah.

### R14 — Vị trí một số trích dẫn chưa đúng phạm vi nguồn

- Block 357 trích “React, TypeScript và Vite[11]”; [11] là React Quick Start, không phải tài liệu Vite hoặc TypeScript. Dịch [11] về ngay sau React; thêm nguồn riêng nếu cần dùng nguồn để giải thích TypeScript/Vite.
- Block 320 gắn [8] OpenCV Getting Started with Videos ở đầu đoạn công thức lấy mẫu s và thời điểm. Nguồn này phù hợp thao tác đọc video; không nên trình bày như nguồn trực tiếp cho toàn bộ thiết kế lấy mẫu của đề tài nếu đó là suy luận/tự thiết kế. Đặt nguồn tại câu mô tả OpenCV, nêu rõ quy tắc lấy mẫu do hệ thống áp dụng.
- Block 298 dùng [6] Ultralytics Training cho học chuyển giao, trong khi [7] PyTorch Transfer Learning trực tiếp hơn. Đây là đề xuất chỉnh chất lượng trích dẫn, không khẳng định kiến thức học chuyển giao đang sai.

## Các điểm cần xác minh, không nên gọi là lỗi chắc chắn

### R15 — Tuyên bố kiểm thử dùng cơ sở dữ liệu/thư mục riêng chưa kèm cách tái lập

- Trang 64, block 734 ghi “cơ sở dữ liệu và thư mục lưu trữ riêng”. `backend/tests/test_api_crud.py` hiện tại dùng `TestClient(app)` trực tiếp, không thấy fixture/override DB; không có `tests/conftest.py`. Mã cấu hình lấy DB từ biến môi trường nên việc tách DB có thể được thực hiện bằng lệnh chạy bên ngoài.
- Cách sửa: bổ sung lệnh/env cấu hình hoặc log chạy kiểm thử để xác nhận. Không kết luận chắc chắn bài kiểm thử đã tác động DB thật và không chạy suite trong quá trình chỉ rà soát này.
- Hai bài API và sáu bài logic đúng với hai tệp `test_api_crud.py`/`test_ai_logic.py` hiện có. Workspace còn các tệp kiểm thử bổ sung khác, nên nên nêu rõ “8 bài trong phạm vi hai tệp...” và ngày/commit thực thi. Không có log trong báo cáo để tự xác nhận chúng đã pass ở lần báo cáo.

### R16 — Hình 4.8 chưa có nhãn đúng đối chứng để suy ra cải thiện

- Trang 66, blocks 752–753, media/image20.png. Hình bên trái đếm tổng 6, bên phải đếm tổng 5; cả hai không mũ bằng 0. Hình có thể minh họa thay đổi vùng đối tượng, nhưng thiếu ground truth và lời giải thích đối tượng nào đúng/sai, nên không tự chứng minh mô hình sau tốt hơn về đếm.
- Cách sửa: chú thích rõ số đối tượng đúng theo quy ước đề tài, phân tích khung đúng/sai/bỏ sót. Phân biệt khung đầu ở baseline và khung xe ở hệ thống có liên kết vì đơn vị đếm có thể thay đổi. Không kết luận bên nào sai chỉ từ ảnh này.

## Các phép kiểm tra cho kết quả đúng — tránh sửa nhầm

- Bảng 4.3: 4.705 + 1.460 + 823 = 6.988 ảnh; 21.142 + 6.361 + 3.530 = 31.033 đối tượng.
- Phân bố lớp train: 5.483 + 10.812 + 4.847 = 21.142.
- Phân bố lớp test: 992 + 1.742 + 796 = 3.530.
- Bảng 4.7: F1 tính từ P/R từng lớp ra 89,921%; 89,883%; 86,031% sau làm tròn. Trung bình ba F1 là 88,612%, đúng Bảng 4.6. Trung bình P/R/AP cũng khớp toàn bộ Bảng 4.6.
- Tổng ma trận nêu cho no-helmet: 691 + 31 + 74 = 796, khớp số mẫu lớp.
- Tập đối chứng: 823 − 332 = 491, đúng.
- Bảng 4.9: no-helmet có TP+FN=610 ở cả hai mô hình. Các P/R/F1 suy ra chỉ riêng no-helmet khác P/R/F1 trung bình hai lớp ở Bảng 4.8 là điều bình thường; không phải mâu thuẫn.
- Bảng 4.12 có 5 hàng kịch bản nhưng nói nằm trong 4 bài test tracker: phù hợp vì test xác nhận một lần đồng thời bao phủ xác nhận ở quan sát thứ ba và không phát sinh lại sự kiện.

