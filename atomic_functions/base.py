from abc import ABC
from abc import abstractmethod

from state import WorkflowState


class BaseAtomicFunction(ABC):

    @abstractmethod
    def execute(
        self,
        state: WorkflowState,
    ) -> WorkflowState:
        pass