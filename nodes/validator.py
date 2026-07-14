from state import WorkflowState


def validate(
    state: WorkflowState,
) -> bool:

    if not state.context:
        return False

    for value in state.context.values():

        if value:
            return True

    return False