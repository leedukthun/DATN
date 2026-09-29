from __future__ import annotations

import math
import statistics
from collections import deque
from dataclasses import dataclass, field

from app.services.ai.violation import DetectionKind, SubjectDetection


@dataclass(slots=True)
class Track:
    track_id: int
    bbox: tuple[int, int, int, int]
    centroid: tuple[float, float]
    missing: int = 0
    age: int = 1
    last_status: DetectionKind = DetectionKind.UNKNOWN
    last_confidence: float = 0.0
    ever_helmet: bool = False
    ever_no_helmet: bool = False
    recent_statuses: deque[DetectionKind] = field(default_factory=deque)
    path: deque[tuple[float, float, float, float]] = field(default_factory=lambda: deque(maxlen=240))
    speeds: deque[float] = field(default_factory=lambda: deque(maxlen=60))
    vehicle_hits: int = 0
    # (time, head offset from the vehicle's top-centre in head heights) while on a vehicle.
    vehicle_offsets: deque[tuple[float, float, float]] = field(default_factory=lambda: deque(maxlen=120))
    duplicate: bool = False
    last_subject: SubjectDetection | None = None


@dataclass(slots=True)
class TrackedSubject:
    track_id: int
    subject: SubjectDetection
    first_no_helmet: bool


class CentroidTracker:
    """Lightweight tracker used by the MVP to avoid counting every frame as a new object."""

    def __init__(
        self,
        max_missing: int = 18,
        max_distance_ratio: float = 0.08,
        confirmation_frames: int = 3,
        window_frames: int = 8,
        min_hits: int = 3,
        min_no_helmet_ratio: float = 0.6,
        min_speed: float = 0.0,
        use_vehicle_evidence: bool = False,
        speed_window_seconds: float = 1.0,
    ) -> None:
        self.max_missing = max_missing
        self.max_distance_ratio = max_distance_ratio
        self.confirmation_frames = max(1, confirmation_frames)
        # Vote over the last N observations: small heads flicker between labels and drop
        # out for a frame, so requiring an unbroken streak misses most real violations.
        self.window_frames = max(self.confirmation_frames, window_frames)
        self.min_hits = max(1, min_hits)
        # Share of "no helmet" votes required; a helmet seen from above can flicker to
        # "no helmet" for a few frames when the rider looks down.
        self.min_no_helmet_ratio = min_no_helmet_ratio
        # A track counts as a rider once it has been seen on a vehicle, or its median speed
        # (box heights per second) reaches min_speed. With a fixed camera this rejects traffic
        # signs and pedestrians. With both disabled every track counts.
        self.min_speed = max(0.0, min_speed)
        self.use_vehicle_evidence = use_vehicle_evidence
        self.same_spot_seconds = 10.0
        self.speed_window_seconds = speed_window_seconds
        self._clock = 0.0
        self._next_id = 1
        self.active: dict[int, Track] = {}
        self.history: dict[int, Track] = {}

    @staticmethod
    def _centroid(bbox: tuple[int, int, int, int]) -> tuple[float, float]:
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    MIN_SPEED_SAMPLES = 8

    def should_display(self, tracked: TrackedSubject) -> bool:
        """Draw riders only: pedestrians' heads are tracked but never shown on the output video."""
        track = self.history.get(tracked.track_id)
        if track is None or not self.use_vehicle_evidence and self.min_speed <= 0:
            return True
        return self.is_rider(track)

    def is_rider(self, track: Track) -> bool:
        if self.min_speed <= 0 and not self.use_vehicle_evidence:
            return True
        # Median rather than max: a single ID switch between nearby heads looks like a jump.
        speed = statistics.median(track.speeds) if len(track.speeds) >= self.MIN_SPEED_SAMPLES else None
        if not self.use_vehicle_evidence:
            # Head-only fallback. Weak: a brisk pedestrian moves as fast (in head heights)
            # as a motorbike slowing at an intersection.
            return speed is not None and speed >= self.min_speed
        # Seen on a motorbike repeatedly (one stray box is not enough), and not standing
        # still once speed is measurable, which rejects pedestrians beside parked bikes.
        on_vehicle = track.vehicle_hits >= 3 and track.vehicle_hits >= 0.25 * track.age
        # Trusted before speed is measurable: requiring it drops most real riders, who are
        # often only tracked for a fraction of a second.
        moving = self.min_speed <= 0 or speed is None or speed >= self.min_speed * 0.6
        return on_vehicle and moving

    def _update_speed(self, track: Track) -> None:
        x1, y1, x2, y2 = track.bbox
        track.path.append((self._clock, track.centroid[0], track.centroid[1], float(max(1, y2 - y1))))
        now = self._clock
        window = [item for item in track.path if now - item[0] <= self.speed_window_seconds]
        elapsed = now - window[0][0]
        if elapsed < self.speed_window_seconds * 0.4:
            return
        distance = math.hypot(window[-1][1] - window[0][1], window[-1][2] - window[0][2])
        box_height = sum(item[3] for item in window) / len(window)
        track.speeds.append(distance / elapsed / box_height)

    MAX_VEHICLE_DRIFT = 4.0  # head heights per second
    DRIFT_BASELINE_SECONDS = 0.25
    MIN_DRIFT_BASELINE_SECONDS = 0.1

    def _rides_vehicle(self, track: Track, subject: SubjectDetection) -> bool:
        """True when the head keeps a steady position on its vehicle over a short baseline.

        A rider's head moves with the motorbike; a pedestrian beside one (or a bike parked
        next to a walking pedestrian) drifts relative to it, so that pairing is not counted.
        """
        if subject.vehicle_bbox is None:
            return False
        vx1, vy1, vx2, _ = subject.vehicle_bbox
        head_height = max(1, subject.bbox[3] - subject.bbox[1])
        cx, cy = subject.center
        offset = ((cx - (vx1 + vx2) / 2) / head_height, (cy - vy1) / head_height)
        now = self._clock
        track.vehicle_offsets.append((now, *offset))
        recent = [item for item in track.vehicle_offsets if now - item[0] <= 4 * self.DRIFT_BASELINE_SECONDS]
        then, ox, oy = recent[0]
        if now - then < self.MIN_DRIFT_BASELINE_SECONDS:
            return True  # too early to judge; short rider tracks would otherwise never qualify
        drift = math.hypot(offset[0] - ox, offset[1] - oy) / (now - then)
        return drift <= self.MAX_VEHICLE_DRIFT

    def _observe(self, track: Track, subject: SubjectDetection) -> None:
        status = subject.status
        track.recent_statuses.append(status)
        track.vehicle_hits += int(self._rides_vehicle(track, subject))
        self._update_speed(track)
        track.ever_helmet = track.ever_helmet or status == DetectionKind.HELMET
        # Only confirm on a no-helmet observation, so the evidence frame shows the violation.
        if track.ever_no_helmet or status != DetectionKind.NO_HELMET:
            return
        no_helmet = sum(item == DetectionKind.NO_HELMET for item in track.recent_statuses)
        helmet = sum(item == DetectionKind.HELMET for item in track.recent_statuses)
        track.ever_no_helmet = (
            no_helmet >= self.confirmation_frames
            and no_helmet >= self.min_no_helmet_ratio * (no_helmet + helmet)
            and self.is_rider(track)
        )
        if track.ever_no_helmet:
            track.duplicate = self._near_recent_violation(track)

    def _near_recent_violation(self, track: Track) -> bool:
        """Detect a track that is really an already-reported rider after an ID switch."""
        box_height = max(1, track.bbox[3] - track.bbox[1])
        for other in self.history.values():
            if other is track or not other.ever_no_helmet or other.duplicate or not other.path:
                continue
            seen_at, ox, oy, _ = other.path[-1]
            elapsed = self._clock - seen_at
            distance = math.hypot(ox - track.centroid[0], oy - track.centroid[1])
            # A nearby track just lost, or a rider waiting at a light re-acquired on the same spot.
            if (elapsed <= self.speed_window_seconds and distance <= 3 * box_height) or (
                elapsed <= self.same_spot_seconds and distance <= box_height
            ):
                return True
        return False

    def _new_track(self, subject: SubjectDetection) -> Track:
        status = subject.status
        track = Track(
            track_id=self._next_id,
            bbox=subject.bbox,
            centroid=self._centroid(subject.bbox),
            last_status=status,
            last_confidence=subject.confidence,
            recent_statuses=deque(maxlen=self.window_frames),
            last_subject=subject,
        )
        self._observe(track, subject)
        self._next_id += 1
        self.active[track.track_id] = track
        self.history[track.track_id] = track
        return track

    def update(
        self,
        subjects: list[SubjectDetection],
        frame_shape: tuple[int, int, int] | tuple[int, int],
        timestamp: float | None = None,
    ) -> list[TrackedSubject]:
        # Without real timestamps assume 25 fps so the speed filter still has a time base.
        self._clock = timestamp if timestamp is not None else self._clock + 1 / 25
        frame_height, frame_width = frame_shape[:2]
        max_distance = max(frame_height, frame_width) * self.max_distance_ratio
        previous_no_helmet = {track_id: track.ever_no_helmet for track_id, track in self.active.items()}

        if not self.active:
            return [
                TrackedSubject(
                    track_id=(track := self._new_track(subject)).track_id,
                    subject=subject,
                    first_no_helmet=track.ever_no_helmet,
                )
                for subject in subjects
            ]

        track_ids = list(self.active)
        subject_centers = [self._centroid(item.bbox) for item in subjects]
        
        # Build cost matrix (distance-based matching)
        pairs: list[tuple[float, int, int]] = []
        for track_id in track_ids:
            track = self.active[track_id]
            tx, ty = track.centroid
            for subject_index, (sx, sy) in enumerate(subject_centers):
                distance = self._compute_distance(
                    (tx, ty), (sx, sy), subjects[subject_index], track
                )
                if distance <= max_distance:
                    pairs.append((distance, track_id, subject_index))
        
        pairs.sort(key=lambda item: item[0])

        matched_tracks: set[int] = set()
        matched_subjects: set[int] = set()
        assignment: dict[int, int] = {}
        
        # Greedy matching: assign closest pairs first
        for _distance, track_id, subject_index in pairs:
            if track_id in matched_tracks or subject_index in matched_subjects:
                continue
            matched_tracks.add(track_id)
            matched_subjects.add(subject_index)
            assignment[subject_index] = track_id

        # Handle unmatched tracks
        for track_id in list(self.active):
            if track_id not in matched_tracks:
                self.active[track_id].missing += 1
                if self.active[track_id].missing > self.max_missing:
                    del self.active[track_id]

        # Generate output
        tracked: list[TrackedSubject] = []
        for subject_index, subject in enumerate(subjects):
            track_id = assignment.get(subject_index)
            if track_id is None:
                track = self._new_track(subject)
                first_no_helmet = track.ever_no_helmet and not track.duplicate
            else:
                track = self.active[track_id]
                was_no_helmet = previous_no_helmet.get(track_id, track.ever_no_helmet)
                track.bbox = subject.bbox
                track.centroid = subject_centers[subject_index]
                track.missing = 0
                track.age += 1
                track.last_status = subject.status
                track.last_confidence = subject.confidence
                track.last_subject = subject
                self._observe(track, subject)
                first_no_helmet = track.ever_no_helmet and not was_no_helmet and not track.duplicate
            tracked.append(
                TrackedSubject(
                    track_id=track.track_id,
                    subject=subject,
                    first_no_helmet=first_no_helmet,
                )
            )
        return tracked

    @staticmethod
    def _compute_distance(
        track_pos: tuple[float, float],
        subject_pos: tuple[float, float],
        subject: SubjectDetection,
        track: Track,
    ) -> float:
        """Compute weighted distance considering centroid + status confidence."""
        tx, ty = track_pos
        sx, sy = subject_pos
        centroid_distance = math.hypot(tx - sx, ty - sy)
        
        # Boost confidence in matches based on status consistency
        status_bonus = 0.0
        if track.last_status == subject.status and track.last_status != DetectionKind.UNKNOWN:
            status_bonus = -0.15 * centroid_distance  # Reduce effective distance by 15%
        
        return centroid_distance + status_bonus

    def summary(self) -> tuple[int, int, int]:
        # Tracks seen for only a frame or two are almost always detector noise.
        tracks = [
            track
            for track in self.history.values()
            if not track.duplicate
            and ((track.age >= self.min_hits and self.is_rider(track)) or track.ever_no_helmet)
        ]
        total = len(tracks)
        no_helmet = sum(track.ever_no_helmet for track in tracks)
        helmet = sum(track.ever_helmet and not track.ever_no_helmet for track in tracks)
        return total, helmet, no_helmet
