import json

import ollama

from state import WorkflowState
from utils.prompt_loader import load_prompt


def generate(
    state: WorkflowState,
) -> WorkflowState:
    """
    Atomic Function 결과(JSON)를 자연어 답변으로 변환한다.
    """

    prompt = load_prompt(
        "nodes/answer_generator",
        context=json.dumps(
            state.context,
            ensure_ascii=False,
            indent=2,
        ),
    )

    response = ollama.chat(
        model=state.answer_model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    state.answer = response["message"]["content"]

    return state