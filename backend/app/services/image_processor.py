from __future__ import annotations

from pathlib import Path

import cv2

from app.core.config import settings
from app.services.ai.detector import Detector
from app.services.ai.violation import DetectionKind, ViolationLogic
from app.services.evidence_service import draw_subject, draw_summary, save_evidence_crop, save_image
from app.services.processing_types import ProcessResult, ViolationArtifact
from app.utils.files import storage_relative


def process_image(
    *,
    source_path: Path,
    detector: Detector,
    violation_logic: ViolationLogic,
    session_id: int,
    media_id: int,
    project_id: int,
    location_id: int,
    analysis_date: str,
) -> ProcessResult:
    frame = cv2.imread(str(source_path))
    if frame is None:
        raise ValueError(f"Không thể đọc ảnh: {source_path.name}")

    detections = detector.predict(frame)
    assessment = violation_logic.assess_image(detections)
    annotated = frame.copy()
    for subject in assessment.subjects:
        draw_subject(annotated, subject)
    draw_summary(
        annotated,
        total=assessment.total_vehicles,
        helmet=assessment.helmet_count,
        no_helmet=assessment.no_helmet_count,
    )

    result_path = settings.storage_root / "results" / f"session_{session_id}" / f"media_{media_id}.jpg"
    save_image(result_path, annotated)

    violations: list[ViolationArtifact] = []
    evidence_dir = (
        settings.storage_root
        / "violations"
        / analysis_date
        / f"project_{project_id}"
        / f"location_{location_id}"
        / f"session_{session_id}"
    )
    violation_index = 0
    for subject in assessment.subjects:
        if subject.status != DetectionKind.NO_HELMET:
            continue
        violation_index += 1
        evidence_path = evidence_dir / f"media_{media_id}_violation_{violation_index:04d}.jpg"
        save_evidence_crop(frame, subject, evidence_path)
        violations.append(
            ViolationArtifact(
                confidence=subject.confidence,
                evidence_path=storage_relative(evidence_path),
                bbox=subject.bbox,
                vehicle_id=f"IMG-{media_id}-{violation_index}",
            )
        )

    return ProcessResult(
        result_path=storage_relative(result_path),
        total_vehicles=assessment.total_vehicles,
        helmet_count=assessment.helmet_count,
        no_helmet_count=assessment.no_helmet_count,
        violations=violations,
    )
