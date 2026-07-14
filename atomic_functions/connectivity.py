from atomic_functions.base import BaseAtomicFunction
from state import WorkflowState


class ConnectivityFunction(BaseAtomicFunction):

    def execute(
        self,
        state: WorkflowState,
    ) -> WorkflowState:

        result = state.graph.check_connectivity(
            state.from_station,
            state.to_station,
        )

        state.context[
            "CHECK_CONNECTIVITY"
        ] = result

        return state