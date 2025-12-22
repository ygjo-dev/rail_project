import os
import json
import time
import streamlit as st
from py2neo import Graph
import folium
from streamlit_folium import st_folium
import ollama

# -----------------------------
# 환경 변수 및 설정 파일 로드
# -----------------------------
CONFIG_FILE = os.environ.get("CONFIG_FILE", "../config/config.json")
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
# Streamlit UI 설정
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
user_question = st.sidebar.text_input("예: 경부고속선으로 광명에서 서울 가?")

if user_question:
    start_time = time.perf_counter()

    try:
        # 1. LLM: 역 이름만 추출
        prompt_extract = f"""
질문에서 출발역과 도착역 이름만 추출하라.

규칙:
- 역 이름만 출력
- 괄호 포함 허용
- 한국어 그대로
- JSON 형식만 출력

형식:
{{"from": "...", "to": "..."}}

질문:
"{user_question}"
"""

        extract_resp = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": "역 이름만 추출한다."},
                {"role": "user", "content": prompt_extract}
            ]
        )

        extracted = extract_resp["message"]["content"]
        st.sidebar.subheader("LLM 추출 결과 (Debug.1)")
        st.sidebar.code(extracted, language="json")

        data = eval(extracted)
        start_kw = data["from"]
        end_kw = data["to"]

        # 2. Cypher 쿼리 실행
        cypher_query = f"""
        MATCH (a:Station)-[:CONNECTS]->(b:Station)
        WHERE a.name CONTAINS "{start_kw}"
          AND b.name CONTAINS "{end_kw}"
        RETURN count(*) > 0 AS is_connected
        """
        st.sidebar.subheader("실행 Cypher (Debug.2)")
        st.sidebar.code(cypher_query, language="cypher")

        result = graph.run(cypher_query).data()
        is_connected = result and result[0]["is_connected"]

        elapsed = time.perf_counter() - start_time

        # 3. 결과 출력
        if is_connected:
            st.sidebar.success("두 역은 연결되어 있습니다.")
        else:
            st.sidebar.warning("두 역은 연결되어 있지 않습니다.")

        st.sidebar.info(f"처리 시간: {elapsed:.2f}초")

    except Exception as e:
        elapsed = time.perf_counter() - start_time
        st.sidebar.error("오류 발생")
        st.sidebar.code(str(e))
        st.sidebar.info(f"처리 시간: {elapsed:.2f}초")
