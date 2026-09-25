# Thông tin checkpoint `best.pt`

Metadata trong checkpoint do người dùng cung cấp cho thấy model dùng hai class:

```text
0: With Helmet
1: Without Helmet
```

Vì checkpoint này không có class `motorcycle`, phiên bản hiện tại coi mỗi bounding box trạng thái đội mũ/không đội mũ là một người điều khiển được quan sát. Module `violation.py` vẫn hỗ trợ model khác có thêm class xe máy: khi đó nó sẽ liên kết vùng đầu với vùng xe trước khi kết luận vi phạm.

Thông tin trên chỉ mô tả class của checkpoint, không phải đánh giá độ chính xác. Confidence và IoU cần được hiệu chỉnh bằng dữ liệu kiểm thử thực tế.
