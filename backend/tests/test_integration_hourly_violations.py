"""Integration test for hourly violations feature."""
import json
from datetime import date, time
from unittest.mock import MagicMock, patch

# Test the full flow
def test_analysis_session_with_violations():
    """Test a complete analysis session with hourly violations calculation."""
    
    # Create mock violation data
    mock_violations = [
        # Violations at different times
        {"timestamp_seconds": 600, "vehicle_id": "v1"},      # 14:10
        {"timestamp_seconds": 1800, "vehicle_id": "v2"},     # 14:30
        {"timestamp_seconds": 3600, "vehicle_id": "v3"},     # 15:00
        {"timestamp_seconds": 4200, "vehicle_id": "v4"},     # 15:10
        {"timestamp_seconds": 5400, "vehicle_id": "v5"},     # 15:30
    ]
    
    # Analysis session parameters
    analysis_date = date(2024, 1, 15)
    start_time = time(14, 0, 0)
    end_time = time(16, 0, 0)
    
    # Calculate expected buckets
    start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
    
    # Expected result
    expected_buckets = [
        {"time_slot": "14:00-15:00", "count": 2},  # violations at 14:10 and 14:30
        {"time_slot": "15:00-16:00", "count": 3},  # violations at 15:00, 15:10, 15:30
    ]
    
    expected_peak = {"time_slot": "15:00-16:00", "count": 3}
    
    # Verify buckets
    print("Analysis Session Test")
    print(f"Date: {analysis_date}")
    print(f"Time Range: {start_time} - {end_time}")
    print(f"Number of violations: {len(mock_violations)}")
    print()
    
    # Calculate buckets
    hourly_buckets = []
    end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second
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
    
    # Count violations
    for violation in mock_violations:
        violation_absolute_seconds = start_seconds + violation["timestamp_seconds"]
        
        for bucket in hourly_buckets:
            if bucket["start_seconds"] <= violation_absolute_seconds < bucket["end_seconds"]:
                bucket["count"] += 1
                print(f"Violation {violation['vehicle_id']} at {violation['timestamp_seconds']}s -> {bucket['time_slot']}")
                break
    
    print()
    
    # Create result
    hourly_violations = [
        {"time_slot": bucket["time_slot"], "count": bucket["count"]}
        for bucket in hourly_buckets
    ]
    
    peak_hour = max(hourly_violations, key=lambda x: x["count"], default=None)
    
    result = {
        "hourly_violations": hourly_violations,
        "peak_hour": peak_hour,
    }
    
    # Verify results
    print("Expected buckets:")
    for bucket in expected_buckets:
        print(f"  {bucket['time_slot']}: {bucket['count']} violations")
    
    print()
    print("Calculated buckets:")
    for bucket in hourly_violations:
        print(f"  {bucket['time_slot']}: {bucket['count']} violations")
    
    print()
    print("Peak hour:", peak_hour)
    
    # Assert
    assert len(hourly_violations) == len(expected_buckets), \
        f"Expected {len(expected_buckets)} buckets, got {len(hourly_violations)}"
    
    for i, (expected, calculated) in enumerate(zip(expected_buckets, hourly_violations)):
        assert expected["time_slot"] == calculated["time_slot"], \
            f"Bucket {i}: expected time_slot {expected['time_slot']}, got {calculated['time_slot']}"
        assert expected["count"] == calculated["count"], \
            f"Bucket {i} ({expected['time_slot']}): expected {expected['count']} violations, got {calculated['count']}"
    
    assert peak_hour["time_slot"] == expected_peak["time_slot"], \
        f"Expected peak hour {expected_peak['time_slot']}, got {peak_hour['time_slot']}"
    assert peak_hour["count"] == expected_peak["count"], \
        f"Expected peak hour count {expected_peak['count']}, got {peak_hour['count']}"
    
    # Test JSON serialization
    json_str = json.dumps(result, ensure_ascii=False)
    parsed = json.loads(json_str)
    
    assert len(parsed["hourly_violations"]) == len(expected_buckets)
    assert parsed["peak_hour"]["count"] == expected_peak["count"]
    
    print()
    print("Result as JSON:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print()
    print("TEST PASSED!")


if __name__ == "__main__":
    test_analysis_session_with_violations()
