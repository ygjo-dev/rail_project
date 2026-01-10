import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import yaml
import time
import streamlit as st
from py2neo import Graph
import folium
from streamlit_folium import st_folium
import ollama

# -----------------------------
# 내부 모듈 import
# -----------------------------
from intent.intents import ALL_INTENTS
from cypher.connectivity import check_connectivity
from cypher.transfers import count_transfers
from intent.parser import parse_intent
from intent.answer_generator import generate_answer

# -----------------------------
# 설정 파일 로드 (YAML)
# -----------------------------
CONFIG_FILE = os.environ.get("CONFIG_FILE", "./config/config.yaml")
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

OLLAMA_API_URL = cfg["ollama"]["api_url"]
PARSER_MODEL = cfg["ollama"]["parser_model"]
ANSWER_MODEL = cfg["ollama"]["answer_model"]

NEO4J_URI = cfg["neo4j"]["uri"]
NEO4J_USER = cfg["neo4j"]["user"]
NEO4J_PASSWORD = cfg["neo4j"]["password"]

ollama.api_url = OLLAMA_API_URL
graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# -----------------------------
# Streamlit UI 설정
# -----------------------------
st.set_page_config(layout="wide")
st.title("Neo4j DB 챗봇 질의")

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
# 질문 입력
# -----------------------------
st.sidebar.header("철도 연결 질문")
user_question = st.sidebar.text_input("예: 서울에서 영등포 가요?")

if user_question:
    total_start = time.perf_counter()
    
    try:
        # 1. Intent / Slot 파싱
        parse_start = time.perf_counter()
        parsed = parse_intent(user_question, PARSER_MODEL)
        parse_elapsed = time.perf_counter() - parse_start

        st.sidebar.subheader("LLM 파싱 결과 (Debug)")
        st.sidebar.json(parsed)

        # 2. 누락 정보 체크
        if parsed.get("missing_info"):
            st.sidebar.warning(
                f"추가 정보가 필요합니다: {', '.join(parsed['missing_info'])}"
            )

        # 3. DB 조회 (intent별 로직)
        context = {"intent": parsed.get("intent")}
        db_start = time.perf_counter()
        
        if parsed.get("intent") == "CHECK_CONNECTIVITY":
            context.update({
                "from_station": parsed.get("from_station"),
                "to_station": parsed.get("to_station"),
                "is_connected": check_connectivity(
                    graph,
                    parsed.get("from_station"),
                    parsed.get("to_station")
                )
            })
        
        elif parsed.get("intent") == "COUNT_TRANSFERS":
            transfers = count_transfers(
                graph,
                parsed.get("from_station"),
                parsed.get("to_station")
            )
            context.update({
                "from_station": parsed.get("from_station"),
                "to_station": parsed.get("to_station"),
                "transfers": transfers
            })
        
        db_elapsed = time.perf_counter() - db_start

        # 4. 자연어 응답 생성
        answer_start = time.perf_counter()
        answer = generate_answer(context, ANSWER_MODEL)
        answer_elapsed = time.perf_counter() - answer_start

        st.sidebar.markdown(answer)

        # -----------------------------
        # 처리 시간 표시
        # -----------------------------
        total_elapsed = time.perf_counter() - total_start
        st.sidebar.info(f"총 처리 시간: {total_elapsed:.2f}초")
        st.sidebar.info(f"  • 파싱 시간: {parse_elapsed:.2f}초 ({PARSER_MODEL})")
        st.sidebar.info(f"  • DB 조회 시간: {db_elapsed:.2f}초")
        st.sidebar.info(f"  • 응답 생성 시간: {answer_elapsed:.2f}초 ({ANSWER_MODEL})")

    except Exception as e:
        total_elapsed = time.perf_counter() - total_start
        st.sidebar.error("오류 발생")
        st.sidebar.code(str(e))
        st.sidebar.info(f"총 처리 시간: {total_elapsed:.2f}초")
