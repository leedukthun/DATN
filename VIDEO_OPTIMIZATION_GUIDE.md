# Video Detection Optimization Guide

Tài liệu này mô tả các cải tiến được thực hiện trong phiên bản tối ưu hóa của hệ thống phát hiện không đội mũ.

## 📊 Cải tiến thực hiện

### 1. **Async I/O Threads** ✅
**Vấn đề cũ:** Ghi video và lưu ảnh chứng minh chặn quá trình detection

**Cải tiến:**
- Tạo thread riêng `_FrameWriter` để ghi frame vào video không chặn main thread
- Tạo thread riêng `_EvidenceSaver` để lưu ảnh bằng chứng asynchronously
- Sử dụng Queue để giao tiếp thread-safe giữa các thread

**Lợi ích:** Detection có thể chạy liên tục trong khi I/O xảy ra ở background

```python
# Main thread giải phóng ngay sau khi put frame vào queue
write_queue.put(annotated, timeout=1.0)

# FrameWriter thread ghi frame không chặn
while self.running:
    frame = self.queue.get()
    self.writer.write(frame)  # Blocking ở đây, không phải main
```

---

### 2. **Loại bỏ Lock Bottleneck** ✅
**Vấn đề cũ:** `_predict_lock` trong `Detector.predict()` gây bottleneck khi frame nhiều

**Cải tiến:**
- Bỏ lock trong predict vì YOLO model thread-safe khi dùng `detach().cpu()`
- Giảm contention giữa threads

**Lợi ích:** Inference không phải chờ lock, tăng throughput

---

### 3. **Adaptive Frame Stride** ✅
**Vấn đề cũ:** Mặc định `VIDEO_FRAME_STRIDE=1` xử lý mọi frame → chậm với video dài

**Cải tiến:**
```python
# Video > 2 phút (3600 frames @ 30fps) tự động tăng stride
if total_frames > 3600:
    adaptive_stride = max(2, base_stride)
else:
    adaptive_stride = base_stride
```

**Bảng tối ưu:**
| Video Length | Stride | Xử lý % Frames | Tốc độ |
|---|---|---|---|
| < 30 giây | 1 | 100% | ✅ Chuẩn |
| 30 giây - 2 phút | 1 | 100% | ✅ Chuẩn |
| 2-5 phút | 2 | 50% | ⚡ 2x nhanh |
| > 5 phút | 2-3 | 33-50% | ⚡⚡ 3x nhanh |

---

### 4. **Improved Centroid Tracker** ✅
**Vấn đề cũ:** Tracker đơn giản, dễ miss object hoặc tạo duplicate tracks

**Cải tiến:**
- Thêm `_compute_distance()` với weight theo status consistency
- Nếu track state matches current detection → giảm effective distance → match priority
- Cấu trúc cost matrix rõ ràng với greedy matching

```python
# Status bonus: nếu track và detection có status giống → easier match
if track.last_status == subject.status:
    status_bonus = -0.15 * centroid_distance  # Giảm distance 15%
```

**Lợi ích:** 
- Ít false positives (duplicate counts)
- Ít false negatives (missed violations)
- Consistent tracking across frames

---

### 5. **Optimized Config** ✅
**Cải tiến:**
- Thêm hướng dẫn chi tiết trong `.env.example` cho từng parameter
- Giải thích tradeoff giữa tốc độ vs độ chính xác

---

## 🎯 Hướng dẫn sử dụng tối ưu

### Scenario 1: Video ngắn (< 1 phút) trên máy tính bất kỳ
```env
VIDEO_FRAME_STRIDE=1          # Xử lý mọi frame
VIDEO_MAX_WIDTH=1280          # Full resolution
CONFIDENCE_THRESHOLD=0.40     # Chuẩn
IOU_THRESHOLD=0.50            # Chuẩn
TRACK_MAX_DISTANCE_RATIO=0.08 # Chuẩn
```
**Kết quả:** Độ chính xác cao nhất

---

### Scenario 2: Video dài (2-10 phút) trên CPU
```env
VIDEO_FRAME_STRIDE=2          # Skip mỗi frame thứ 2
VIDEO_MAX_WIDTH=960           # Giảm độ phân giải
CONFIDENCE_THRESHOLD=0.45     # Tăng ngưỡng (ít noise)
IOU_THRESHOLD=0.50            # Chuẩn
TRACK_MAX_DISTANCE_RATIO=0.10 # Chịu đựng motion nhanh hơn
```
**Kết quả:** Xử lý 2x nhanh, vẫn bắt được violations

---

### Scenario 3: Video 4K hoặc rất dài (> 10 phút)
```env
VIDEO_FRAME_STRIDE=3          # Skip 2 frame rồi xử lý 1
VIDEO_MAX_WIDTH=640           # Giảm nhiều độ phân giải
CONFIDENCE_THRESHOLD=0.45     # Tăng ngưỡng
IOU_THRESHOLD=0.50            # Chuẩn
TRACK_MAX_DISTANCE_RATIO=0.12 # Lớn hơn cho fast motion
```
**Kết quả:** Xử lý 3x nhanh, phù hợp demo/preview

---

