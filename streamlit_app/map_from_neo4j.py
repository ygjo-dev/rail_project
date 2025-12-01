import streamlit as st
from py2neo import Graph
import folium
from streamlit_folium import st_folium
from transformers import pipeline

generator = pipeline("text-generation", model="/root/models/gpt4all-lora-quantized.bin", device=-1)


def ask_llm(prompt, max_tokens=200):
    result = generator(prompt, max_new_tokens=max_tokens)
    return result[0]["generated_text"]

# -------------------------------
# 2️⃣ Streamlit 페이지 설정
# -------------------------------
st.set_page_config(layout="wide")
st.title("Neo4j 지도 + 로컬 LLM 챗봇 (GPT4All HuggingFace)")

# -------------------------------
# 3️⃣ Neo4j 연결
# -------------------------------
graph = Graph("bolt://neo4j:7687", auth=("neo4j", "password"))

# -------------------------------
# 4️⃣ 지도 생성
# -------------------------------
stations = graph.run("""
    MATCH (s:Station)
    RETURN s.name AS name, s.code AS code, s.lat AS lat, s.lon AS lon, s.isKTX AS isKTX
""").data()

m = folium.Map(location=[37.5665, 126.9780], zoom_start=7)
for station in stations:
    popup_text = f"""
    <b>{station['name']}</b><br>
    코드: {station['code']}<br>
    KTX 여부: {'O' if station['isKTX'] else 'X'}
    """
    folium.Marker(
        location=[station['lat'], station['lon']],
        popup=popup_text,
        icon=folium.Icon(color='blue', icon='train', prefix='fa')
    ).add_to(m)

st_folium(m, width=700, height=500)

# -------------------------------
# 4️⃣ LLM 챗봇
# -------------------------------
st.sidebar.header("LLM 챗봇 질문")
user_question = st.sidebar.text_input("질문을 입력하세요:", "")

if user_question:
    # 1️⃣ 질문 → Cypher 쿼리 생성
    prompt_cypher = f"""
Neo4j 그래프 DB에는 철도역 Station 노드가 있습니다.
사용자의 질문을 바탕으로 Cypher 쿼리를 만들어주세요.
질문: "{user_question}"
"""
    cypher_query = ask_llm(prompt_cypher)

    # 2️⃣ Neo4j 실행
    try:
        result = graph.run(cypher_query).data()
    except Exception as e:
        result = f"쿼리 실행 중 오류: {e}"

    # 3️⃣ Cypher 결과 → 자연스러운 답변 생성
    prompt_answer = f"""
사용자 질문: "{user_question}"
Cypher 결과: {result}
위 정보를 바탕으로 자연스럽게 답변을 만들어 주세요.
"""
    answer = ask_llm(prompt_answer)

    st.sidebar.text_area("💬 답변", value=answer, height=150)
