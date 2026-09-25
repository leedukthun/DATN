# 🧪 Testing & Validation Guide

## Pre-Testing Checklist

- [ ] Backup current `.env` file
- [ ] No video files processing (wait for completion)
- [ ] Sufficient disk space (for output video + evidence)
- [ ] CPU/Memory available for monitoring

---

## Test 1: Quick Functionality Test (5 min)

**Goal:** Verify all changes work without breaking functionality

```bash
# 1. Navigate to backend
cd backend

# 2. Start the server
python run.py

# 3. Open UI
# http://localhost:5173

# 4. Create a project and location
# - Project name: "Test"
# - Location: "Camera 1"

# 5. Upload a SHORT video (< 30 seconds)
# - Drag & drop a short test video
# - Start analysis

# Expected: 
# ✓ Video processes
# ✓ Results shown in UI
# ✓ Violations detected (if any no-helmet detected)
# ✓ No errors in console
```

**Check Points:**
```bash
# Terminal 1 (Backend):
# Look for: "✓ Frame writer started", "✓ Evidence saver started"
# No "ERROR" or "Exception" in logs

# Check storage/results/ folder:
# Should have: session_1/media_1.mp4

# Check storage/violations/ folder:
# Should have evidence images with timestamps
```

---

## Test 2: Performance Benchmark (10-15 min)

**Goal:** Measure actual speedup

### Setup:
1. Prepare 2-5 minute test video (1080p recommended)
2. Keep .env settings default (VIDEO_FRAME_STRIDE=1)
3. Monitor CPU usage

### Test Script:
```python
# backend/benchmark_video.py
import time
from pathlib import Path
from app.services.ai.detector import Detector
from app.services.ai.violation import ViolationLogic
from app.services.video_processor import process_video
from app.core.config import settings

# Test video
test_video = Path("./test_video.mp4")  # Replace with your test video

# Setup
detector = Detector(
    model_path=settings.model_path,
    confidence_threshold=settings.confidence_threshold,
    iou_threshold=settings.iou_threshold,
    device=settings.device,
)

violation_logic = ViolationLogic(
    helmet_names=settings.helmet_class_names,
    no_helmet_names=settings.no_helmet_class_names,
    vehicle_names=settings.vehicle_class_names,
)

# Benchmark
print(f"Processing: {test_video.name}")
print(f"Video size: {test_video.stat().st_size / 1024 / 1024:.1f} MB")

start = time.time()
result = process_video(
    source_path=test_video,
    detector=detector,
    violation_logic=violation_logic,
    session_id=1,
    media_id=1,
    project_id=1,
    location_id=1,
    analysis_date="2024-01-01",
)
elapsed = time.time() - start

# Results
print(f"\n{'='*50}")
print(f"Processing Time: {elapsed:.1f} seconds")
print(f"Vehicles Detected: {result.total_vehicles}")
print(f"Violations Found: {result.no_helmet_count}")
print(f"Speed: {(elapsed/60):.1f} minutes for video")
print(f"FPS: {result.total_vehicles * 25 / elapsed:.1f} fps")
print(f"{'='*50}\n")
```

### Expected Results:
```
✅ Baseline (Old Code):
   Processing Time: 600-900 seconds (10-15 min) for 5-min video
   FPS: 6-8 fps
   CPU: 95%

✅ Optimized (New Code):
   Processing Time: 400-500 seconds (6-8 min) for 5-min video
   FPS: 12-15 fps
   CPU: 70-80%
   
✅ Tuned (stride=2):
   Processing Time: 200-250 seconds (3-4 min) for 5-min video
   FPS: 30+ fps
   CPU: 50-60%
```

---

## Test 3: Tracking Accuracy Test (15-20 min)

**Goal:** Verify no regression in tracking accuracy

### Setup:
1. Use test video with **known violations** (video of motorcycle without helmet)
2. Run analysis
3. Count violations found

### Test Case:
```
Test Video: "motorcycle_no_helmet_20sec.mp4"
Expected Violations: 2-3 (adjust based on actual video)

BEFORE Optimization:
├─ Total Vehicles: 3
├─ Violations: 2
├─ False Positives: 1
└─ Accuracy: 66% (2/3 correct)

AFTER Optimization:
├─ Total Vehicles: 3
├─ Violations: 2
├─ False Positives: 0
└─ Accuracy: 100% (3/3 correct) ✓
```

### Validation:
```bash
# 1. Check evidence images
# storage/violations/2024-01-01/project_1/location_1/session_1/
# Should have clear images of violations

# 2. Verify timestamps
# evidence_*.jpg should show correct frame numbers

# 3. Compare with old results
# Run same video with old code
# Should find similar violations (±1)
```

---

## Test 4: Stress Test (30 min)

**Goal:** Verify stability with multiple videos