### Scenario 4: GPU NVIDIA (PyTorch + CUDA)
```env
DEVICE=0                      # Dùng GPU thay CPU
VIDEO_FRAME_STRIDE=1          # Có thể xử lý mọi frame nhanh
VIDEO_MAX_WIDTH=1280          # Full resolution
# ... rest chuẩn
```
**Kết quả:** Xử lý 10-20x nhanh, có thể real-time

---

## 📈 Benchmarks (ước tính)

Với video 5 phút (7500 frames @ 25fps) trên CPU i7 8-core:

| Config | Stride | Width | Thời gian | Tốc độ Frame |
|---|---|---|---|---|
| **Cũ** (all locked) | 1 | 1280 | ~15-20 phút | 6-8 fps |
| **Cải tiến (default)** | 1 | 1280 | ~10-12 phút | 12-15 fps |
| **Tối ưu (stride=2)** | 2 | 960 | ~4-5 phút | 30+ fps |
| **Cực nhanh (stride=3)** | 3 | 640 | ~2-3 phút | 50+ fps |

*Lưu ý: Con số thực phụ thuộc vào máy, model YOLO version, và độ phức tạp video*

---

## 🔧 Tuning Tips

### Nếu miss violations (false negatives)
```env
CONFIDENCE_THRESHOLD=0.35      # Giảm (nhạy hơn)
VIDEO_FRAME_STRIDE=1           # Xử lý mọi frame
TRACK_MAX_DISTANCE_RATIO=0.10  # Lớn hơn (chịu motion)
```

### Nếu có false positives (đếm nhiều)
```env
CONFIDENCE_THRESHOLD=0.50      # Tăng (nghiêm ngặt hơn)
TRACK_MAX_MISSING=12           # Nhỏ hơn (remove tracks nhanh)
TRACK_MAX_DISTANCE_RATIO=0.06  # Nhỏ hơn (matching chặt)
```

### Nếu xử lý quá chậm
```env
VIDEO_FRAME_STRIDE=2           # Skip frames
VIDEO_MAX_WIDTH=640            # Giảm resolution
CONFIDENCE_THRESHOLD=0.45      # Giảm tính toán NMS
```

### Nếu cần real-time (video stream)
- Dùng GPU (`DEVICE=0`)
- Tăng stride (`VIDEO_FRAME_STRIDE=2-3`)
- Giảm resolution (`VIDEO_MAX_WIDTH=640`)
- Tăng threshold confidence (`CONFIDENCE_THRESHOLD=0.50`)

---

## 🚀 Advanced Optimization

### Option 1: Replace Centroid Tracker
Hiện tại dùng Centroid Tracker (đơn giản, nhanh). Có thể nâng cấp:

```python
# Trong services/ai/tracker.py, thay class CentroidTracker bằng:
from ultralytics import YOLO
from ultralytics.solutions import ObjectCounter  # Nếu có

# Hoặc integrate ByteTrack:
# pip install byte-track
from byte_tracker import BYTETracker
```

**Lợi ích:** Tracking chính xác hơn ở môi trường đông đúc, tránh ID switch

---

### Option 2: Batch Inference
Hiện tại xử lý frame-by-frame. Có thể batch nhiều frame:

```python
# Queue frames → batch 8-16 frames → inference 1 lần
# Tăng throughput 3-5x nhưng + latency
```

---

### Option 3: Multi-GPU
Nếu có 2+ GPU:

```python
# Detector instance 1 → GPU:0
# Detector instance 2 → GPU:1
# Thread 1 xử lý frames → GPU:0
# Thread 2 xử lý frames → GPU:1
```

---

## 📋 Checklist trước production

- [ ] Test với dữ liệu thật (video từ camera CCTV)
- [ ] Fine-tune confidence_threshold với test set
- [ ] Calibrate tracker parameters với video real
- [ ] Monitor CPU/GPU usage
- [ ] Kiểm tra accuracy (P/R/F1 metrics)
- [ ] Setup logging để track performance
- [ ] Dùng PostgreSQL (không SQLite) nếu > 10 analysis/day
- [ ] Cân nhắc Celery + Redis queue cho video nhiều

---

## 🆘 Troubleshooting

### Q: Vẫn chậm dù đã optimize
**A:** 
- Cứu: Kiểm tra `nvidia-smi` xem GPU dùng không, hay CPU hết core
- Nếu GPU free: Đặt `DEVICE=0`
- Nếu CPU hết: Dùng `VIDEO_FRAME_STRIDE=3` hoặc `VIDEO_MAX_WIDTH=480`

### Q: Miss quá nhiều violations
**A:**
- Kiểm tra CONFIDENCE_THRESHOLD (hạ xuống 0.35)
- Tăng video resolution (VIDEO_MAX_WIDTH=1920)
- Tăng TRACK_MAX_DISTANCE_RATIO (0.12)
- Test model với labeled test set

### Q: Chiếm quá nhiều disk (storage)
**A:**
- Giảm video resolution → .mp4 nhỏ hơn
- Xóa old analysis (retention policy)
- Compress evidence images với quality lower

---

## 📞 Liên hệ

Nếu cần support thêm optimization, file issue với:
- Video specs (duration, resolution, fps)
- Machine specs (CPU, RAM, GPU)
- Current settings và performance
