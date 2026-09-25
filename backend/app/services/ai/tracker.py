from __future__ import annotations

import math
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
    no_helmet_streak: int = 0
    last_subject: SubjectDetection | None = None


@dataclass(slots=True)
class TrackedSubject:
    track_id: int
    subject: SubjectDetection
    first_no_helmet: bool


class CentroidTracker:
    """Lightweight tracker used by the MVP to avoid counting every frame as a new object."""

    def __init__(self, max_missing: int = 18, max_distance_ratio: float = 0.08, confirmation_frames: int = 3) -> None:
        self.max_missing = max_missing
        self.max_distance_ratio = max_distance_ratio
        self.confirmation_frames = max(1, confirmation_frames)
        self._next_id = 1
        self.active: dict[int, Track] = {}
        self.history: dict[int, Track] = {}

    @staticmethod
    def _centroid(bbox: tuple[int, int, int, int]) -> tuple[float, float]:
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    def _new_track(self, subject: SubjectDetection) -> Track:
        status = subject.status
        track = Track(
            track_id=self._next_id,
            bbox=subject.bbox,
            centroid=self._centroid(subject.bbox),
            last_status=status,
            last_confidence=subject.confidence,
            ever_helmet=status == DetectionKind.HELMET,
            ever_no_helmet=status == DetectionKind.NO_HELMET and self.confirmation_frames == 1,
            no_helmet_streak=int(status == DetectionKind.NO_HELMET),
            last_subject=subject,
        )
        self._next_id += 1
        self.active[track.track_id] = track
        self.history[track.track_id] = track
        return track

    def update(
        self,
        subjects: list[SubjectDetection],
        frame_shape: tuple[int, int, int] | tuple[int, int],
    ) -> list[TrackedSubject]:
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
                self.active[track_id].no_helmet_streak = 0
                if self.active[track_id].missing > self.max_missing:
                    del self.active[track_id]

        # Generate output
        tracked: list[TrackedSubject] = []
        for subject_index, subject in enumerate(subjects):
            track_id = assignment.get(subject_index)
            if track_id is None:
                track = self._new_track(subject)
                first_no_helmet = track.ever_no_helmet
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
                track.ever_helmet = track.ever_helmet or subject.status == DetectionKind.HELMET
                track.no_helmet_streak = (
                    track.no_helmet_streak + 1 if subject.status == DetectionKind.NO_HELMET else 0
                )
                track.ever_no_helmet = track.ever_no_helmet or track.no_helmet_streak >= self.confirmation_frames
                first_no_helmet = track.ever_no_helmet and not was_no_helmet
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
        tracks = list(self.history.values())
        total = len(tracks)
        no_helmet = sum(track.ever_no_helmet for track in tracks)
        helmet = sum(track.ever_helmet and not track.ever_no_helmet for track in tracks)
        return total, helmet, no_helmet
