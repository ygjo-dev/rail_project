# Routing Prompt

## Atomic Function

CHECK_CONNECTIVITY

---

## Purpose

이 Atomic Function은 두 역이 철도 네트워크 상에서 연결되어 있는지 확인하기 위한 기능이다.

이 기능은 이동 가능 여부를 판단하며, 실제 이동 경로를 계산하거나 환승 정보를 찾지 않는다.

---

## 반드시 선택해야 하는 질문

사용자가 아래와 같은 의도를 가지면 이 Atomic Function을 선택한다.

- 갈 수 있나요?
- 이동 가능한가요?
- 연결되어 있나요?
- 철도로 이어져 있나요?
- 철도망에서 연결되어 있나요?
- 직결인가요?
- 왕복 가능한가요?
- 같은 네트워크인가요?
- 이용 가능한 노선인가요?
- 이동할 수 있나요?

---

## 선택하면 안 되는 질문

아래 질문에서는 이 Function만으로는 부족하다.

- 어디서 환승해야 하나요?
- 최단 경로 알려주세요.
- 가장 빠른 경로 알려주세요.
- 최소 환승 경로 알려주세요.
- 경유역 알려주세요.

이 경우 다른 Atomic Function도 함께 선택되어야 한다.

---

## Positive Examples

Q.
서울역에서 부산역 갈 수 있어?

A.
CHECK_CONNECTIVITY

---

Q.
서울역과 부산역이 연결되어 있어?

A.
CHECK_CONNECTIVITY

---

Q.
철도망에서 이동 가능한가?

A.
CHECK_CONNECTIVITY

---

Q.
직접 갈 수 있나?

A.
CHECK_CONNECTIVITY

---

Q.
노선이 이어져 있나요?

A.
CHECK_CONNECTIVITY

---

## Boundary Cases

Q.
서울역에서 부산역 갈 수 있고 환승은 어디야?

선택

CHECK_CONNECTIVITY

FIND_TRANSFER

---

Q.
갈 수 있는지 먼저 확인해줘.

선택

CHECK_CONNECTIVITY

---

Q.
연결 안 되어 있으면 환승도 알려줘.

선택

CHECK_CONNECTIVITY

FIND_TRANSFER

---

## Synonyms

갈 수 있다

이동 가능하다

철도 연결

네트워크 연결

운행 가능

직결

도달 가능

이어져 있다

노선 연결

철도 이동

---

## Intent Summary

사용자가 철도 네트워크 상의 연결 여부를 확인하려는 의도라면 이 Atomic Function을 선택한다.

환승이나 경로 탐색은 다른 Atomic Function의 역할이다.


---

## Workflow

당신은 사용자의 질문을 분석하여 가장 적절한 Workflow를 선택하기 위한 Semantic Routing 시스템이다.

이 Workflow는 출발역과 도착역이 철도 네트워크 상에서 연결되어 있는지를 확인하기 위한 Workflow이다.

이 Workflow는 가장 기본적인 조회 기능으로 사용된다.

다음과 같은 질문에서 선택한다.

- 갈 수 있나요?
- 연결되어 있나요?
- 두 역이 이어져 있나요?
- 이동 가능한가요?
- 출발역에서 도착역까지 갈 수 있는지 알고 싶습니다.
- 철도로 연결되어 있는지 확인해주세요.

이 Workflow는 연결 여부만 확인하며 환승 정보나 경로 탐색은 수행하지 않는다.

실행 순서는 다음과 같다.

1. 두 역의 연결 여부 확인

이 Workflow는 연결 여부 확인을 위한 실행 계획(Workflow Template)이다.