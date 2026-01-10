import json
import ollama
from intent.intents import ALL_INTENTS

SYSTEM_PROMPT = """
너는 철도 Neo4j 데이터베이스 질의를 위한 Intent 파서다.

역할:
사용자의 질문을 분석하여,
어떤 유형의 DB 질의를 실행해야 하는지(Intent)를 하나 선택하고
필요한 역 이름 정보를 추출한다.

너는 Cypher를 생성하지 않는다.
너는 질문에 직접 답하지 않는다.
추측하거나 없는 정보를 만들어내지 않는다.
"""

USER_PROMPT_TEMPLATE = """
질문을 분석하여 아래 형식의 JSON으로 출력하라.

가능한 intent 목록:
{intent_list}

출력 형식:
{{
  "intent": "...",
  "from_station": "...",
  "to_station": "...",
  "missing_info": []
}}

질문:
"{question}"
"""

def parse_intent(question: str, model: str) -> dict:
    """
    Ollama 모델을 사용해 intent + slot 파싱
    """
    prompt = USER_PROMPT_TEMPLATE.format(
        intent_list=", ".join(ALL_INTENTS),
        question=question
    )

    resp = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    content = resp["message"]["content"]

    try:
        return json.loads(content)
    except Exception:
        raise ValueError(f"LLM output parse error: {content}")
