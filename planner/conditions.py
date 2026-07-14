from state import WorkflowState

def connected(
    state: WorkflowState,
) -> bool:

    result = state.context.get(
        "CHECK_CONNECTIVITY",
        {}
    )

    return result.get(
        "connected",
        False,
    )