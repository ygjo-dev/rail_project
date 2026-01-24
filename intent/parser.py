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

--------------------------------------------------
[Intent 정의]
--------------------------------------------------

CHECK_CONNECTIVITY
- 두 역 사이에 철도 경로가 존재하는지 여부를 묻는 질문

COUNT_TRANSFERS
- 두 역 사이 이동 시 필요한 환승 횟수를 묻는 질문

LIST_LINES
- 두 역 사이 이동에 사용되는 철도 노선 정보를 묻는 질문

CHECK_STATION_VALID
- 특정 역이 DB에 존재하는지 확인하는 질문

--------------------------------------------------
[판단 원칙]
--------------------------------------------------

- 질문의 핵심 목적에 가장 가까운 Intent 하나만 선택한다.
- 여러 의미가 섞여 있어도 가장 우선되는 하나를 선택한다.
- 출발역(from_station), 도착역(to_station) 등 필요한 슬롯 값을 추출한다.
- 질문에서 누락된 필수 슬롯 값은 null로 둔다.
- null로 된 슬롯 이름을 그대로 missing_info 배열에 추가하여 명시한다.
- 실제로 값이 있는 슬롯 이름은 missing_info에 넣지 않는다.
- 만약 질문에서 intent를 판단할 수 없으면 intent를 "null"으로 설정한다.

--------------------------------------------------
[출력]
--------------------------------------------------

반드시 JSON만 출력한다.
설명 문장, 코드블록, 주석을 포함하지 않는다.
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
    후처리로 missing_info 검증 및 intent 기본값 설정
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
        parsed = json.loads(content)
    except Exception:
        raise ValueError(f"LLM output parse error: {content}")

    # 후처리: intent 기본값
    if not parsed.get("intent"):
        parsed["intent"] = "null"

    # 후처리: missing_info 검증
    missing = []
    for slot in ["from_station", "to_station"]:
        if parsed.get(slot) is None:
            missing.append(slot)
    parsed["missing_info"] = missing

    return parsed
