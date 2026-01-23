# Rail-Knowledge Intelligence: Agentic GraphRAG 시스템
철도 관련 전문 데이터를 그래프 구조로 정규화하고, 사용자 질문의 의도를 분석하여 정확한 경로 및 연결 정보를 제공하는 **LLM 기반 지능형 지식 에이전트**입니다.

## 프로젝트 개요
1. 단순한 텍스트 검색 기반 RAG의 한계를 극복하기 위해 GraphRAG(Graph Retrieval-Augmented Generation) 기술 구현 목적. 
2. 철도역과 노선 간의 관계를 Neo4j 그래프 데이터베이스로 구축하고, LangGraph를 통해 질문 의도 파악부터 Cypher 쿼리 생성, 답변 최적화까지 이어지는 에이전트 워크플로우 구현 목적.

## 주요 기능
- **Intent-Based Graph Search:** 사용자의 자연어 질문에서 출발지, 도착지 등의 정보를 추출하고 질문의 의도(연결성, 환승 등)를 파악
- **Dynamic Cypher Generation:** 추출된 의도를 바탕으로 그래프 DB 조회를 위한 Cypher 쿼리를 실행하여 정확한 데이터를 추출
- **Interactive Visualization:** Streamlit과 Folium을 연동하여 철도 네트워크를 지도상에 시각화하고 대화형 인터페이스를 제공

## 시스템 아키텍처 (Agentic Workflow)
1. **InUser Inputput:** 사용자로부터 철도 관련 질문 수신 (예: "서울에서 천안까지 KTX로 갈 수 있어?")
2. **Intent Parsing:** - 질문의 의도를 분석하고 주요 개체(역 이름, 노선 등)를 추출
   - 답변 불가능할 경우 추가 정보 요청 혹은 거절 메시지 생성
3. **Graph Traversal (Neo4j):** 분석된 정보를 바탕으로 그래프 DB 내의 노드와 관계를 탐색
4. **Context Synthesis:** DB 조회 결과와 질문을 결합하여 최적의 컨텍스트 생성
5. **Final Answer:** 생성된 컨텍스트를 바탕으로 사용자에게 답변 제공

## 기술 스택
- **Language:** Python
- **Orchestration:** LangChain, LangGraph
- **LLM:** Ollama (Llama3-8B, Qwen2.5-3B)
- **Database:** Neo4j (Graph Database)
- **Infra:** Docker, Docker Compose
- **UI:** Streamlit, Folium, PyDeck

## 기술적 도전과 해결 방안
- **데이터 적합성 판단:** 질문의 의도가 철도 도메인인지 판별하는 로직을 LangGraph 노드로 구성하여 불필요한 API 호출 및 비용 절감
- **정밀한 데이터 검색:** 복잡한 철도 용어를 처리하기 위한 임베딩 최적화 및 검색 결과 재랭킹(Reranking) 전략 고민
- **워크플로우 제어:** 복잡한 조건 분기를 LangGraph의 상태 관리(State Management)를 통해 안정적으로 구현

## 프로젝트 구조
```text
├── config/             # 시스템 설정 템플릿 (config.template.yaml)
├── cypher/             # Neo4j 쿼리 실행 및 데이터 처리 로직
├── data/               # 철도 데이터 파일 (GeoJSON 등)
├── intent/             # 질문 의도 분석 및 프롬프트 로직
├── neo4j_scripts/      # 데이터 전처리 및 DB 적재 스크립트 (import_geojson.py)
├── utils/              # 설정 로더 및 공통 유틸리티
├── streamlit_app/      # 메인 UI 서비스 (map_from_neo4j.py)
├── docker-compose.yml  # 전체 서비스 오케스트레이션
└── Dockerfile          # 어플리케이션 빌드
```

## 시작 가이드

1. **저장소 클론 (Branch: main):**
   ```bash
   git clone https://github.com/ygjo-dev/rail_project.git
   cd rail_project
   ```
2. **환경 변수 설정 (.env):** 프로젝트 루트 폴더에 .env 파일을 생성하고 아래 내용을 입력합니다. 이 설정은 Docker Compose가 프로젝트 폴더를 인식하는 데 사용됩니다.
   ```Plaintext
   # .env 파일 내용
   PROJECT_PATH=.
   ```
3. **데이터 및 설정 준비:**
   - 'data/' 폴더에 '{데이터이름}.geojson' 파일을 추가
   - 'config/config.template.yaml'을 복사하여 'config/config.yaml'을 생성하고 접속 정보를 입력
4. **환경 구축 및 실행:**
   모든 서비스 빌드 및 실행 (Neo4j, Ollama, Streamlit)
   
   - **CPU-only 모드**: CPU만 존재하는 환경일 때
   ```bash
   docker-compose up -d
   ```
   - **NVIDIA GPU 활용 모드**: GPU 드라이버와 Toolkit이 설치된 환경일 때
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
   ```
5. **서비스 실행:**
   ```bash
   # 컨테이너 실행 후 초기 1회 데이터 import(neo4j 서버에 그래프DB 생성) 수행
   docker exec -it streamlit-env python neo4j_scripts/import_geojson.py
   ```
6. **서비스 접속:**
   - 웹 브라우저에서 http://localhost:8501 접속