# Rà soát Chương 3 – phân tích, thiết kế và đối chiếu chọn lọc mã nguồn

Đã đọc toàn bộ blocks 430–651, bao gồm 8 bảng đặc tả use case, các bảng yêu cầu/kiến trúc/cơ sở dữ liệu/lưu trữ, công thức OMML và ảnh sơ đồ/giao diện image2–image10. Không chỉnh sửa báo cáo hoặc mã nguồn. Số trang dưới đây là số in trong báo cáo; PDF cao hơn 10 trang trong Chương 3.

## 1. Sai khác quan trọng cần xác nhận phiên bản triển khai

### D01 – Cao: quy tắc bỏ vùng đầu khi không phát hiện xe trái với mã nguồn đang có

- Vị trí: §3.3.1.4, block 571, trang 46 (PDF 56); lặp lại ở §3.3.4.3, block 611, trang 50 (PDF 60).
- Nguyên văn block 571: “Các vùng đầu chỉ được sử dụng để ghi nhận trạng thái khi có thể liên kết với một xe máy phù hợp. Nếu mô hình phát hiện vùng đầu nhưng không phát hiện được xe tương ứng, hoặc vùng đầu không thỏa mãn điều kiện liên kết với bất kỳ xe nào, phát hiện đó không được đưa vào số liệu có mũ hoặc không mũ của hệ thống.”
- Nguyên văn block 611: “Những vùng đầu không liên kết được với xe không được tính thành đối tượng độc lập.”
- Đối chiếu: `backend/app/services/ai/violation.py:101` có nhánh `if not vehicles:` trả một `SubjectDetection` cho từng vùng đầu có/không mũ. Nhánh này kiểm tra có phát hiện xe trong khung hình hay không, không kiểm tra checkpoint có 2 hay 3 lớp. Vì vậy ngay cả khi dùng checkpoint 3 lớp, khung hình không có detection xe vẫn đếm vùng đầu độc lập. `assess_image()` lấy `len(subjects)` làm tổng xe; video cũng đưa các subject đó vào tracker.
- Hệ quả: ảnh chỉ chứa người đi bộ hoặc khung hình bỏ sót toàn bộ xe vẫn có thể tạo đối tượng/NO_HELMET. Điều này ảnh hưởng trực tiếp phát biểu “đơn vị đếm là xe máy” và lập luận giảm báo nhầm người đi bộ ở blocks 549, 572, 610, 650.
- Cách sửa báo cáo: xác nhận chính xác phiên bản code/checkpoint đã dùng thực nghiệm. Nếu phiên bản này là bản nộp, báo cáo phải mô tả cơ chế dự phòng và giới hạn; nếu thiết kế đích thực sự chỉ đếm vùng đầu gắn xe, cần đồng bộ phần triển khai và chạy lại các kiểm thử liên quan trước khi giữ kết luận. Không thể chỉ đổi lời văn rồi xem số liệu cũ mặc nhiên còn hợp lệ.
- Độ chắc chắn: sai khác với workspace hiện tại là chắc chắn; việc đó có áp dụng bản thực nghiệm trong báo cáo hay không cần xác nhận phiên bản.

### D02 – Trung bình: thiếu/sai quy tắc phân loại HELMET và UNKNOWN cho cả video

- Vị trí: §3.3.4.3, block 612, trang 50 (PDF 60).
- Nguyên văn: “Những mã chưa đủ thông tin hoặc chưa đạt điều kiện xác nhận được giữ ở nhóm chưa xác định khi cần tổng hợp.”
- Vấn đề nội dung: câu này dễ hiểu rằng mọi track chưa đủ K lần NO_HELMET đều thuộc UNKNOWN, trong khi báo cáo vẫn hiển thị số có mũ ở use case và giao diện. Chưa có quy tắc xác định HELMET cho lịch sử cả track; bảng 3.4 chỉ xác định trạng thái tại một lần quan sát.
- Đối chiếu: `backend/app/services/ai/tracker.py:172–177`: NO_HELMET nếu `ever_no_helmet`; HELMET nếu `ever_helmet and not ever_no_helmet`; còn lại mới UNKNOWN. Ví dụ track từng thấy HELMET, sau đó thấy NO_HELMET hai lần với K=3 vẫn được tổng hợp vào HELMET, không phải UNKNOWN.
- Gợi ý: thêm ba quy tắc tổng hợp video rõ ràng theo trạng thái lịch sử; sửa câu thành “Các track chưa từng được quan sát HELMET và chưa đủ điều kiện xác nhận NO_HELMET thuộc nhóm UNKNOWN”, nếu đúng bản triển khai được đánh giá. Nêu UNKNOWN = tổng track − HELMET − NO_HELMET.
- Độ chắc chắn: thiếu quy tắc trong báo cáo là chắc chắn; đối chiếu phiên bản code vẫn cần xác nhận.

