import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import json
import time
import streamlit as st
from py2neo import Graph
import folium
from streamlit_folium import st_folium
import ollama

# -----------------------------
# 내부 모듈 import
# -----------------------------
from intent.intents import CHECK_CONNECTIVITY
from cypher.connectivity import check_connectivity
from intent.parser import parse_intent
from intent.answer_generator import generate_answer

# -----------------------------
# 환경 변수 및 설정 파일 로드
# -----------------------------
CONFIG_FILE = os.environ.get("CONFIG_FILE", "./config/config.json")
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    cfg = json.load(f)

OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", cfg["ollama_api_url"])
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", cfg["ollama_model"])
NEO4J_URI = os.environ.get("NEO4J_URI", cfg["neo4j_uri"])
NEO4J_USER = os.environ.get("NEO4J_USER", cfg["neo4j_user"])
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", cfg["neo4j_password"])

# Ollama API 설정
ollama.api_url = OLLAMA_API_URL

# Neo4j 연결
graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# -----------------------------
# Streamlit UI 설정 (변경 없음)
# -----------------------------
st.set_page_config(layout="wide")
st.title("Neo4j DB 챗봇 질의")

# 지도 시각화
stations = graph.run("""
    MATCH (s:Station)
    WHERE s.lat IS NOT NULL AND s.lon IS NOT NULL
    RETURN s.name AS name, s.lat AS lat, s.lon AS lon
""").data()

m = folium.Map(location=[37.5665, 126.9780], zoom_start=7)

for s in stations:
    folium.Marker(
        location=[s["lat"], s["lon"]],
        popup=s["name"],
        icon=folium.Icon(color="blue", icon="train", prefix="fa")
    ).add_to(m)

st_folium(m, width=750, height=500)

# -----------------------------
# 질문 입력 UI
# -----------------------------
st.sidebar.header("철도 연결 질문")
user_question = st.sidebar.text_input("예: 서울에서 영등포가?")

if user_question:
    start_time = time.perf_counter()

    try:
        # -----------------------------
        # 1. LLM: intent + slot 추출
        # -----------------------------
        parsed = parse_intent(user_question, OLLAMA_MODEL)

        st.sidebar.subheader("LLM 파싱 결과 (Debug)")
        st.sidebar.json(parsed)

        # -----------------------------
        # 2. 정보 부족 시 역질문
        # -----------------------------
        if parsed["missing_info"]:
            st.sidebar.warning(
                f"추가 정보가 필요합니다: {', '.join(parsed['missing_info'])}"
            )

        # -----------------------------
        # 3. Intent별 고정 로직 실행
        # -----------------------------
        else:
            intent = parsed["intent"]

            if intent == CHECK_CONNECTIVITY:
                is_connected = check_connectivity(
                    graph,
                    parsed["from_station"],
                    parsed["to_station"]
                )

                response_context = {
                    "intent": intent,
                    "from_station": parsed["from_station"],
                    "to_station": parsed["to_station"],
                    "is_connected": is_connected
                }

                answer = generate_answer(response_context, OLLAMA_MODEL)
                st.sidebar.markdown(answer)
            else:
                st.sidebar.info(
                    f"Debug: 아직 지원하지 않는 질문 유형입니다: {intent}" #TODO: 질문 유형 생성 필요
                )

        elapsed = time.perf_counter() - start_time
        st.sidebar.info(f"처리 시간: {elapsed:.2f}초")

    except Exception as e:
        elapsed = time.perf_counter() - start_time
        st.sidebar.error("오류 발생")
        st.sidebar.code(str(e))
        st.sidebar.info(f"처리 시간: {elapsed:.2f}초")
