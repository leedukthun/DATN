from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import Enum

from app.services.ai.detector import Detection


class DetectionKind(str, Enum):
    HELMET = "HELMET"
    NO_HELMET = "NO_HELMET"
    VEHICLE = "VEHICLE"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


@dataclass(slots=True)
class SubjectDetection:
    bbox: tuple[int, int, int, int]
    confidence: float
    status: DetectionKind
    source_label: str
    head_bbox: tuple[int, int, int, int] | None = None
    vehicle_bbox: tuple[int, int, int, int] | None = None

    @property
    def center(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


@dataclass(slots=True)
class ImageAssessment:
    subjects: list[SubjectDetection]
    total_vehicles: int
    helmet_count: int
    no_helmet_count: int

    @property
    def violation_count(self) -> int:
        return self.no_helmet_count


class ViolationLogic:
    """Maps model classes to business states and associates head states to vehicles when available."""

    def __init__(
        self,
        helmet_names: list[str],
        no_helmet_names: list[str],
        vehicle_names: list[str],
        *,
        require_vehicle: bool = False,
        ignore_zones: list[tuple[float, float, float, float]] | None = None,
        head_dedup_iou: float = 0.5,
    ) -> None:
        self.helmet_names = {self.normalize(value) for value in helmet_names}
        self.no_helmet_names = {self.normalize(value) for value in no_helmet_names}
        self.vehicle_names = {self.normalize(value) for value in vehicle_names}
        self.require_vehicle = require_vehicle
        self.ignore_zones = list(ignore_zones or [])
        self.head_dedup_iou = head_dedup_iou

    def has_vehicle_class(self, class_names: list[str]) -> bool:
        return any(self.normalize(name) in self.vehicle_names for name in class_names)

    @staticmethod
    def normalize(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", value.lower())

    def kind(self, detection: Detection) -> DetectionKind:
        name = self.normalize(detection.class_name)
        if name in self.no_helmet_names:
            return DetectionKind.NO_HELMET
        if name in self.helmet_names:
            return DetectionKind.HELMET
        if name in self.vehicle_names:
            return DetectionKind.VEHICLE
        return DetectionKind.OTHER

    @staticmethod
    def _head_vehicle_score(head: Detection, vehicle: Detection) -> float | None:
        hx, hy = head.center
        x1, y1, x2, y2 = vehicle.bbox
        width = max(1, x2 - x1)
        height = max(1, y2 - y1)

        # A rider's head is normally around the upper part of a motorcycle box,
        # and may sit slightly above that box depending on the detector.
        expanded_x1 = x1 - 0.20 * width
        expanded_x2 = x2 + 0.20 * width
        expanded_y1 = y1 - 0.80 * height
        expanded_y2 = y1 + 0.70 * height
        if not (expanded_x1 <= hx <= expanded_x2 and expanded_y1 <= hy <= expanded_y2):
            return None

        target_x = (x1 + x2) / 2.0
        target_y = y1
        distance = math.hypot(hx - target_x, hy - target_y)
        scale = max(width, height)
        return distance / max(scale, 1.0)

    @staticmethod
    def _iou(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
        ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
        ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
        inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
        if inter == 0:
            return 0.0
        area_a = max(0, a[2] - a[0]) * max(0, a[3] - a[1])
        area_b = max(0, b[2] - b[0]) * max(0, b[3] - b[1])
        return inter / max(1, area_a + area_b - inter)

    def _dedupe_heads(self, heads: list[Detection]) -> list[Detection]:
        """YOLO runs NMS per class, so one head can come back as both helmet and no-helmet."""
        kept: list[Detection] = []
        for head in sorted(heads, key=lambda item: item.confidence, reverse=True):
            if all(self._iou(head.bbox, other.bbox) < self.head_dedup_iou for other in kept):
                kept.append(head)
        return kept

    def _in_ignore_zone(self, detection: Detection, frame_shape: tuple[int, ...] | None) -> bool:
        if not self.ignore_zones or frame_shape is None:
            return False
        height, width = frame_shape[:2]
        cx, cy = detection.center
        nx, ny = cx / max(1, width), cy / max(1, height)
        return any(x1 <= nx <= x2 and y1 <= ny <= y2 for x1, y1, x2, y2 in self.ignore_zones)

    def _split(
        self,
        detections: list[Detection],
        frame_shape: tuple[int, ...] | None,
    ) -> tuple[list[Detection], list[Detection]]:
        detections = [item for item in detections if not self._in_ignore_zone(item, frame_shape)]
        vehicles = [item for item in detections if self.kind(item) == DetectionKind.VEHICLE]
        heads = self._dedupe_heads(
            [
                item
                for item in detections
                if self.kind(item) in (DetectionKind.HELMET, DetectionKind.NO_HELMET) and self._head_shaped(item)
            ]
        )
        return vehicles, heads

    @staticmethod
    def _head_shaped(detection: Detection) -> bool:
        """Heads are roughly square; wide boxes are cars or cargo the model mistook for a head."""
        x1, y1, x2, y2 = detection.bbox
        ratio = max(1, x2 - x1) / max(1, y2 - y1)
        return 0.35 <= ratio <= 1.5

    def _best_vehicle(self, head: Detection, vehicles: list[Detection]) -> Detection | None:
        candidates = [
            (score, index)
            for index, vehicle in enumerate(vehicles)
            if (score := self._head_vehicle_score(head, vehicle)) is not None
        ]
        return vehicles[min(candidates)[1]] if candidates else None

    def build_head_observations(
        self,
        detections: list[Detection],
        frame_shape: tuple[int, ...] | None = None,
    ) -> list[SubjectDetection]:
        """One subject per head, for video tracking.

        Vehicle boxes flicker in and out on CCTV footage, so a head is never dropped for lacking
        a vehicle in a single frame; the tracker decides over time whether it belongs to a rider.
        """
        vehicles, heads = self._split(detections, frame_shape)
        if frame_shape is not None:
            # A head cut by the frame edge is only partly visible; wait until it is in view.
            height, width = frame_shape[:2]
            heads = [h for h in heads if h.bbox[0] > 2 and h.bbox[2] < width - 2 and h.bbox[3] < height - 2]
        observations: list[SubjectDetection] = []
        for head in heads:
            vehicle = self._best_vehicle(head, vehicles)
            observations.append(
                SubjectDetection(
                    bbox=head.bbox,
                    confidence=head.confidence,
                    status=self.kind(head),
                    source_label=head.class_name,
                    head_bbox=head.bbox,
                    vehicle_bbox=vehicle.bbox if vehicle is not None else None,
                )
            )
        return observations

    def build_subjects(
        self,
        detections: list[Detection],
        frame_shape: tuple[int, ...] | None = None,
    ) -> list[SubjectDetection]:
        vehicles, heads = self._split(detections, frame_shape)
        helmets = [item for item in heads if self.kind(item) == DetectionKind.HELMET]
        no_helmets = [item for item in heads if self.kind(item) == DetectionKind.NO_HELMET]

        def head_subject(item: Detection) -> SubjectDetection:
            return SubjectDetection(
                bbox=item.bbox,
                confidence=item.confidence,
                status=self.kind(item),
                source_label=item.class_name,
                head_bbox=item.bbox,
            )

        # A head-state-only model (With Helmet / Without Helmet) has no vehicle boxes,
        # so each helmet-state box is treated as one observed rider.
        if not vehicles:
            return [] if self.require_vehicle else [head_subject(item) for item in heads]

        subjects = [
            SubjectDetection(
                bbox=vehicle.bbox,
                confidence=vehicle.confidence,
                status=DetectionKind.UNKNOWN,
                source_label=vehicle.class_name,
            )
            for vehicle in vehicles
        ]

        def associate(head: Detection) -> int | None:
            candidates: list[tuple[float, int]] = []
            for index, vehicle in enumerate(vehicles):
                score = self._head_vehicle_score(head, vehicle)
                if score is not None:
                    candidates.append((score, index))
            return min(candidates)[1] if candidates else None

        unassociated: list[Detection] = []

        # A no-helmet observation takes precedence over a helmet observation.
        for head in helmets:
            index = associate(head)
            if index is None:
                unassociated.append(head)
            elif subjects[index].status == DetectionKind.UNKNOWN:
                subjects[index].status = DetectionKind.HELMET
                subjects[index].confidence = head.confidence
                subjects[index].head_bbox = head.bbox

        for head in no_helmets:
            index = associate(head)
            if index is None:
                unassociated.append(head)
            else:
                subjects[index].status = DetectionKind.NO_HELMET
                subjects[index].confidence = head.confidence
                subjects[index].head_bbox = head.bbox

        # Keep the behaviour consistent with vehicle-less frames when association is optional.
        if not self.require_vehicle:
            subjects.extend(head_subject(item) for item in unassociated)
        return subjects

    def assess_image(
        self,
        detections: list[Detection],
        frame_shape: tuple[int, ...] | None = None,
    ) -> ImageAssessment:
        subjects = self.build_subjects(detections, frame_shape)
        helmet_count = sum(item.status == DetectionKind.HELMET for item in subjects)
        no_helmet_count = sum(item.status == DetectionKind.NO_HELMET for item in subjects)
        return ImageAssessment(
            subjects=subjects,
            total_vehicles=len(subjects),
            helmet_count=helmet_count,
            no_helmet_count=no_helmet_count,
        )