### D03 – Thấp/trung bình, bổ sung để tái lập: mô tả tracker chưa nêu điểm ghép thực tế có trọng số trạng thái

- Vị trí: §3.3.2, block 576, trang 47 (PDF 57).
- Nguyên văn: “Việc liên kết dựa trên khoảng cách giữa các tâm, ưu tiên các cặp gần nhau và nằm trong ngưỡng cho phép.”
- Đối chiếu: `backend/app/services/ai/tracker.py:155–170` giảm 15% khoảng cách khi trạng thái hiện tại giống trạng thái trước và khác UNKNOWN; sau đó dùng khoảng cách đã điều chỉnh để lọc ngưỡng và ghép greedy. Đây không hoàn toàn là xếp cặp theo khoảng cách hình học nguyên bản.
- Gợi ý: nếu báo cáo nhằm mô tả đúng thuật toán đã chạy, bổ sung công thức khoảng cách hiệu dụng và nêu lý do ưu tiên trạng thái. Đây là chi tiết còn thiếu, không phải toàn bộ mô tả Centroid Tracking sai.

## 2. Lỗi nội dung/nhất quán ngay trong báo cáo

### D04 – Trung bình: sơ đồ kiến trúc gán tác vụ theo dõi cho mô hình YOLO

- Vị trí: Hình 3.2, ảnh image3.png nằm ở block 502, chú thích block 503; trang 39 (PDF 49).
- Nguyên văn trong hình: “Mô hình YOLO” / “Nhận diện & theo dõi”.
- Mâu thuẫn: bảng 3.3 (block 507) phân vai mô-đun YOLO là dự đoán khung giới hạn/nhãn/độ tin cậy, còn §3.3.2 (block 575) nói hệ thống dùng Centroid Tracking. Code cũng tách `Detector` và `CentroidTracker`.
- Gợi ý: đổi nhãn dưới “Mô hình YOLO” thành “Nhận diện đối tượng”; thể hiện Centroid Tracking trong dịch vụ xử lý ảnh/video hoặc thêm thành phần riêng nếu cần. Không gán khả năng theo dõi của pipeline cho checkpoint nhận diện.

### D05 – Trung bình: tiền điều kiện use case Quản lý dự án không phù hợp luồng tạo mới

- Vị trí: §3.1.5.3, bảng block 483, bắt đầu trang 31 (PDF 41).
- Nguyên văn ô Tiền điều kiện: “Người dùng đã đăng nhập; thao tác với dự án hiện có”.
- Mâu thuẫn: luồng cơ bản ngay dưới gồm “Chọn tạo dự án”, “Nhập tên, mô tả và xác nhận tạo”; tạo mới không yêu cầu dự án đã tồn tại. Cụm “thao tác với dự án hiện có” cũng chưa diễn đạt đủ điều kiện quyền truy cập.
- Gợi ý sửa: “Người dùng đã đăng nhập. Đối với thao tác xem, sửa hoặc xóa, dự án phải tồn tại và người dùng có quyền truy cập.”

### D06 – Thấp: yêu cầu CN04 thiếu sửa/xóa địa điểm so với đặc tả

- Vị trí: Bảng 3.1, block 450, trang 27 (PDF 37); đối chiếu §3.1.5.4, block 486, từ trang 32 (PDF 42).
- Nguyên văn CN04: “Tạo địa điểm thuộc dự án, xem thông tin và các phiên phân tích tại địa điểm.”
- Nguyên văn mô tả use case: “Cho phép người dùng xem, thêm, sửa và xóa địa điểm quan sát thuộc một dự án.”
- Vấn đề: bảng yêu cầu chức năng thiếu hai thao tác mà đặc tả và triển khai đã có; khó truy vết đầy đủ phạm vi yêu cầu/kiểm thử.
- Gợi ý sửa CN04: “Tạo, sửa, xóa địa điểm thuộc dự án; xem thông tin và các phiên phân tích tại địa điểm.”

### D07 – Thấp: hai dẫn chiếu số bảng bị lệch

- Block 622, trang 51 (PDF 61): “Chức năng và các trường tiêu biểu của từng bảng dữ liệu được nêu ở bảng 3.4:” nhưng ngay dưới là “Bảng 3.5. Các bảng dữ liệu” (block 623). Sửa 3.4 → 3.5.
- Block 626, trang 52 (PDF 62): “Kho tệp được chia thành bốn nhóm để thuận tiện quản lý, được nêu ở bảng 3.5:” nhưng ngay dưới là “Bảng 3.6. Cấu trúc kho lưu trữ dữ liệu” (block 627). Sửa 3.5 → 3.6.

### D08 – Thấp: một số câu/tiêu đề chưa hoàn chỉnh và chưa thống nhất

