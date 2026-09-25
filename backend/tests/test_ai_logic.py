from app.services.ai.detector import Detection
from app.services.ai.tracker import CentroidTracker
from app.services.ai.violation import DetectionKind, ViolationLogic


def logic() -> ViolationLogic:
    return ViolationLogic(
        helmet_names=["With Helmet"],
        no_helmet_names=["Without Helmet"],
        vehicle_names=["motorcycle"],
    )


def test_head_state_only_model_counts_each_detection_as_subject() -> None:
    detections = [
        Detection((10, 10, 30, 30), 0.9, 0, "With Helmet"),
        Detection((50, 10, 70, 30), 0.8, 1, "Without Helmet"),
    ]
    assessment = logic().assess_image(detections)
    assert assessment.total_vehicles == 2
    assert assessment.helmet_count == 1
    assert assessment.no_helmet_count == 1


def test_vehicle_model_associates_no_helmet_with_vehicle() -> None:
    detections = [
        Detection((50, 80, 180, 220), 0.95, 2, "motorcycle"),
        Detection((95, 50, 125, 85), 0.88, 1, "Without Helmet"),
    ]
    assessment = logic().assess_image(detections)
    assert assessment.total_vehicles == 1
    assert assessment.no_helmet_count == 1
    assert assessment.subjects[0].status == DetectionKind.NO_HELMET


def test_tracker_does_not_count_same_subject_twice_across_adjacent_frames() -> None:
    tracker = CentroidTracker(max_missing=3, max_distance_ratio=0.2)
    subject_a = logic().assess_image(
        [Detection((100, 100, 150, 160), 0.9, 1, "Without Helmet")]
    ).subjects
    subject_b = logic().assess_image(
        [Detection((105, 103, 155, 163), 0.91, 1, "Without Helmet")]
    ).subjects
    tracker.update(subject_a, (480, 640, 3))
    tracker.update(subject_b, (480, 640, 3))
    tracker.update(subject_b, (480, 640, 3))
    total, helmet, no_helmet = tracker.summary()
    assert (total, helmet, no_helmet) == (1, 0, 1)


def test_single_frame_false_positive_does_not_become_violation():
    tracker = CentroidTracker()
    events = []
    for label in ['With Helmet', 'Without Helmet', 'With Helmet']:
        subjects = logic().assess_image([Detection((100, 100, 150, 160), 0.9, 0, label)]).subjects
        events.extend(tracker.update(subjects, (480, 640, 3)))
    assert tracker.summary() == (1, 1, 0)
    assert not any(event.first_no_helmet for event in events)


def test_confirmed_violation_emits_only_once():
    tracker = CentroidTracker()
    subjects = logic().assess_image([Detection((100, 100, 150, 160), 0.9, 1, 'Without Helmet')]).subjects
    events = [tracker.update(subjects, (480, 640, 3))[0].first_no_helmet for _ in range(5)]
    assert events == [False, False, True, False, False]
    assert tracker.summary() == (1, 0, 1)


def test_missing_detection_resets_confirmation():
    tracker = CentroidTracker()
    subjects = logic().assess_image([Detection((100, 100, 150, 160), 0.9, 1, 'Without Helmet')]).subjects
    tracker.update(subjects, (480, 640, 3))
    tracker.update(subjects, (480, 640, 3))
    tracker.update([], (480, 640, 3))
    tracker.update(subjects, (480, 640, 3))
    assert tracker.summary() == (1, 0, 0)
