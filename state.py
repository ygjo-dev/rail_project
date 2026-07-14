from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from planner.execution_plan import ExecutionStep


@dataclass
class WorkflowState:

    # ==========================
    # Input
    # ==========================

    question: str

    graph: Any

    parser_model: str

    answer_model: str

    # ==========================
    # Parsed Slots
    # ==========================

    from_station: str | None = None

    to_station: str | None = None

    missing_info: list[str] = field(
        default_factory=list
    )

    # ==========================
    # Planner
    # ==========================

    execution_plan: list[ExecutionStep] = field(
        default_factory=list
    )

    routing_candidates: list[dict] = field(
        default_factory=list
    )

    # ==========================
    # Execution Result
    # ==========================

    context: dict = field(
        default_factory=dict
    )

    # ==========================
    # Answer
    # ==========================

    answer: str = ""

    # ==========================
    # Metadata
    # ==========================

    metadata: dict = field(
        default_factory=dict
    )

    error: str | None = None