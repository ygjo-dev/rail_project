from state import WorkflowState


class ExecutionEngine:

    def run(
        self,
        state: WorkflowState,
    ) -> WorkflowState:

        for step in state.execution_plan:

            if step.condition is not None:

                if not step.condition(state):
                    continue

            executor = step.executor_cls()

            state = executor.execute(
                state
            )

        return state