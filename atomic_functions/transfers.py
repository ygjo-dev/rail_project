from atomic_functions.base import BaseAtomicFunction
from state import WorkflowState


class TransferFunction(BaseAtomicFunction):

    def execute(
        self,
        state: WorkflowState,
    ) -> WorkflowState:

        result = state.graph.find_transfer(
            state.from_station,
            state.to_station,
        )

        state.context[
            "FIND_TRANSFER"
        ] = result

        return state