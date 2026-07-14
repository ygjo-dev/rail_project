from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING

from atomic_functions.base import BaseAtomicFunction

if TYPE_CHECKING:
    from state import WorkflowState


@dataclass
class ExecutionStep:

    executor_cls: type[BaseAtomicFunction]

    condition: Callable[
        ["WorkflowState"],
        bool,
    ] | None = None