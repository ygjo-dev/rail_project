import json

import ollama

from utils.prompt_loader import load_prompt
from state import WorkflowState


PROMPT_TEMPLATE = load_prompt("nodes/parser")


def parse_intent(
    question: str,
    model: str
) -> dict:
    """
    사용자 질문에서 철도 엔티티를 추출한다.

    Returns
    -------
    {
        "from_station": "...",
        "to_station": "...",
        "missing_info": []
    }
    """

    prompt = PROMPT_TEMPLATE.format(
        question=question
    )

    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"].strip()

    try:
        parsed = json.loads(content)

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse LLM response as JSON.\n\n{content}"
        ) from e

    required_fields = [
        "from_station",
        "to_station"
    ]

    missing = [
        field
        for field in required_fields
        if parsed.get(field) is None
    ]

    parsed["missing_info"] = missing

    return parsed

from state import WorkflowState


def parse(
    state: WorkflowState,
) -> WorkflowState:

    parsed = parse_intent(
        state.question,
        state.parser_model,
    )

    state.from_station = parsed.get(
        "from_station"
    )

    state.to_station = parsed.get(
        "to_station"
    )

    state.missing_info = parsed.get(
        "missing_info",
        [],
    )

    return state