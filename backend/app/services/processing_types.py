from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ViolationArtifact:
    confidence: float
    evidence_path: str
    bbox: tuple[int, int, int, int]
    vehicle_id: str | None = None
    frame_number: int | None = None
    timestamp_seconds: float | None = None


@dataclass(slots=True)
class ProcessResult:
    result_path: str
    total_vehicles: int
    helmet_count: int
    no_helmet_count: int
    violations: list[ViolationArtifact] = field(default_factory=list)

    @property
    def violation_count(self) -> int:
        return len(self.violations)