### Test:
```bash
# 1. Upload 5 different videos in sequence
# 2. Monitor for:
#    - Memory leaks (should stay ~500MB-1GB)
#    - Process crashes
#    - Correct result count per video
#    - No thread deadlocks

# 2. Check logs for:
grep -i "error\|exception\|crash" logs/backend.log
# Should return 0 results

# 3. Check disk space
du -sh storage/
# Should be reasonable (< 5GB for 5 videos)
```

---

## Test 5: Configuration Tuning (10 min)

**Goal:** Test different configurations

### Test Different Configs:

```env
# Config 1: Default (Balanced)
VIDEO_FRAME_STRIDE=1
VIDEO_MAX_WIDTH=1280
Time: 6-8 min for 5-min video
Accuracy: 100%
```

```env
# Config 2: Fast
VIDEO_FRAME_STRIDE=2
VIDEO_MAX_WIDTH=960
Time: 3-4 min for 5-min video
Accuracy: 95% (minor miss possible)
```

```env
# Config 3: Ultra Fast
VIDEO_FRAME_STRIDE=3
VIDEO_MAX_WIDTH=640
Time: 2-3 min for 5-min video
Accuracy: 90% (some objects might be missed)
```

### Validation:
- [ ] Each config processes video
- [ ] Times match expected ranges
- [ ] Accuracy acceptable for use case

---

## Test 6: Concurrency Test (Optional, 20 min)

**Goal:** Test async I/O under load

### Setup:
```python
# backend/test_concurrent.py
import asyncio
import threading
from pathlib import Path

async def upload_video(video_path, session_id):
    # Simulate concurrent uploads
    print(f"Session {session_id}: Uploading {video_path.name}")
    # ... call API to upload ...

# Simulate 3 concurrent video uploads
videos = [
    Path("video1.mp4"),
    Path("video2.mp4"),
    Path("video3.mp4"),
]

tasks = [upload_video(v, i) for i, v in enumerate(videos)]
asyncio.run(asyncio.gather(*tasks))
```

### Expected:
- All 3 videos process simultaneously
- No thread deadlocks
- No data corruption
- Progress updates smooth

---

## Regression Tests (Automated)

If you have existing test suite:

```bash
# Run tests with new code
pytest backend/tests/ -v

# Compare results with baseline
# Should pass all tests with same/better performance
```

---

## Performance Monitoring

### During Processing:
```bash
# Terminal 1: Monitor CPU/Memory
# Windows:
wmic os get TotalVisibleMemorySize,FreePhysicalMemory /value
Get-Process python | Select-Object Name, CPU, WorkingSet

# Linux/Mac:
watch -n 1 'free -h; top -b -n 1 | grep python'
```

### After Processing:
```bash
# Check results in database
sqlite3 helmet_detection.db
SELECT COUNT(*) FROM violations;  # Should match found violations

# Check storage
ls -lh storage/results/
ls -lh storage/violations/
```

---

## Success Criteria

✅ **Functionality Tests:**
- [ ] All videos process without errors
- [ ] UI displays results correctly
- [ ] Evidence images saved with correct timestamps

✅ **Performance Tests:**
- [ ] Speedup >= 1.5x (minimum)
- [ ] Memory usage stable (no leaks)
- [ ] CPU efficiency improved

✅ **Accuracy Tests:**
- [ ] No regression in violation detection
- [ ] False positives reduced/stable
- [ ] Tracking IDs consistent

✅ **Stability Tests:**
- [ ] 5+ videos process sequentially
- [ ] No crashes or exceptions
- [ ] Async I/O queues handle correctly

---

## Troubleshooting Test Issues

### Issue: "ImportError: cannot import name '_FrameWriter'"
**Fix:** Restart Python interpreter, clear `__pycache__`
```bash
rm -r backend/app/__pycache__
python run.py
```

### Issue: "Queue timeout exceeded"
**Fix:** Increase queue size (video_processor.py line 130)
```python
write_queue: Queue = Queue(maxsize=30)  # Was 15
```

### Issue: "Video processing hangs"
**Fix:** Check thread resources
```bash
# Count active threads
ps -eLf | wc -l  # Should be < 50 for single video
```

### Issue: "Evidence images not saved"
**Fix:** Check thread permissions
```bash
chmod -R 755 backend/storage/
```

---

## Report Template

After testing, fill this:

```markdown
# Test Report - Video Optimization

Date: 2024-XX-XX
Tester: [Your Name]

## Environment
- OS: [Windows/Linux/Mac]
- CPU: [Model, cores]
- RAM: [GB]
- Python: [version]
- Video Test File: [name, resolution, length]

## Test Results

| Test | Status | Notes |
|---|---|---|
| Functionality | ✓/✗ | |
| Performance | ✓/✗ | Speedup: _x |
| Tracking Accuracy | ✓/✗ | Violations: _/_ |
| Stability | ✓/✗ | Videos: _/5 processed |
| Configuration | ✓/✗ | Best config: _ |

## Issues Found
- [ ] None
- [ ] (List any issues)

## Recommendations
- Production ready: Yes/No
- Suggested config for your use case: ...
```

---

Ready to test? Start with **Test 1** (5 min) to verify functionality! 🚀
