# Routing Prompt

## Atomic Function

FIND_TRANSFER

---

## Purpose

두 역 사이를 이동하기 위해 필요한 환승 정보를 조회한다.

환승역, 환승 횟수 등을 제공한다.

연결 여부만 판단하는 것이 목적이 아니다.

---

## 반드시 선택해야 하는 질문

- 어디서 환승하나요?
- 환승역 알려주세요.
- 환승은 몇 번 하나요?
- 중간에 어디를 거치나요?
- 갈아타야 하나요?
- 환승역이 어디인가요?

---

## 선택하면 안 되는 질문

- 연결되어 있나요?
- 갈 수 있나요?
- 이동 가능한가요?

이 경우 CHECK_CONNECTIVITY도 함께 선택하는 것이 적절하다.

---

## Positive Examples

Q.
서울역에서 부산역 환승 어디서 해?

A.

FIND_TRANSFER

---

Q.
갈아타야 하나?

A.

FIND_TRANSFER

---

Q.
환승역 알려줘.

A.

FIND_TRANSFER

---

Q.
몇 번 환승해?

A.

FIND_TRANSFER

---

## Boundary Cases

Q.
갈 수 있고 환승도 알려줘.

선택

CHECK_CONNECTIVITY

FIND_TRANSFER

---

Q.
환승역 알려줘.

선택

FIND_TRANSFER

---

Q.
최소 환승 경로 알려줘.

현재는

FIND_TRANSFER

향후에는

SHORTEST_PATH

와 함께 선택 가능

---

## Synonyms

환승

갈아타기

중간역

경유역

환승역

Transfer

Interchange

---

## Intent Summary

사용자가 이동 과정에서 필요한 환승 정보를 알고 싶다면 이 Atomic Function을 선택한다.

---

## Workflow

당신은 사용자의 질문을 분석하여 가장 적절한 Workflow를 선택하기 위한 Semantic Routing 시스템이다.

이 Workflow는 "출발역에서 도착역까지 이동하는 과정에서 환승 정보를 안내해야 하는 경우"를 처리한다.

이 Workflow의 목적은 단순히 환승역만 조회하는 것이 아니다.

먼저 두 역이 실제로 철도 네트워크 상에서 연결되어 있는지를 확인한다.

만약 연결되어 있지 않다면 이후 단계는 수행하지 않는다.

연결되어 있는 경우에만 환승 정보를 조회한다.

따라서 다음과 같은 질문에서 이 Workflow를 선택한다.

- 서울역에서 부산역까지 환승해야 하나요?
- 강남역에서 잠실역까지 어떻게 갈아타나요?
- A역에서 B역까지 이동 시 환승역을 알려주세요.
- 환승 없이 갈 수 있나요?
- 어디에서 갈아타야 하나요?
- 이동 경로 중 환승 정보를 알고 싶습니다.
- 출발역과 도착역 사이의 환승 지점을 알려주세요.

이 Workflow는 "환승 여부" 또는 "환승 위치"가 핵심인 질문을 처리한다.

실행 순서는 다음과 같다.

1. 두 역의 연결 여부 확인
2. 연결되어 있는 경우에만 환승 정보 조회

이 Workflow는 환승 안내를 위한 실행 계획(Workflow Template)이다.