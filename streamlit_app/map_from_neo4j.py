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

from intent.intents import ALL_INTENTS
from cypher.connectivity import check_connectivity
from cypher.transfers import count_transfers
from intent.parser import parse_intent
from intent.answer_generator import generate_answer
from utils.config_loader import load_config # Config Loader 사용

# config.yaml 파일 읽기
cfg = load_config()
OLLAMA_API_URL = cfg["ollama"]["api_url"]
PARSER_MODEL = cfg["ollama"]["parser_model"]
ANSWER_MODEL = cfg["ollama"]["answer_model"]

NEO4J_URI = cfg["neo4j"]["uri"]
NEO4J_USER = cfg["neo4j"]["user"]
NEO4J_PASSWORD = cfg["neo4j"]["password"]

ollama.api_url = OLLAMA_API_URL
graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Streamlit UI 설정
st.set_page_config(layout="wide", page_title="철도 Agent")
st.title("철도 Agent")

# 지도에 표시할 역 데이터 가져오기
stations = graph.run("""
    MATCH (s:Station)
    WHERE s.lat IS NOT NULL AND s.lon IS NOT NULL
    RETURN s.name AS name, s.lat AS lat, s.lon AS lon
""").data()

# 지도 초기화 (서울을 중심으로)
m = folium.Map(location=[37.5665, 126.9780], zoom_start=7)
for s in stations:
    folium.Marker(
        location=[s["lat"], s["lon"]],
        popup=s["name"],
        icon=folium.Icon(color="blue", icon="train", prefix="fa")
    ).add_to(m)

st_folium(m, width=750, height=500)

# 사이드바 UI: 사용자 입력 및 처리
st.sidebar.header("철도 관련 질문")
user_question = st.sidebar.text_input("예: 서울에서 부산까지 KTX 연결되어 있어?")

if user_question:
    total_start = time.perf_counter()
    
    try:
        # 질문 의도(Intent) 파싱
        parse_start = time.perf_counter()
        parsed = parse_intent(user_question, PARSER_MODEL)
        parse_elapsed = time.perf_counter() - parse_start

        st.sidebar.subheader("🔍 디버그: LLM 파싱 결과")
        st.sidebar.json(parsed)

        # 질문에서 필수 정보 누락 확인
        if parsed.get("missing_info"):
            st.sidebar.warning(
                f"추가 정보가 필요합니다: {', '.join(parsed['missing_info'])}"
            )

        # DB 조회, 의도(Intent)별 로직 분기
        context = {"intent": parsed.get("intent")}
        db_start = time.perf_counter()
        
        if parsed.get("intent") == "CHECK_CONNECTIVITY": # 연결 여부 확인
            context.update({
                "from_station": parsed.get("from_station"),
                "to_station": parsed.get("to_station"),
                "is_connected": check_connectivity(
                    graph,
                    parsed.get("from_station"),
                    parsed.get("to_station")
                )
            })
        
        elif parsed.get("intent") == "COUNT_TRANSFERS": # 환승 횟수 확인
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

        # 자연어 답변 생성
        answer_start = time.perf_counter()
        answer = generate_answer(context, ANSWER_MODEL)
        answer_elapsed = time.perf_counter() - answer_start

        st.sidebar.markdown("### 답변")
        st.sidebar.write(answer)

        # 처리 시간 지표
        total_elapsed = time.perf_counter() - total_start
        st.sidebar.divider()
        st.sidebar.info(f"총 소요 시간: {total_elapsed:.2f}초")
        st.sidebar.caption(f" • 파싱: {parse_elapsed:.2f}초 ({PARSER_MODEL})")
        st.sidebar.caption(f" • DB 조회: {db_elapsed:.2f}초")
        st.sidebar.caption(f" • 답변 생성: {answer_elapsed:.2f}초 ({ANSWER_MODEL})")

    except Exception as e:
        total_elapsed = time.perf_counter() - total_start
        st.sidebar.error("처리 중 오류가 발생했습니다.")
        st.sidebar.code(str(e))
        st.sidebar.info(f"총 경과 시간: {total_elapsed:.2f}초")