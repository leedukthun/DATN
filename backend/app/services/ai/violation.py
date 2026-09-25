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
    ) -> None:
        self.helmet_names = {self.normalize(value) for value in helmet_names}
        self.no_helmet_names = {self.normalize(value) for value in no_helmet_names}
        self.vehicle_names = {self.normalize(value) for value in vehicle_names}

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

    def build_subjects(self, detections: list[Detection]) -> list[SubjectDetection]:
        vehicles = [item for item in detections if self.kind(item) == DetectionKind.VEHICLE]
        helmets = [item for item in detections if self.kind(item) == DetectionKind.HELMET]
        no_helmets = [item for item in detections if self.kind(item) == DetectionKind.NO_HELMET]

        # The supplied model may expose only With Helmet / Without Helmet classes.
        # In that case each helmet-state box is treated as one observed rider.
        if not vehicles:
            return [
                SubjectDetection(
                    bbox=item.bbox,
                    confidence=item.confidence,
                    status=self.kind(item),
                    source_label=item.class_name,
                    head_bbox=item.bbox,
                )
                for item in (*helmets, *no_helmets)
            ]

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

        # A no-helmet observation takes precedence over a helmet observation.
        for head in helmets:
            index = associate(head)
            if index is not None and subjects[index].status == DetectionKind.UNKNOWN:
                subjects[index].status = DetectionKind.HELMET
                subjects[index].confidence = head.confidence
                subjects[index].head_bbox = head.bbox

        for head in no_helmets:
            index = associate(head)
            if index is not None:
                subjects[index].status = DetectionKind.NO_HELMET
                subjects[index].confidence = head.confidence
                subjects[index].head_bbox = head.bbox

        return subjects

    def assess_image(self, detections: list[Detection]) -> ImageAssessment:
        subjects = self.build_subjects(detections)
        helmet_count = sum(item.status == DetectionKind.HELMET for item in subjects)
        no_helmet_count = sum(item.status == DetectionKind.NO_HELMET for item in subjects)
        return ImageAssessment(
            subjects=subjects,
            total_vehicles=len(subjects),
            helmet_count=helmet_count,
            no_helmet_count=no_helmet_count,
        )
