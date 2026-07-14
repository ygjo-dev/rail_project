from planner.execution_engine import (
    ExecutionEngine,
)


def retry(
    state,
    max_retry=2,
):

    engine = ExecutionEngine()

    for _ in range(max_retry):

        state = engine.run(state)

        if state.context:
            break

    return state