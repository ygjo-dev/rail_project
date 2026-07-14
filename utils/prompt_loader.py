from pathlib import Path


PROMPT_DIR = Path("prompts")


def load_prompt(
    prompt_name: str,
    **kwargs,
):

    path = PROMPT_DIR / f"{prompt_name}.md"

    prompt = path.read_text(
        encoding="utf-8"
    )

    if kwargs:

        prompt = prompt.format(
            **kwargs
        )

    return prompt