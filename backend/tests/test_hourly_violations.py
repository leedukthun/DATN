"""Test hourly violations calculation."""
import json
from datetime import time


def test_hourly_buckets_calculation():
    """Test that hourly buckets are created correctly."""
    # Simulate start and end time
    start_time = time(14, 0, 0)  # 14:00:00
    end_time = time(16, 0, 0)    # 16:00:00
    
    # Convert to seconds
    start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
    end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second
    
    # Check for midnight crossing
    crosses_midnight = end_seconds < start_seconds
    if crosses_midnight:
        end_seconds += 24 * 3600
    
    # Create buckets
    buckets = []
    current_seconds = start_seconds
    while current_seconds < end_seconds:
        bucket_start = current_seconds
        bucket_end = min(current_seconds + 3600, end_seconds)
        
        start_hour = (bucket_start % (24 * 3600)) // 3600
        start_min = (bucket_start % 3600) // 60
        end_hour = (bucket_end % (24 * 3600)) // 3600
        end_min = (bucket_end % 3600) // 60
        
        time_slot = f"{start_hour:02d}:{start_min:02d}-{end_hour:02d}:{end_min:02d}"
        buckets.append({
            "time_slot": time_slot,
            "start_seconds": bucket_start,
            "end_seconds": bucket_end,
        })
        
        current_seconds = bucket_end
    
    print("Created buckets:")
    for bucket in buckets:
        print(f"  {bucket['time_slot']}: {bucket['start_seconds']}-{bucket['end_seconds']}")
    
    # Check results
    assert len(buckets) == 2, f"Expected 2 buckets, got {len(buckets)}"
    assert buckets[0]["time_slot"] == "14:00-15:00"
    assert buckets[1]["time_slot"] == "15:00-16:00"


def test_violation_classification():
    """Test that violations are classified into correct buckets."""
    start_time = time(14, 0, 0)
    end_time = time(16, 0, 0)
    
    start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
    end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second
    
    # Create buckets
    hourly_buckets = []
    current_seconds = start_seconds
    while current_seconds < end_seconds:
        bucket_start = current_seconds
        bucket_end = min(current_seconds + 3600, end_seconds)
        
        start_hour = (bucket_start % (24 * 3600)) // 3600
        start_min = (bucket_start % 3600) // 60
        end_hour = (bucket_end % (24 * 3600)) // 3600
        end_min = (bucket_end % 3600) // 60
        
        time_slot = f"{start_hour:02d}:{start_min:02d}-{end_hour:02d}:{end_min:02d}"
        hourly_buckets.append({
            "time_slot": time_slot,
            "start_seconds": bucket_start,
            "end_seconds": bucket_end,
            "count": 0
        })
        
        current_seconds = bucket_end
    
    # Simulate violations
    violations_timestamps = [600, 1800, 3600, 4200, 5400]  # in seconds
    # 600s = 10min => 14:10 (first bucket)
    # 1800s = 30min => 14:30 (first bucket)
    # 3600s = 60min => 15:00 (second bucket)
    # 4200s = 70min => 15:10 (second bucket)
    # 5400s = 90min => 15:30 (second bucket)
    
    for timestamp in violations_timestamps:
        violation_absolute_seconds = start_seconds + timestamp
        
        for bucket in hourly_buckets:
            if bucket["start_seconds"] <= violation_absolute_seconds < bucket["end_seconds"]:
                bucket["count"] += 1
                break
    
    print("Violation counts per bucket:")
    for bucket in hourly_buckets:
        print(f"  {bucket['time_slot']}: {bucket['count']} violations")
    
    # Check results
    assert hourly_buckets[0]["count"] == 2, f"Expected 2 violations in first bucket, got {hourly_buckets[0]['count']}"
    assert hourly_buckets[1]["count"] == 3, f"Expected 3 violations in second bucket, got {hourly_buckets[1]['count']}"


def test_peak_hour():
    """Test that peak hour is correctly identified."""
    hourly_violations = [
        {"time_slot": "14:00-15:00", "count": 2},
        {"time_slot": "15:00-16:00", "count": 5},
    ]
    
    peak_hour = max(hourly_violations, key=lambda x: x["count"], default=None)
    
    print(f"Peak hour: {peak_hour}")
    
    assert peak_hour["time_slot"] == "15:00-16:00"
    assert peak_hour["count"] == 5


def test_result_json():
    """Test that result is properly formatted as JSON."""
    hourly_violations = [
        {"time_slot": "14:00-15:00", "count": 2},
        {"time_slot": "15:00-16:00", "count": 5},
    ]
    peak_hour = max(hourly_violations, key=lambda x: x["count"], default=None)
    
    result = {
        "hourly_violations": hourly_violations,
        "peak_hour": peak_hour,
    }
    
    json_str = json.dumps(result, ensure_ascii=False)
    print(f"Result JSON:\n{json_str}")
    
    # Verify it can be parsed back
    parsed = json.loads(json_str)
    assert len(parsed["hourly_violations"]) == 2
    assert parsed["peak_hour"]["count"] == 5


if __name__ == "__main__":
    print("Running hourly violations tests...\n")
    
    print("Test 1: Hourly buckets calculation")
    test_hourly_buckets_calculation()
    print("PASSED\n")
    
    print("Test 2: Violation classification")
    test_violation_classification()
    print("PASSED\n")
    
    print("Test 3: Peak hour identification")
    test_peak_hour()
    print("PASSED\n")
    
    print("Test 4: Result JSON formatting")
    test_result_json()
    print("PASSED\n")
    
    print("All tests passed!")
