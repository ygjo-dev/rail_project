import json
import ollama

def generate_answer(context: dict, model: str) -> str:
    """
    DB 계산 결과(context)를 기반으로 LLM이 자연어 답변만 생성
    """
    prompt = f"""
너는 철도 정보 안내 시스템이다.

아래 JSON 결과를 사실 그대로 자연어로 설명하라.

규칙:
- JSON에 없는 정보는 절대 추측하지 말 것
- 단정적으로 말할 것
- 불필요한 설명은 하지 말 것
- 한국어로 답변할 것

JSON:
{json.dumps(context, ensure_ascii=False, indent=2)}
"""

    resp = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": "철도 질의 결과 설명"},
            {"role": "user", "content": prompt}
        ]
    )

    return resp["message"]["content"]
