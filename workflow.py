import time

from state import WorkflowState

from planner.execution_engine import (
    ExecutionEngine,
)

from nodes.parser import parse
from nodes.router import route_state
from nodes.validator import validate
from nodes.feedback import retry
from nodes.answer_generator import generate


def run_workflow(
    question,
    graph,
    parser_model,
    answer_model,
):

    state = WorkflowState(
        question=question,
        graph=graph,
        parser_model=parser_model,
        answer_model=answer_model,
    )

    metrics = {}

    # ==========================
    # Parse
    # ==========================

    parse_start = time.perf_counter()

    state = parse(state)

    metrics["parse_time"] = (
        time.perf_counter()
        - parse_start
    )

    if state.missing_info:

        return {
            "success": False,
            "state": state,
            "error":
                "추가 정보가 필요합니다: "
                + ", ".join(
                    state.missing_info
                ),
        }

    # ==========================
    # Semantic Routing
    # ==========================

    routing_start = time.perf_counter()

    state = route_state(state)

    metrics["routing_time"] = (
        time.perf_counter()
        - routing_start
    )

    # ==========================
    # Execute Workflow
    # ==========================

    execute_start = time.perf_counter()

    engine = ExecutionEngine()

    state = engine.run(
        state
    )

    metrics["execution_time"] = (
        time.perf_counter()
        - execute_start
    )

    # ==========================
    # Validate
    # ==========================

    if not validate(state):

        state = retry(state)

    # ==========================
    # Generate Answer
    # ==========================

    answer_start = time.perf_counter()

    state = generate(state)

    metrics["answer_time"] = (
        time.perf_counter()
        - answer_start
    )

    state.metadata["metrics"] = metrics

    return {
        "success": True,
        "state": state,
        "answer": state.answer,
        "metrics": metrics,
    }