- §3.1.5.7, bảng block 495, ô Các yêu cầu đặc biệt: “Cách tính tỉ lệ vi phạm, phân biệt khung giờ khai báo của phiên với thống kê chi tiết dựa trên thời điểm vi phạm trong video.” Đây là cụm liệt kê, chưa thành yêu cầu. Có thể sửa: “Hệ thống phải áp dụng thống nhất công thức tính tỷ lệ và phân biệt khung giờ khai báo của phiên với thời điểm xác nhận trong video.” Dùng “tỷ lệ” nhất quán.
- Block 461: “3.1.4.2 Biểu đồ UseCase tổng quát” thiếu dấu chấm sau 2. Sửa thành “3.1.4.2. Biểu đồ use case tổng quát”; thống nhất “use case”/“UseCase” toàn chương.
- Block 491: “3.1.5.6. UseCase xem kết quả và minh chứng” không thống nhất hoa đầu tên với các mục cạnh đó. Sửa “Xem”.
- Blocks 550 và 596 thiếu dấu chấm kết thúc đoạn.
- Block 594 “3.3.3.2. Ghi nhận một lần cho mỗi mã theo dõi.” có dấu chấm cuối tiêu đề, khác phần lớn tiêu đề ngang cấp; bỏ dấu cuối cho thống nhất.

## 3. Điểm cần làm rõ, không khẳng định là lỗi đã chứng minh

### D09 – Giới hạn thống kê thời gian cần viết rõ nếu dùng code hiện tại

- Vị trí: §3.2.3, block 543, trang 44 (PDF 54).
- Nguyên văn: “Đối với thống kê thời gian chi tiết từ video, thời điểm của một trường hợp được tính bằng giờ bắt đầu phiên cộng với thời điểm xác nhận trong video. Các video trong cùng phiên sử dụng chung mốc giờ bắt đầu. Ảnh tĩnh không có thời điểm tương đối nên không tham gia cách thống kê chi tiết này.”
- Đối chiếu chọn lọc: `_calculate_hourly_violations` trong `backend/app/services/analysis_service.py` chỉ đếm timestamp nằm trong các khoảng từ giờ bắt đầu đến giờ kết thúc do người dùng nhập. Upload chỉ kiểm tra end > start, không kiểm tra thời lượng video phù hợp khoảng đó. Video dài hơn khoảng khai báo có thể có bản ghi NO_HELMET được tính vào tổng nhưng không vào bảng theo giờ.
- Gợi ý: nêu điều kiện dữ liệu hoặc bổ sung giới hạn rằng tổng theo giờ có thể thấp hơn tổng số ghi nhận khi timestamp vượt giờ kết thúc; kiểm tra ở phần thực nghiệm nếu báo cáo khẳng định hai tổng luôn khớp. Không thêm kết luận về sai số khi chưa kiểm tra dữ liệu cụ thể.

## Những nội dung đã kiểm tra và không phát hiện sai rõ ràng

- Hình 3.4 (ERD) có đủ 6 bảng; chiều quan hệ 1–N và khóa ngoại session/media phù hợp mô hình dữ liệu ở mức sơ đồ khái quát. Image5 nền trong suốt khi xem trực tiếp, không phải ảnh trắng/đen lỗi; bản QA nền trắng là `erd_white_qa.png`.
- Công thức R dùng NO_HELMET/tổng xe; các công thức vùng liên kết và khoảng cách chuẩn hóa khớp hệ số 0,2; 0,8; 0,7 và hàm `_head_vehicle_score` hiện tại. Phải kiểm tra render công thức ở QA tổng thể, vì text extraction không giữ đầy đủ cấu trúc căn/phân số.
- Trạng thái phiên thành công một phần, chỉ cộng kết quả tệp COMPLETED, đầu mối thống kê theo phiên và gói ZIP cơ bản phù hợp mã nguồn.
- Thừa nhận chưa phân biệt người lái/người ngồi sau, chưa loại trùng giữa tệp, khả năng mất track rồi đếm lại được trình bày rõ; không xem các giới hạn đã công khai này tự thân là “lỗi thuật toán”.
- Sơ đồ use case và các mockup giao diện được đọc trực tiếp; không thấy lỗi nghiệp vụ lớn khác ngoài các mục đã nêu.

Ghi chú cho người tổng hợp: đã phát hiện `/storage` đang mount công khai trong code nhưng không đưa vào danh sách lỗi chính vì nhiệm vụ là rà soát báo cáo, và dòng bảo mật của bảng 3.2 giới hạn cụ thể ở các thao tác quản lý qua API. Chỉ đề cập nếu phần khác của báo cáo khẳng định toàn bộ tệp/media đã có kiểm soát truy cập trực tiếp.
